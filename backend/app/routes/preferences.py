from flask import Blueprint, request, jsonify, g
from app.database.db import get_db_session
from app.models.job import JobPreference
from app.utils.security import jwt_required

preferences_bp = Blueprint("preferences", __name__)

VALID_REMOTE_PREFS = {"remote", "hybrid", "onsite", "any"}
VALID_EXP_LEVELS = {"entry", "mid", "senior", "any"}

def normalize_to_string(value) -> str:
    """Normalize a string or list of strings into a comma-separated string."""
    if isinstance(value, list):
        return ", ".join([str(item).strip() for item in value if str(item).strip()])
    return str(value or "").strip()

@preferences_bp.route("", methods=["GET"])
@jwt_required
def get_preferences():
    """Retrieve job preferences for the current authenticated user."""
    session = get_db_session()
    user_id = g.current_user.id

    prefs = session.query(JobPreference).filter(JobPreference.user_id == user_id).first()
    if not prefs:
        prefs = JobPreference(
            user_id=user_id,
            desired_titles="Software Engineer, Full Stack Developer, Frontend Developer, Backend Developer",
            desired_locations="Remote, Bangalore, Hyderabad, Pune, Mumbai, Delhi NCR",
            remote_preference="any",
            employment_types="full-time, internship",
            experience_level="entry",
            fresh_graduate_friendly=True,
        )
        session.add(prefs)
        session.commit()

    return jsonify({
        "preferences": prefs.to_dict()
    }), 200

@preferences_bp.route("", methods=["PUT"])
@jwt_required
def update_preferences():
    """Update job search preferences and filters."""
    session = get_db_session()
    user_id = g.current_user.id
    data = request.get_json() or {}

    prefs = session.query(JobPreference).filter(JobPreference.user_id == user_id).first()
    if not prefs:
        prefs = JobPreference(user_id=user_id)
        session.add(prefs)

    # Update fields
    if "desired_titles" in data:
        prefs.desired_titles = normalize_to_string(data["desired_titles"])

    if "desired_locations" in data:
        prefs.desired_locations = normalize_to_string(data["desired_locations"])

    if "remote_preference" in data:
        rem_pref = str(data["remote_preference"]).lower().strip()
        prefs.remote_preference = rem_pref if rem_pref in VALID_REMOTE_PREFS else "any"

    if "min_salary" in data:
        try:
            prefs.min_salary = max(0, int(data["min_salary"]))
        except (ValueError, TypeError):
            prefs.min_salary = 0

    if "employment_types" in data:
        prefs.employment_types = normalize_to_string(data["employment_types"])

    if "experience_level" in data:
        exp_lvl = str(data["experience_level"]).lower().strip()
        prefs.experience_level = exp_lvl if exp_lvl in VALID_EXP_LEVELS else "entry"

    if "fresh_graduate_friendly" in data:
        prefs.fresh_graduate_friendly = bool(data["fresh_graduate_friendly"])

    if "skills_filter" in data:
        prefs.skills_filter = normalize_to_string(data["skills_filter"])

    if "companies_whitelist" in data:
        prefs.companies_whitelist = normalize_to_string(data["companies_whitelist"])

    if "companies_blacklist" in data:
        prefs.companies_blacklist = normalize_to_string(data["companies_blacklist"])

    session.commit()

    return jsonify({
        "message": "Job preferences updated successfully",
        "preferences": prefs.to_dict()
    }), 200
