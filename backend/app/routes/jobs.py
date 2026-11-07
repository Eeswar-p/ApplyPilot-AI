from flask import Blueprint, request, jsonify, g
from sqlalchemy import or_
from app.database.db import get_db_session
from app.models.job import Job, JobPreference
from app.models.application import Application
from app.services.discovery import JobDiscoveryEngine
from app.utils.security import jwt_required

jobs_bp = Blueprint("jobs", __name__)

@jobs_bp.route("/discover", methods=["POST"])
@jwt_required
def trigger_discovery():
    """Trigger the multi-platform job discovery engine for the current user."""
    session = get_db_session()
    user_id = g.current_user.id

    try:
        engine = JobDiscoveryEngine(session)
        result = engine.run_discovery_for_user(user_id)
        return jsonify({
            "message": "Job discovery completed successfully",
            "stats": result,
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Discovery failed: {str(e)}"}), 500

@jobs_bp.route("", methods=["GET"])
@jwt_required
def list_jobs():
    """Retrieve paginated jobs with search and source filters, and user application status."""
    session = get_db_session()
    user_id = g.current_user.id

    # Query parameters
    search = request.args.get("search", "").strip()
    source = request.args.get("source", "").strip().lower()
    employment_type = request.args.get("employment_type", "").strip().lower()
    page = max(1, int(request.args.get("page", 1)))
    per_page = min(50, max(1, int(request.args.get("per_page", 12))))

    # Query jobs linked to the user's discovery & application history
    query = session.query(Job, Application).join(
        Application,
        (Application.job_id == Job.id) & (Application.user_id == user_id)
    )

    # Filter out any blacklisted companies from user preferences
    prefs = session.query(JobPreference).filter(JobPreference.user_id == user_id).first()
    if prefs and prefs.companies_blacklist:
        blacklist_items = [b.strip() for b in prefs.companies_blacklist.split(",") if b.strip()]
        for item in blacklist_items:
            query = query.filter(~Job.company.ilike(f"%{item}%"))

    # Search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Job.title.ilike(search_pattern),
                Job.company.ilike(search_pattern),
                Job.location.ilike(search_pattern),
                Job.description.ilike(search_pattern),
                Job.requirements.ilike(search_pattern),
            )
        )

    # Platform source filter
    if source and source != "all":
        query = query.filter(Job.source == source)

    # Employment type filter
    if employment_type and employment_type != "all":
        query = query.filter(Job.employment_type.ilike(f"%{employment_type}%"))

    total = query.count()
    results = query.order_by(Job.id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    jobs_data = []
    for job, application in results:
        job_dict = job.to_dict()
        job_dict["application_id"] = application.id
        job_dict["application_status"] = application.status
        job_dict["match_score"] = application.match_score
        job_dict["relevance_category"] = application.relevance_category
        jobs_data.append(job_dict)

    pages = (total + per_page - 1) // per_page if total > 0 else 1

    return jsonify({
        "jobs": jobs_data,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }), 200

@jobs_bp.route("/<int:job_id>", methods=["GET"])
@jwt_required
def get_job_details(job_id: int):
    """Retrieve full job description and application details for a single job."""
    session = get_db_session()
    user_id = g.current_user.id

    result = session.query(Job, Application).outerjoin(
        Application,
        (Application.job_id == Job.id) & (Application.user_id == user_id)
    ).filter(Job.id == job_id).first()

    if not result:
        return jsonify({"error": "Job opportunity not found"}), 404

    job, application = result
    job_dict = job.to_dict()
    if application:
        job_dict["application"] = application.to_dict()
    else:
        job_dict["application"] = None

    return jsonify({
        "job": job_dict
    }), 200
