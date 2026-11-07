from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.automation import AutomationSession, AutomationLog, AutomationSetting

class AutomationSessionManager:
    """Manages automation session lifecycles, real-time logging, and state transitions."""

    def __init__(self, db: Session):
        self.db = db

    def create_or_resume_session(self, user_id: int) -> AutomationSession:
        """Create a new automation session or resume an active one."""
        active = self.db.query(AutomationSession).filter(
            AutomationSession.user_id == user_id,
            AutomationSession.status.in_(["running", "paused"])
        ).first()

        if active:
            active.status = "running"
            self.log(active.id, user_id, "INFO", "Resumed automation session")
            self.db.commit()
            return active

        new_session = AutomationSession(
            user_id=user_id,
            status="running",
            started_at=datetime.now(timezone.utc),
            total_discovered=0,
            total_processed=0,
            total_successful=0,
            total_failed=0,
        )
        self.db.add(new_session)
        self.db.flush()

        self.log(new_session.id, user_id, "INFO", "Started new automated application session")
        self.db.commit()
        return new_session

    def log(self, session_id: Optional[int], user_id: int, level: str, message: str):
        """Append an entry to the automation log."""
        log_entry = AutomationLog(
            session_id=session_id,
            user_id=user_id,
            log_level=level.upper(),
            message=message,
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(log_entry)

    def pause_session(self, user_id: int) -> Optional[AutomationSession]:
        """Pause currently running session."""
        active = self.db.query(AutomationSession).filter(
            AutomationSession.user_id == user_id,
            AutomationSession.status == "running"
        ).first()
        if active:
            active.status = "paused"
            self.log(active.id, user_id, "WARNING", "Automation session paused by user")
            self.db.commit()
        return active

    def stop_session(self, user_id: int) -> Optional[AutomationSession]:
        """Stop and terminate currently active session."""
        active = self.db.query(AutomationSession).filter(
            AutomationSession.user_id == user_id,
            AutomationSession.status.in_(["running", "paused"])
        ).first()
        if active:
            active.status = "stopped"
            active.ended_at = datetime.now(timezone.utc)
            self.log(active.id, user_id, "INFO", "Automation session gracefully stopped")
            self.db.commit()
        return active

    def complete_session(self, session_id: int):
        """Mark session as completed."""
        session = self.db.query(AutomationSession).filter(AutomationSession.id == session_id).first()
        if session:
            session.status = "completed"
            session.ended_at = datetime.now(timezone.utc)
            self.log(session.id, session.user_id, "SUCCESS", f"Session completed. Success: {session.total_successful}, Failed: {session.total_failed}")
            self.db.commit()

    def get_latest_session(self, user_id: int) -> Optional[AutomationSession]:
        """Get the most recent automation session for a user."""
        return self.db.query(AutomationSession).filter(
            AutomationSession.user_id == user_id
        ).order_by(AutomationSession.id.desc()).first()

    def get_session_logs(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent timestamped logs for a user."""
        logs = self.db.query(AutomationLog).filter(
            AutomationLog.user_id == user_id
        ).order_by(AutomationLog.timestamp.desc()).limit(limit).all()
        return [log.to_dict() for log in reversed(logs)]
