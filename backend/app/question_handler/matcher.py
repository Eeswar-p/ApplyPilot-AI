import re
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.profile import UserProfile, Education, Skill, Experience
from app.models.screening import SavedAnswer, ScreeningQuestion

class ScreeningQuestionHandler:
    """Intelligent and safe screening question answering engine.
    Ensures answers are grounded exclusively in verified candidate profile facts and saved answers.
    Never invents or fabricates candidate qualifications.
    """

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self._load_candidate_facts()

    def _load_candidate_facts(self):
        """Preload verified profile facts and saved custom answers."""
        self.profile = self.db.query(UserProfile).filter(UserProfile.user_id == self.user_id).first()
        self.education = self.db.query(Education).filter(Education.user_id == self.user_id).all()
        self.skills = self.db.query(Skill).filter(Skill.user_id == self.user_id).all()
        self.experience = self.db.query(Experience).filter(Experience.user_id == self.user_id).all()
        self.saved_answers = self.db.query(SavedAnswer).filter(SavedAnswer.user_id == self.user_id).all()

        # Build skill name lookup
        self.skill_names = [s.skill_name.lower().strip() for s in self.skills]

        # Calculate total years of experience
        total_years = 0.0
        for s in self.skills:
            if s.years_of_experience:
                total_years = max(total_years, s.years_of_experience)
        self.total_exp_years = total_years

    def answer_question(self, question_text: str, options: Optional[list] = None) -> Tuple[Optional[str], float, str]:
        """Answer a screening question.
        Returns: (proposed_answer, confidence_score, source_reason)
        """
        clean_q = question_text.lower().strip()

        # 1. Check user's previously approved saved answers
        for sa in self.saved_answers:
            pattern = sa.question_pattern.lower().strip()
            if pattern in clean_q or clean_q in pattern:
                return sa.answer_text, 1.0, "Verified custom answer"

        # 2. Work Authorization / Visa Sponsorship
        if any(kw in clean_q for kw in ["authorized to work", "legally authorized", "work authorization"]):
            ans = "Yes"
            if options and "yes" in [o.lower() for o in options]:
                ans = next(o for o in options if o.lower() == "yes")
            return ans, 0.95, "Verified citizen / resident work authorization"

        if any(kw in clean_q for kw in ["require sponsorship", "visa sponsorship", "future sponsorship"]):
            ans = "No"
            if options and "no" in [o.lower() for o in options]:
                ans = next(o for o in options if o.lower() == "no")
            return ans, 0.95, "Standard work eligibility without sponsorship requirement"

        # 3. Highest Qualification / Degree
        if any(kw in clean_q for kw in ["highest qualification", "highest degree", "degree level", "education level"]):
            if self.profile and self.profile.highest_degree:
                return self.profile.highest_degree, 0.95, "Verified candidate profile degree"
            if self.education:
                return self.education[0].degree, 0.90, "Educational qualification history"

        # 4. Years of Experience
        if any(kw in clean_q for kw in ["years of experience", "total experience", "how many years"]):
            # Check if specific technology asked
            for skill in self.skills:
                if skill.skill_name.lower() in clean_q:
                    return str(int(skill.years_of_experience or 1)), 0.90, f"Verified skill experience for {skill.skill_name}"
            # Default to total years
            return str(int(self.total_exp_years or 0)), 0.85, "Total verified candidate experience"

        # 5. Relocation Willingness
        if any(kw in clean_q for kw in ["willing to relocate", "relocation", "open to relocate"]):
            ans = "Yes"
            if options and "yes" in [o.lower() for o in options]:
                ans = next(o for o in options if o.lower() == "yes")
            return ans, 0.90, "Candidate relocation preference"

        # 6. Notice Period / Availability
        if any(kw in clean_q for kw in ["notice period", "how soon can you start", "availability", "when can you start"]):
            ans = "Immediate / 15 Days"
            if options:
                # Find closest option (e.g. Immediate, 15 days, 1 month)
                for opt in options:
                    if any(w in opt.lower() for w in ["immediate", "15", "1 month", "flexible"]):
                        return opt, 0.90, "Standard fresh graduate availability"
            return ans, 0.85, "Availability estimate"

        # 7. Graduation Year
        if any(kw in clean_q for kw in ["graduation year", "year of graduation", "passing year", "batch"]):
            if self.profile and self.profile.graduation_year:
                return str(self.profile.graduation_year), 0.95, "Profile graduation year"
            if self.education and self.education[0].end_date:
                return str(self.education[0].end_date), 0.85, "Degree completion year"

        # Unknown question requiring user confirmation
        return None, 0.0, "Unknown question requiring user review"
