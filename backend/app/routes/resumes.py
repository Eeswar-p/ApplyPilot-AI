from flask import Blueprint, request, jsonify, g
from app.database.db import get_db_session
from app.models.resume import Resume
from app.resume.storage import save_uploaded_resume, delete_stored_resume
from app.resume.parser import parse_resume_document
from app.utils.security import jwt_required

resumes_bp = Blueprint("resumes", __name__)

@resumes_bp.route("/upload", methods=["POST"])
@jwt_required
def upload_resume():
    """Upload a new PDF or DOCX resume, parse its text, and store metadata."""
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded with key 'resume'"}), 400

    file = request.files["resume"]
    session = get_db_session()
    user_id = g.current_user.id

    try:
        # 1. Save file to storage
        saved_path, original_filename, file_size, file_ext = save_uploaded_resume(file, user_id)

        # 2. Extract parsed text
        parse_result = parse_resume_document(saved_path, file_ext)
        parsed_text = parse_result.get("raw_text", "")

        # 3. Determine if this should be the primary resume
        existing_count = session.query(Resume).filter(Resume.user_id == user_id).count()
        is_primary = existing_count == 0

        # 4. Create database record
        resume_record = Resume(
            user_id=user_id,
            filename=original_filename,
            file_path=str(saved_path),
            file_size=file_size,
            file_type=file_ext,
            parsed_text=parsed_text,
            is_primary=is_primary,
        )
        session.add(resume_record)
        session.commit()

        return jsonify({
            "message": "Resume uploaded and parsed successfully",
            "resume": resume_record.to_dict(include_text=True),
            "meta": {
                "word_count": parse_result.get("word_count", 0),
                "detected_emails": parse_result.get("detected_emails", []),
                "detected_phones": parse_result.get("detected_phones", []),
            }
        }), 201

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Failed to process resume: {str(e)}"}), 500

@resumes_bp.route("", methods=["GET"])
@jwt_required
def list_resumes():
    """List all resumes uploaded by the current user."""
    session = get_db_session()
    user_id = g.current_user.id

    resumes = session.query(Resume).filter(
        Resume.user_id == user_id
    ).order_by(Resume.is_primary.desc(), Resume.id.desc()).all()

    return jsonify({
        "resumes": [r.to_dict(include_text=False) for r in resumes],
        "count": len(resumes),
    }), 200

@resumes_bp.route("/<int:resume_id>", methods=["GET"])
@jwt_required
def get_resume(resume_id: int):
    """Retrieve full resume details including parsed text."""
    session = get_db_session()
    user_id = g.current_user.id

    resume = session.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == user_id
    ).first()

    if not resume:
        return jsonify({"error": "Resume not found or access denied"}), 404

    return jsonify({
        "resume": resume.to_dict(include_text=True)
    }), 200

@resumes_bp.route("/<int:resume_id>/primary", methods=["PUT"])
@jwt_required
def set_primary_resume(resume_id: int):
    """Set a resume as the primary resume for automated applications."""
    session = get_db_session()
    user_id = g.current_user.id

    target_resume = session.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == user_id
    ).first()

    if not target_resume:
        return jsonify({"error": "Resume not found or access denied"}), 404

    # Unset primary flag for all user's resumes
    session.query(Resume).filter(Resume.user_id == user_id).update({"is_primary": False})
    
    # Set this resume as primary
    target_resume.is_primary = True
    session.commit()

    return jsonify({
        "message": "Primary resume updated",
        "resume": target_resume.to_dict(include_text=False)
    }), 200

@resumes_bp.route("/<int:resume_id>", methods=["DELETE"])
@jwt_required
def delete_resume(resume_id: int):
    """Delete a resume file from disk and database."""
    session = get_db_session()
    user_id = g.current_user.id

    resume = session.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == user_id
    ).first()

    if not resume:
        return jsonify({"error": "Resume not found or access denied"}), 404

    was_primary = resume.is_primary
    file_path = resume.file_path

    # Delete record from database
    session.delete(resume)
    session.commit()

    # Clean up physical file on disk
    delete_stored_resume(file_path)

    # If the deleted resume was primary, designate newest remaining resume as primary
    if was_primary:
        next_resume = session.query(Resume).filter(
            Resume.user_id == user_id
        ).order_by(Resume.id.desc()).first()
        if next_resume:
            next_resume.is_primary = True
            session.commit()

    return jsonify({"message": "Resume deleted successfully"}), 200
