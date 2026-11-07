from datetime import datetime, timezone
from flask import Blueprint, jsonify
from sqlalchemy import text
from app.database.db import get_db_session

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """Verify backend and database health."""
    db_status = "healthy"
    try:
        session = get_db_session()
        session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return jsonify({
        "status": "ok",
        "service": "ApplyPilot AI Backend",
        "version": "1.0.0",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200
