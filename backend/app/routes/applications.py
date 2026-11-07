from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from sqlalchemy import or_, func
from app.utils.security import jwt_required
from app.models.application import Application
from app.models.job import Job
from app.models.resume import Resume

applications_bp = Blueprint("applications", __name__)

VALID_STATUSES = {
    "Discovered", "Eligible", "Pending Approval", "Applying",
    "Applied", "Failed", "Skipped", "Interview", "Rejected", "Offer Received"
}

@applications_bp.route("", methods=["GET"])
@jwt_required
def get_applications():
    user_id = g.current_user.id
    status = request.args.get("status")
    source = request.args.get("source")
    search = request.args.get("search")
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(100, max(1, request.args.get("limit", 20, type=int)))
    offset = (page - 1) * limit

    query = g.db.query(Application).join(Job).filter(Application.user_id == user_id)

    if status and status != "All":
        query = query.filter(Application.status == status)

    if source:
        query = query.filter(Job.source == source.lower())

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Job.title.ilike(search_pattern),
                Job.company.ilike(search_pattern),
                Job.location.ilike(search_pattern)
            )
        )

    total_count = query.count()
    apps = query.order_by(Application.updated_at.desc()).offset(offset).limit(limit).all()

    return jsonify({
        "applications": [app.to_dict() for app in apps],
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit if total_count > 0 else 1
    }), 200

@applications_bp.route("/<int:app_id>", methods=["GET"])
@jwt_required
def get_application(app_id):
    user_id = g.current_user.id
    app = g.db.query(Application).filter(
        Application.id == app_id,
        Application.user_id == user_id
    ).first()

    if not app:
        return jsonify({"error": "Application record not found."}), 404

    return jsonify({"application": app.to_dict()}), 200

@applications_bp.route("/<int:app_id>/status", methods=["PUT"])
@jwt_required
def update_application_status(app_id):
    user_id = g.current_user.id
    app = g.db.query(Application).filter(
        Application.id == app_id,
        Application.user_id == user_id
    ).first()

    if not app:
        return jsonify({"error": "Application record not found."}), 404

    data = request.get_json() or {}
    new_status = data.get("status")

    if not new_status or new_status not in VALID_STATUSES:
        return jsonify({
            "error": f"Invalid status. Must be one of: {', '.join(sorted(VALID_STATUSES))}"
        }), 400

    app.status = new_status
    if new_status == "Applied" and not app.applied_at:
        app.applied_at = datetime.now(timezone.utc)

    g.db.commit()

    return jsonify({
        "message": f"Application status updated to '{new_status}'.",
        "application": app.to_dict()
    }), 200

@applications_bp.route("/<int:app_id>/approve", methods=["POST"])
@jwt_required
def approve_application(app_id):
    user_id = g.current_user.id
    app = g.db.query(Application).filter(
        Application.id == app_id,
        Application.user_id == user_id
    ).first()

    if not app:
        return jsonify({"error": "Application record not found."}), 404

    if app.status != "Pending Approval":
        return jsonify({"error": "Only applications pending approval can be approved."}), 400

    app.status = "Applied"
    app.applied_at = datetime.now(timezone.utc)
    app.automation_result = "Approved by candidate and verified."
    g.db.commit()

    return jsonify({
        "message": "Application approved successfully.",
        "application": app.to_dict()
    }), 200

@applications_bp.route("/<int:app_id>", methods=["DELETE"])
@jwt_required
def delete_application(app_id):
    user_id = g.current_user.id
    app = g.db.query(Application).filter(
        Application.id == app_id,
        Application.user_id == user_id
    ).first()

    if not app:
        return jsonify({"error": "Application record not found."}), 404

    g.db.delete(app)
    g.db.commit()

    return jsonify({"message": "Application removed from tracking."}), 200

@applications_bp.route("/stats", methods=["GET"])
@jwt_required
def get_application_stats():
    """Returns dynamic, live database statistics for user dashboard analytics."""
    user_id = g.current_user.id

    # Total counts by status
    status_counts = dict(
        g.db.query(Application.status, func.count(Application.id))
        .filter(Application.user_id == user_id)
        .group_by(Application.status)
        .all()
    )

    total_discovered = sum(status_counts.values())
    applied = status_counts.get("Applied", 0)
    failed = status_counts.get("Failed", 0)
    eligible = status_counts.get("Eligible", 0)
    pending_approval = status_counts.get("Pending Approval", 0)
    applying = status_counts.get("Applying", 0)
    skipped = status_counts.get("Skipped", 0)
    interviews = status_counts.get("Interview", 0)
    offers = status_counts.get("Offer Received", 0)
    rejections = status_counts.get("Rejected", 0)

    # Success rate
    denom = applied + failed
    success_rate = round((applied / denom) * 100, 1) if denom > 0 else 0.0

    # Platform distribution
    platform_query = (
        g.db.query(Job.source, func.count(Application.id))
        .join(Application, Application.job_id == Job.id)
        .filter(Application.user_id == user_id)
        .group_by(Job.source)
        .all()
    )
    by_platform = [{"source": src or "other", "count": cnt} for src, cnt in platform_query]

    # Recent activity
    recent_apps = (
        g.db.query(Application)
        .filter(Application.user_id == user_id)
        .order_by(Application.updated_at.desc())
        .limit(8)
        .all()
    )

    return jsonify({
        "total_discovered": total_discovered,
        "eligible": eligible,
        "pending_approval": pending_approval,
        "applying": applying,
        "applied": applied,
        "failed": failed,
        "skipped": skipped,
        "interviews": interviews,
        "offers": offers,
        "rejections": rejections,
        "success_rate": success_rate,
        "by_platform": by_platform,
        "recent_activity": [app.to_dict() for app in recent_apps]
    }), 200
