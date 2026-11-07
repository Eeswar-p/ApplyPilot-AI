from flask import Blueprint, request, jsonify, g
from app.database.db import get_db_session
from app.models.profile import UserProfile, Education, Skill, Experience
from app.utils.security import jwt_required

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("", methods=["GET"])
@jwt_required
def get_profile():
    """Retrieve the complete profile, including education, skills, and experience."""
    session = get_db_session()
    user_id = g.current_user.id

    profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id, full_name=g.current_user.email.split("@")[0].capitalize())
        session.add(profile)
        session.commit()

    education_list = session.query(Education).filter(Education.user_id == user_id).order_by(Education.id.desc()).all()
    skills_list = session.query(Skill).filter(Skill.user_id == user_id).order_by(Skill.id.asc()).all()
    experience_list = session.query(Experience).filter(Experience.user_id == user_id).order_by(Experience.id.desc()).all()

    return jsonify({
        "profile": profile.to_dict(),
        "education": [e.to_dict() for e in education_list],
        "skills": [s.to_dict() for s in skills_list],
        "experience": [exp.to_dict() for exp in experience_list],
    }), 200

@profile_bp.route("", methods=["PUT"])
@jwt_required
def update_profile():
    """Update user personal and career details."""
    session = get_db_session()
    user_id = g.current_user.id
    data = request.get_json() or {}

    profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        session.add(profile)

    # Update personal fields
    allowed_fields = [
        "full_name", "phone", "address", "city", "state", "country",
        "postal_code", "linkedin_url", "github_url", "portfolio_url",
        "bio", "graduation_year", "highest_degree"
    ]
    for field in allowed_fields:
        if field in data:
            setattr(profile, field, data[field])

    session.commit()
    return jsonify({
        "message": "Profile updated successfully",
        "profile": profile.to_dict(),
    }), 200

# ==================== Education Endpoints ====================

@profile_bp.route("/education", methods=["POST"])
@jwt_required
def add_education():
    """Add a new educational qualification."""
    data = request.get_json() or {}
    institution = data.get("institution", "").strip()
    degree = data.get("degree", "").strip()

    if not institution or not degree:
        return jsonify({"error": "Institution and degree are required"}), 400

    session = get_db_session()
    edu = Education(
        user_id=g.current_user.id,
        institution=institution,
        degree=degree,
        field_of_study=data.get("field_of_study", "").strip(),
        start_date=data.get("start_date", "").strip(),
        end_date=data.get("end_date", "").strip(),
        gpa=data.get("gpa", "").strip(),
        is_current=bool(data.get("is_current", False)),
    )
    session.add(edu)
    session.commit()

    return jsonify({
        "message": "Education record added",
        "education": edu.to_dict(),
    }), 201

@profile_bp.route("/education/<int:edu_id>", methods=["PUT"])
@jwt_required
def update_education(edu_id: int):
    """Update an existing educational qualification."""
    session = get_db_session()
    edu = session.query(Education).filter(
        Education.id == edu_id,
        Education.user_id == g.current_user.id
    ).first()

    if not edu:
        return jsonify({"error": "Education record not found or access denied"}), 404

    data = request.get_json() or {}
    for field in ["institution", "degree", "field_of_study", "start_date", "end_date", "gpa", "is_current"]:
        if field in data:
            setattr(edu, field, data[field])

    session.commit()
    return jsonify({
        "message": "Education record updated",
        "education": edu.to_dict(),
    }), 200

@profile_bp.route("/education/<int:edu_id>", methods=["DELETE"])
@jwt_required
def delete_education(edu_id: int):
    """Delete an educational qualification."""
    session = get_db_session()
    edu = session.query(Education).filter(
        Education.id == edu_id,
        Education.user_id == g.current_user.id
    ).first()

    if not edu:
        return jsonify({"error": "Education record not found or access denied"}), 404

    session.delete(edu)
    session.commit()
    return jsonify({"message": "Education record deleted"}), 200

# ==================== Skills Endpoints ====================

@profile_bp.route("/skills", methods=["POST"])
@jwt_required
def add_skill():
    """Add a technical or professional skill."""
    data = request.get_json() or {}
    skill_name = data.get("skill_name", "").strip()

    if not skill_name:
        return jsonify({"error": "Skill name is required"}), 400

    session = get_db_session()
    skill = Skill(
        user_id=g.current_user.id,
        skill_name=skill_name,
        category=data.get("category", "Technical").strip(),
        proficiency_level=data.get("proficiency_level", "Intermediate").strip(),
        years_of_experience=float(data.get("years_of_experience", 0.0) or 0.0),
    )
    session.add(skill)
    session.commit()

    return jsonify({
        "message": "Skill added",
        "skill": skill.to_dict(),
    }), 201

@profile_bp.route("/skills/<int:skill_id>", methods=["PUT"])
@jwt_required
def update_skill(skill_id: int):
    """Update an existing skill."""
    session = get_db_session()
    skill = session.query(Skill).filter(
        Skill.id == skill_id,
        Skill.user_id == g.current_user.id
    ).first()

    if not skill:
        return jsonify({"error": "Skill not found or access denied"}), 404

    data = request.get_json() or {}
    if "skill_name" in data:
        skill.skill_name = data["skill_name"].strip()
    if "category" in data:
        skill.category = data["category"].strip()
    if "proficiency_level" in data:
        skill.proficiency_level = data["proficiency_level"].strip()
    if "years_of_experience" in data:
        skill.years_of_experience = float(data["years_of_experience"] or 0.0)

    session.commit()
    return jsonify({
        "message": "Skill updated",
        "skill": skill.to_dict(),
    }), 200

@profile_bp.route("/skills/<int:skill_id>", methods=["DELETE"])
@jwt_required
def delete_skill(skill_id: int):
    """Delete a skill."""
    session = get_db_session()
    skill = session.query(Skill).filter(
        Skill.id == skill_id,
        Skill.user_id == g.current_user.id
    ).first()

    if not skill:
        return jsonify({"error": "Skill not found or access denied"}), 404

    session.delete(skill)
    session.commit()
    return jsonify({"message": "Skill deleted"}), 200

# ==================== Experience Endpoints ====================

@profile_bp.route("/experience", methods=["POST"])
@jwt_required
def add_experience():
    """Add a work or internship experience entry."""
    data = request.get_json() or {}
    company = data.get("company", "").strip()
    job_title = data.get("job_title", "").strip()

    if not company or not job_title:
        return jsonify({"error": "Company and job title are required"}), 400

    session = get_db_session()
    exp = Experience(
        user_id=g.current_user.id,
        company=company,
        job_title=job_title,
        location=data.get("location", "").strip(),
        start_date=data.get("start_date", "").strip(),
        end_date=data.get("end_date", "").strip(),
        is_current=bool(data.get("is_current", False)),
        description=data.get("description", "").strip(),
    )
    session.add(exp)
    session.commit()

    return jsonify({
        "message": "Experience record added",
        "experience": exp.to_dict(),
    }), 201

@profile_bp.route("/experience/<int:exp_id>", methods=["PUT"])
@jwt_required
def update_experience(exp_id: int):
    """Update a work or internship experience entry."""
    session = get_db_session()
    exp = session.query(Experience).filter(
        Experience.id == exp_id,
        Experience.user_id == g.current_user.id
    ).first()

    if not exp:
        return jsonify({"error": "Experience record not found or access denied"}), 404

    data = request.get_json() or {}
    for field in ["company", "job_title", "location", "start_date", "end_date", "is_current", "description"]:
        if field in data:
            setattr(exp, field, data[field])

    session.commit()
    return jsonify({
        "message": "Experience record updated",
        "experience": exp.to_dict(),
    }), 200

@profile_bp.route("/experience/<int:exp_id>", methods=["DELETE"])
@jwt_required
def delete_experience(exp_id: int):
    """Delete a work experience entry."""
    session = get_db_session()
    exp = session.query(Experience).filter(
        Experience.id == exp_id,
        Experience.user_id == g.current_user.id
    ).first()

    if not exp:
        return jsonify({"error": "Experience record not found or access denied"}), 404

    session.delete(exp)
    session.commit()
    return jsonify({"message": "Experience record deleted"}), 200
