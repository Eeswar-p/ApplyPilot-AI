import time
import threading
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.database.db import get_db_context
from app.models.user import User
from app.models.profile import UserProfile
from app.models.resume import Resume
from app.models.application import Application
from app.models.job import Job
from app.models.automation import AutomationSession, AutomationSetting, AutomationLog
from app.automation.browser import BrowserManager
from app.automation.navigator import JobNavigator
from app.automation.form_scanner import FormScanner
from app.automation.filler import FormFiller
from app.automation.session_manager import AutomationSessionManager
from app.question_handler.matcher import ScreeningQuestionHandler

class ApplicationEngine:
    """End-to-end autonomous job application engine.
    Orchestrates browser automation, profile mapping, form scanning,
    resume uploading, factual screening question responses, and submission verification.
    """

    _active_threads: Dict[int, threading.Thread] = {}
    _stop_flags: Dict[int, bool] = {}
    _pause_flags: Dict[int, bool] = {}

    @classmethod
    def is_running(cls, user_id: int) -> bool:
        t = cls._active_threads.get(user_id)
        return t is not None and t.is_alive()

    @classmethod
    def request_stop(cls, user_id: int):
        cls._stop_flags[user_id] = True

    @classmethod
    def request_pause(cls, user_id: int):
        cls._pause_flags[user_id] = True

    @classmethod
    def request_resume(cls, user_id: int):
        cls._pause_flags[user_id] = False

    @classmethod
    def start_background_session(cls, user_id: int, headless: bool = True, max_jobs: Optional[int] = None) -> bool:
        """Starts automation loop in a background thread."""
        if cls.is_running(user_id):
            return False

        cls._stop_flags[user_id] = False
        cls._pause_flags[user_id] = False

        thread = threading.Thread(
            target=cls._run_worker,
            args=(user_id, headless, max_jobs),
            daemon=True,
            name=f"AutomationWorker-User-{user_id}"
        )
        cls._active_threads[user_id] = thread
        thread.start()
        return True

    @classmethod
    def _run_worker(cls, user_id: int, headless: bool, max_jobs: Optional[int]):
        """Background thread worker with standalone database session context."""
        with get_db_context() as db:
            session_mgr = AutomationSessionManager(db)
            session = session_mgr.create_or_resume_session(user_id)

            engine = cls(db, user_id, session.id)
            engine.run(headless=headless, max_jobs=max_jobs)

    def __init__(self, db: Session, user_id: int, session_id: int):
        self.db = db
        self.user_id = user_id
        self.session_id = session_id
        self.session_mgr = AutomationSessionManager(db)

    def _should_stop(self) -> bool:
        return self._stop_flags.get(self.user_id, False)

    def _is_paused(self) -> bool:
        return self._pause_flags.get(self.user_id, False)

    def run(self, headless: bool = True, max_jobs: Optional[int] = None):
        """Execute the automation pipeline for candidate applications."""
        user = self.db.query(User).filter(User.id == self.user_id).first()
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == self.user_id).first()
        primary_resume = self.db.query(Resume).filter(
            Resume.user_id == self.user_id,
            Resume.is_primary == True
        ).first()

        # Load automation settings
        setting = self.db.query(AutomationSetting).filter(AutomationSetting.user_id == self.user_id).first()
        if not setting:
            setting = AutomationSetting(user_id=self.user_id)
            self.db.add(setting)
            self.db.commit()

        limit = max_jobs or setting.max_applications_per_session or 15
        delay = setting.application_delay_seconds or 5
        require_approval = setting.require_approval

        if not primary_resume:
            self.session_mgr.log(
                self.session_id, self.user_id, "ERROR",
                "Automation halted: No primary resume found. Please upload a resume first."
            )
            sess = self.db.query(AutomationSession).filter(AutomationSession.id == self.session_id).first()
            if sess:
                sess.status = "failed"
                sess.error_message = "No primary resume found"
                sess.ended_at = datetime.now(timezone.utc)
                self.db.commit()
            return

        # Fetch eligible applications
        applications = self.db.query(Application).filter(
            Application.user_id == self.user_id,
            Application.status.in_(["Eligible", "Discovered", "Pending Approval"])
        ).order_by(Application.match_score.desc()).limit(limit).all()

        sess = self.db.query(AutomationSession).filter(AutomationSession.id == self.session_id).first()
        if sess:
            sess.total_discovered = len(applications)
            self.db.commit()

        if not applications:
            self.session_mgr.log(
                self.session_id, self.user_id, "WARNING",
                "No eligible job applications queued. Discover jobs and check eligibility first."
            )
            self.session_mgr.complete_session(self.session_id)
            return

        self.session_mgr.log(
            self.session_id, self.user_id, "INFO",
            f"Found {len(applications)} candidate jobs queued for automated application processing."
        )

        # Launch browser context
        browser_mgr = BrowserManager(user_id=self.user_id)
        question_handler = ScreeningQuestionHandler(self.db, self.user_id)

        try:
            browser_mgr.launch_context(headless=headless)
            page = browser_mgr.new_page()

            navigator = JobNavigator(page)
            scanner = FormScanner(page)
            filler = FormFiller(page, user, profile, primary_resume, question_handler)

            for app in applications:
                # Check stop request
                if self._should_stop():
                    self.session_mgr.log(self.session_id, self.user_id, "WARNING", "Stop requested. Halting automation.")
                    break

                # Handle pause
                while self._is_paused():
                    time.sleep(1)
                    if self._should_stop():
                        break

                if self._should_stop():
                    break

                job = app.job
                if not job or not job.job_url:
                    continue

                # Update session current job
                if sess:
                    sess.current_job_title = job.title
                    sess.current_job_company = job.company
                    self.db.commit()

                app.status = "Applying"
                self.db.commit()

                self.session_mgr.log(
                    self.session_id, self.user_id, "INFO",
                    f"Navigating to {job.title} at {job.company} ({job.source})..."
                )

                # 1. Navigate
                nav_success, nav_err = navigator.navigate_safely(job.job_url)
                if not nav_success:
                    app.status = "Failed"
                    app.failure_reason = f"Navigation error: {nav_err}"
                    if sess:
                        sess.total_failed += 1
                        sess.total_processed += 1
                    self.session_mgr.log(self.session_id, self.user_id, "ERROR", f"Failed to load job page: {nav_err}")
                    self.db.commit()
                    continue

                # 2. Check and click Apply button
                apply_clicked, apply_err = navigator.find_and_click_apply()
                self.session_mgr.log(
                    self.session_id, self.user_id, "INFO",
                    "Application entry detected. Scanning application form fields..."
                )

                # 3. Scan fields
                fields = scanner.scan_form_fields()

                # 4. Fill form
                fill_res = filler.fill_all_fields(fields)
                for log_msg in fill_res.get("action_log", []):
                    self.session_mgr.log(self.session_id, self.user_id, "INFO", log_msg)

                # 5. Check if approval required
                if require_approval:
                    app.status = "Pending Approval"
                    app.automation_result = f"Filled {fill_res['filled_count']} fields. Awaiting candidate sign-off."
                    app.resume_id = primary_resume.id
                    if sess:
                        sess.total_processed += 1
                    self.session_mgr.log(
                        self.session_id, self.user_id, "INFO",
                        f"Application for {job.company} held for manual candidate approval."
                    )
                    self.db.commit()
                    time.sleep(delay)
                    continue

                # 6. Submit application
                sub_res = filler.submit_application(require_approval=False)
                if sub_res.get("submitted"):
                    app.status = "Applied"
                    app.applied_at = datetime.now(timezone.utc)
                    app.resume_id = primary_resume.id
                    app.automation_result = sub_res.get("message", "Application submitted successfully.")
                    if sess:
                        sess.total_successful += 1
                        sess.total_processed += 1
                    self.session_mgr.log(
                        self.session_id, self.user_id, "SUCCESS",
                        f"Successfully submitted application for {job.title} at {job.company}!"
                    )
                else:
                    app.status = "Failed"
                    app.failure_reason = sub_res.get("message", "Application submission failed.")
                    if sess:
                        sess.total_failed += 1
                        sess.total_processed += 1
                    self.session_mgr.log(
                        self.session_id, self.user_id, "WARNING",
                        f"Submission failed for {job.company}: {app.failure_reason}"
                    )

                self.db.commit()

                # Pacing delay between applications
                time.sleep(delay)

            # Finalize session
            self.session_mgr.complete_session(self.session_id)

        except Exception as e:
            self.session_mgr.log(
                self.session_id, self.user_id, "ERROR",
                f"Automation session encountered unexpected exception: {str(e)}"
            )
            if sess:
                sess.status = "failed"
                sess.error_message = str(e)
                sess.ended_at = datetime.now(timezone.utc)
                self.db.commit()
        finally:
            browser_mgr.close()
            # Clear running state
            self._active_threads.pop(self.user_id, None)
            self._stop_flags.pop(self.user_id, None)
            self._pause_flags.pop(self.user_id, None)
