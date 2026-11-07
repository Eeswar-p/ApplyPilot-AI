from flask import Blueprint, request, jsonify, g
from app.database.db import get_db_session
from app.services.eligibility import EligibilityEngine
from app.utils.security import jwt_required

eligibility_bp = Blueprint("eligibility", __name__)

@eligibility_bp.route("/evaluate", methods=["POST"])
@jwt_required
def evaluate_eligibility():
    """Evaluate candidate eligibility for a single job or all discovered opportunities."""
    session = get_db_session()
    user_id = g.current_user.id
    data = request.get_json(silent=True) or {}
    job_id = data.get("job_id")

    engine = EligibilityEngine(session)

    try:
        if job_id:
            result = engine.evaluate_job_for_user(user_id, int(job_id))
            return jsonify({
                "message": "Job eligibility evaluated successfully",
                "evaluation": result,
            }), 200
        else:
            result = engine.evaluate_all_discovered_for_user(user_id)
            return jsonify({
                "message": f"Evaluated {result['total_evaluated']} opportunities. {result['eligible_count']} determined eligible.",
                "summary": result,
            }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Evaluation failed: {str(e)}"}), 500

@eligibility_bp.route("/<int:job_id>", methods=["GET"])
@jwt_required
def get_job_eligibility_breakdown(job_id: int):
    """Retrieve detailed matching breakdown, score components, and reasoning for a specific job."""
    session = get_db_session()
    user_id = g.current_user.id
    engine = EligibilityEngine(session)

    try:
        result = engine.evaluate_job_for_user(user_id, job_id)
        return jsonify({
            "evaluation": result
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve breakdown: {str(e)}"}), 500
