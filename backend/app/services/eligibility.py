import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.job import Job, JobPreference
from app.models.profile import UserProfile, Education, Skill, Experience
from app.models.application import Application

TECH_KEYWORDS = [
    "python", "react", "javascript", "typescript", "java", "c++", "c#", "go", "golang",
    "node.js", "nodejs", "flask", "fastapi", "django", "sql", "postgresql", "mysql",
    "mongodb", "redis", "docker", "kubernetes", "aws", "azure", "git", "html", "css",
    "tailwind", "redux", "next.js", "rest", "graphql", "linux", "machine learning",
    "data structures", "algorithms", "oop", "pytorch", "tensorflow"
]

class EligibilityEngine:
    """Evaluates candidate profile against job postings to calculate match scores and generate factual explanations."""

    def __init__(self, session: Session):
        self.session = session

    def evaluate_job_for_user(self, user_id: int, job_id: int) -> Dict[str, Any]:
        """Compute match score and reasoning for a single job against candidate profile."""
        job = self.session.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job with ID {job_id} not found")

        # Load candidate profile
        profile = self.session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        skills = self.session.query(Skill).filter(Skill.user_id == user_id).all()
        education = self.session.query(Education).filter(Education.user_id == user_id).all()
        experience = self.session.query(Experience).filter(Experience.user_id == user_id).all()
        prefs = self.session.query(JobPreference).filter(JobPreference.user_id == user_id).first()

        candidate_skills = {s.skill_name.lower().strip() for s in skills}
        job_full_text = f"{job.title} {job.description} {job.requirements}".lower()

        # 1. Skill Matching (Weight: 40%)
        # Identify keywords required in the job
        required_skills = [tech for tech in TECH_KEYWORDS if tech in job_full_text]
        if not required_skills:
            # Fallback if no specific tech keywords identified
            required_skills = ["computer science", "problem-solving"]

        matched_skills = [tech for tech in required_skills if any(tech in cs for cs in candidate_skills)]
        missing_skills = [tech for tech in required_skills if tech not in matched_skills]

        skill_ratio = len(matched_skills) / len(required_skills) if required_skills else 1.0
        skill_score = min(40.0, skill_ratio * 40.0)

        # 2. Education & Degree Match (Weight: 25%)
        edu_score = 0.0
        degree_matched = False
        highest_degree = (profile.highest_degree if profile else "").lower()
        candidate_degrees = [e.degree.lower() for e in education]
        if highest_degree:
            candidate_degrees.append(highest_degree)

        req_lower = job.requirements.lower()
        if any(deg in req_lower for deg in ["b.tech", "b.e", "bachelor", "degree", "graduate", "m.tech", "mca"]):
            if any(any(d in cd for d in ["b.tech", "b.e", "bachelor", "m.tech", "mca", "b.s."]) for cd in candidate_degrees):
                edu_score = 25.0
                degree_matched = True
            else:
                edu_score = 15.0 # Partial credit for listed education
        else:
            edu_score = 25.0 # No strict degree requirement stated
            degree_matched = True

        # 3. Experience & Fresh Graduate Alignment (Weight: 20%)
        exp_score = 20.0
        job_exp = job.experience_required.lower()
        fresh_grad_mode = prefs.fresh_graduate_friendly if prefs else True

        if "0-1" in job_exp or "0-2" in job_exp or "intern" in job.employment_type.lower():
            exp_score = 20.0
        elif "3+" in job_exp or "5+" in job_exp:
            exp_score = 5.0 if not fresh_grad_mode else 0.0
        else:
            exp_score = 15.0

        # 4. Location & Preference Alignment (Weight: 15%)
        loc_score = 0.0
        pref_locations = [l.strip().lower() for l in (prefs.desired_locations if prefs else "").split(",") if l.strip()]
        job_loc = job.location.lower()

        if "remote" in job_loc or any(loc in job_loc for loc in pref_locations):
            loc_score = 15.0
        else:
            loc_score = 8.0 # Partial credit if willing to relocate

        # Total Score Calculation (0 to 100)
        total_score = round(skill_score + edu_score + exp_score + loc_score)
        total_score = max(0, min(100, total_score))

        # Classification
        if total_score >= 75:
            category = "Highly Relevant"
            status = "Eligible"
        elif total_score >= 50:
            category = "Moderately Relevant"
            status = "Eligible"
        else:
            category = "Not Relevant"
            status = "Skipped"

        # Factual, non-hallucinated reasoning
        reason_parts = []
        if matched_skills:
            reason_parts.append(f"Matched {len(matched_skills)} key skills: {', '.join([s.title() for s in matched_skills[:5]])}.")
        if missing_skills:
            reason_parts.append(f"Target qualifications to develop: {', '.join([s.title() for s in missing_skills[:4]])}.")
        if degree_matched:
            reason_parts.append("Educational credentials satisfy the requirement.")
        if "0-2" in job_exp or "0-1" in job_exp:
            reason_parts.append("Experience bracket is ideally aligned for fresh graduates.")

        explanation = " ".join(reason_parts) if reason_parts else "General alignment with specified preferences."

        # Update or create Application record
        application = self.session.query(Application).filter(
            Application.user_id == user_id,
            Application.job_id == job_id
        ).first()

        if not application:
            application = Application(
                user_id=user_id,
                job_id=job_id,
                status=status,
                match_score=total_score,
                relevance_category=category,
                relevance_reason=explanation,
            )
            self.session.add(application)
        else:
            application.match_score = total_score
            application.relevance_category = category
            application.relevance_reason = explanation
            # Only update status if currently Discovered, otherwise preserve user's workflow
            if application.status == "Discovered":
                application.status = status

        self.session.commit()

        return {
            "job_id": job.id,
            "job_title": job.title,
            "company": job.company,
            "match_score": total_score,
            "relevance_category": category,
            "status": application.status,
            "matched_skills": [s.title() for s in matched_skills],
            "missing_skills": [s.title() for s in missing_skills],
            "relevance_reason": explanation,
            "score_breakdown": {
                "skills": round(skill_score),
                "education": round(edu_score),
                "experience": round(exp_score),
                "location": round(loc_score),
            }
        }

    def evaluate_all_discovered_for_user(self, user_id: int) -> Dict[str, Any]:
        """Evaluate all jobs discovered for a user."""
        apps = self.session.query(Application).filter(
            Application.user_id == user_id
        ).all()

        results = []
        eligible_count = 0
        skipped_count = 0

        for app in apps:
            res = self.evaluate_job_for_user(user_id, app.job_id)
            results.append(res)
            if res["status"] == "Eligible":
                eligible_count += 1
            elif res["status"] == "Skipped":
                skipped_count += 1

        return {
            "total_evaluated": len(results),
            "eligible_count": eligible_count,
            "skipped_count": skipped_count,
            "evaluations": results,
        }
