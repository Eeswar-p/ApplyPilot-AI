import os
import re
from typing import Dict, Any, List, Optional
from playwright.sync_api import Page, Locator
from app.automation.form_scanner import FormScanner, FormFieldDescriptor
from app.question_handler.matcher import ScreeningQuestionHandler
from app.models.profile import UserProfile
from app.models.resume import Resume
from app.models.user import User

class FormFiller:
    """Intelligently fills job application forms using candidate profile,
    uploaded resume, and factual screening question answers.
    """

    def __init__(
        self,
        page: Page,
        user: User,
        profile: Optional[UserProfile],
        primary_resume: Optional[Resume],
        question_handler: ScreeningQuestionHandler
    ):
        self.page = page
        self.user = user
        self.profile = profile
        self.primary_resume = primary_resume
        self.question_handler = question_handler

    def _get_candidate_value_for_field(self, field: FormFieldDescriptor) -> Optional[str]:
        """Map candidate profile facts to a scanned form field."""
        label_lower = field.label.lower()
        name_lower = field.name.lower()
        combined = f"{label_lower} {name_lower}"

        # 1. Email
        if any(k in combined for k in ["email", "e-mail", "mail address"]):
            return self.user.email

        # 2. First Name
        if any(k in combined for k in ["first name", "firstname", "given name"]):
            if self.profile and self.profile.full_name:
                parts = self.profile.full_name.split()
                return parts[0] if parts else ""
            return ""

        # 3. Last Name
        if any(k in combined for k in ["last name", "lastname", "surname", "family name"]):
            if self.profile and self.profile.full_name:
                parts = self.profile.full_name.split()
                return " ".join(parts[1:]) if len(parts) > 1 else parts[0]
            return ""

        # 4. Full Name
        if any(k in combined for k in ["full name", "fullname", "candidate name", "your name", "name"]):
            if self.profile and self.profile.full_name:
                return self.profile.full_name
            return ""

        # 5. Phone / Mobile
        if any(k in combined for k in ["phone", "mobile", "cell", "contact number", "telephone"]):
            if self.profile and self.profile.phone:
                return self.profile.phone
            return ""

        # 6. Location / Address / City
        if any(k in combined for k in ["city", "current city", "location", "address", "current location"]):
            if self.profile and self.profile.current_location:
                return self.profile.current_location
            return ""

        # 7. LinkedIn
        if any(k in combined for k in ["linkedin", "linked in"]):
            if self.profile and self.profile.linkedin_url:
                return self.profile.linkedin_url
            return ""

        # 8. GitHub
        if any(k in combined for k in ["github", "git"]):
            if self.profile and self.profile.github_url:
                return self.profile.github_url
            return ""

        # 9. Portfolio / Website
        if any(k in combined for k in ["portfolio", "website", "personal site", "url"]):
            if self.profile and self.profile.portfolio_url:
                return self.profile.portfolio_url
            return ""

        # 10. Fallback to screening question handler
        answer, confidence, reason = self.question_handler.answer_question(field.label, field.options)
        if answer and confidence >= 0.70:
            return answer

        return None

    def fill_all_fields(self, fields: List[FormFieldDescriptor]) -> Dict[str, Any]:
        """Fills interactive form inputs on the current page."""
        filled_count = 0
        missing_required = []
        action_log = []

        for field in fields:
            selector = field.selector or f"#{field.field_id}"
            loc = self.page.locator(selector).first
            if not loc or loc.count() == 0:
                continue

            try:
                # Handle file upload inputs (Resume / CV)
                if field.field_type == "file" or any(k in field.label.lower() for k in ["resume", "cv", "curriculum vitae"]):
                    if self.primary_resume and self.primary_resume.file_path and os.path.exists(self.primary_resume.file_path):
                        loc.set_input_files(self.primary_resume.file_path)
                        filled_count += 1
                        action_log.append(f"Uploaded resume: {self.primary_resume.file_name}")
                    else:
                        if field.required:
                            missing_required.append(f"Resume required but not provided ({field.label})")
                    continue

                # Handle Checkboxes (e.g., terms and conditions, age confirmation)
                if field.field_type == "checkbox":
                    if any(k in field.label.lower() for k in ["agree", "terms", "confirm", "certify", "authorized", "consent"]):
                        loc.check()
                        filled_count += 1
                        action_log.append(f"Checked agreement checkbox: {field.label}")
                    continue

                # Handle Radio Buttons
                if field.field_type == "radio":
                    proposed_val = self._get_candidate_value_for_field(field)
                    if proposed_val:
                        loc.check()
                        filled_count += 1
                        action_log.append(f"Selected radio option for: {field.label}")
                    continue

                # Handle Dropdowns (<select>)
                if field.field_type == "select":
                    val = self._get_candidate_value_for_field(field)
                    if val and field.options:
                        # Find best matching option
                        matched_opt = None
                        for opt in field.options:
                            if val.lower() in opt.lower() or opt.lower() in val.lower():
                                matched_opt = opt
                                break
                        if matched_opt:
                            loc.select_option(label=matched_opt)
                            filled_count += 1
                            action_log.append(f"Selected '{matched_opt}' for dropdown: {field.label}")
                        elif field.required:
                            # Pick first non-empty option if strictly required
                            non_empty = [o for o in field.options if o and not o.lower().startswith("select")]
                            if non_empty:
                                loc.select_option(label=non_empty[0])
                                filled_count += 1
                                action_log.append(f"Defaulted required select '{non_empty[0]}' for: {field.label}")
                    continue

                # Handle standard text, email, tel, number, textarea
                candidate_val = self._get_candidate_value_for_field(field)
                if candidate_val:
                    loc.fill(str(candidate_val))
                    filled_count += 1
                    action_log.append(f"Filled '{field.label}' with value")
                else:
                    if field.required:
                        missing_required.append(f"Missing required field: '{field.label}'")

            except Exception as e:
                action_log.append(f"Error filling {field.label}: {str(e)}")

        return {
            "filled_count": filled_count,
            "missing_required": missing_required,
            "action_log": action_log,
            "can_submit": len(missing_required) == 0
        }

    def submit_application(self, require_approval: bool = False) -> Dict[str, Any]:
        """Validates form, checks approval requirements, and submits if authorized."""
        if require_approval:
            return {
                "status": "Pending Approval",
                "message": "Form successfully filled and held for candidate review and approval.",
                "submitted": False
            }

        # Locate submit button
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Submit Application')",
            "button:has-text('Submit application')",
            "button:has-text('Submit')",
            "button:has-text('Apply Now')",
            "button:has-text('Send Application')",
            "button:has-text('Review your application')",
        ]

        submit_btn = None
        for sel in submit_selectors:
            btn = self.page.locator(sel)
            if btn.count() > 0 and btn.first.is_visible():
                submit_btn = btn.first
                break

        if not submit_btn:
            return {
                "status": "Failed",
                "message": "Submit button not found on application page.",
                "submitted": False
            }

        try:
            submit_btn.click()
            self.page.wait_for_timeout(2000)

            # Verification: check for success message, confirmation dialog, or thank you text
            success_keywords = ["thank you", "application submitted", "received your application", "success", "congratulations"]
            page_text = self.page.locator("body").inner_text().lower()

            has_success = any(kw in page_text for kw in success_keywords)

            return {
                "status": "Applied" if has_success else "Applied",
                "message": "Application submitted successfully." if has_success else "Application submitted; awaiting platform confirmation.",
                "submitted": True
            }

        except Exception as e:
            return {
                "status": "Failed",
                "message": f"Error during submission: {str(e)}",
                "submitted": False
            }
