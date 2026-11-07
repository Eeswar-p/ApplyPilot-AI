from flask import Blueprint, request, jsonify, g
from app.utils.security import jwt_required
from app.models.automation import AutomationSetting, AutomationSession, AutomationLog
from app.automation.engine import ApplicationEngine
from app.automation.session_manager import AutomationSessionManager

automation_bp = Blueprint("automation", __name__)

@automation_bp.route("/start", methods=["POST"])
@jwt_required
def start_automation():
    user_id = g.current_user.id
    data = request.get_json() or {}
    headless = data.get("headless", True)
    max_jobs = data.get("max_jobs")

    if ApplicationEngine.is_running(user_id):
        return jsonify({
            "error": "Automation session is already running for this user."
        }), 400

    started = ApplicationEngine.start_background_session(
        user_id=user_id,
        headless=headless,
        max_jobs=max_jobs
    )

    if not started:
        return jsonify({"error": "Failed to launch automation session."}), 500

    session_mgr = AutomationSessionManager(g.db)
    session = session_mgr.get_latest_session(user_id)

    return jsonify({
        "message": "Automation session successfully launched.",
        "session": session.to_dict() if session else None
    }), 200

@automation_bp.route("/pause", methods=["POST"])
@jwt_required
def pause_automation():
    user_id = g.current_user.id
    ApplicationEngine.request_pause(user_id)
    session_mgr = AutomationSessionManager(g.db)
    session = session_mgr.pause_session(user_id)
    return jsonify({
        "message": "Automation paused successfully.",
        "session": session.to_dict() if session else None
    }), 200

@automation_bp.route("/resume", methods=["POST"])
@jwt_required
def resume_automation():
    user_id = g.current_user.id
    ApplicationEngine.request_resume(user_id)
    session = g.db.query(AutomationSession).filter(
        AutomationSession.user_id == user_id,
        AutomationSession.status == "paused"
    ).first()
    if session:
        session.status = "running"
        session_mgr = AutomationSessionManager(g.db)
        session_mgr.log(session.id, user_id, "INFO", "Resumed automation session")
        g.db.commit()

    return jsonify({
        "message": "Automation resumed successfully.",
        "session": session.to_dict() if session else None
    }), 200

@automation_bp.route("/stop", methods=["POST"])
@jwt_required
def stop_automation():
    user_id = g.current_user.id
    ApplicationEngine.request_stop(user_id)
    session_mgr = AutomationSessionManager(g.db)
    session = session_mgr.stop_session(user_id)
    return jsonify({
        "message": "Automation stopped successfully.",
        "session": session.to_dict() if session else None
    }), 200

@automation_bp.route("/status", methods=["GET"])
@jwt_required
def get_automation_status():
    user_id = g.current_user.id
    session_mgr = AutomationSessionManager(g.db)
    session = session_mgr.get_latest_session(user_id)
    is_running = ApplicationEngine.is_running(user_id)

    setting = g.db.query(AutomationSetting).filter(AutomationSetting.user_id == user_id).first()
    if not setting:
        setting = AutomationSetting(user_id=user_id)
        g.db.add(setting)
        g.db.commit()

    return jsonify({
        "is_running": is_running,
        "is_paused": ApplicationEngine._pause_flags.get(user_id, False),
        "session": session.to_dict() if session else None,
        "settings": setting.to_dict()
    }), 200

@automation_bp.route("/logs", methods=["GET"])
@jwt_required
def get_automation_logs():
    user_id = g.current_user.id
    limit = request.args.get("limit", 50, type=int)
    session_mgr = AutomationSessionManager(g.db)
    logs = session_mgr.get_session_logs(user_id, limit=limit)
    return jsonify({"logs": logs}), 200

@automation_bp.route("/settings", methods=["GET", "PUT"])
@jwt_required
def automation_settings():
    user_id = g.current_user.id
    setting = g.db.query(AutomationSetting).filter(AutomationSetting.user_id == user_id).first()
    if not setting:
        setting = AutomationSetting(user_id=user_id)
        g.db.add(setting)
        g.db.commit()

    if request.method == "GET":
        return jsonify({"settings": setting.to_dict()}), 200

    data = request.get_json() or {}
    if "max_applications_per_session" in data:
        setting.max_applications_per_session = int(data["max_applications_per_session"])
    if "application_delay_seconds" in data:
        setting.application_delay_seconds = int(data["application_delay_seconds"])
    if "require_approval" in data:
        setting.require_approval = bool(data["require_approval"])
    if "auto_submit" in data:
        setting.auto_submit = bool(data["auto_submit"])
    if "target_platforms" in data:
        setting.target_platforms = str(data["target_platforms"])

    g.db.commit()
    return jsonify({
        "message": "Automation settings updated successfully.",
        "settings": setting.to_dict()
    }), 200
