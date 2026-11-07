from flask import Flask
from app.routes.health import health_bp
from app.routes.auth import auth_bp
from app.routes.profile import profile_bp
from app.routes.resumes import resumes_bp
from app.routes.preferences import preferences_bp
from app.routes.jobs import jobs_bp
from app.routes.eligibility import eligibility_bp
from app.routes.automation import automation_bp
from app.routes.applications import applications_bp

def register_routes(app: Flask):
    """Register all route blueprints with Flask app."""
    # System & Health
    app.register_blueprint(health_bp, url_prefix="/api")
    
    # Phase 2: Authentication & User Management
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(profile_bp, url_prefix="/api/profile")

    # Phase 3: Resume Management
    app.register_blueprint(resumes_bp, url_prefix="/api/resumes")

    # Phase 4: Job Preferences
    app.register_blueprint(preferences_bp, url_prefix="/api/preferences")

    # Phase 5: Job Discovery
    app.register_blueprint(jobs_bp, url_prefix="/api/jobs")

    # Phase 6: Eligibility Evaluation
    app.register_blueprint(eligibility_bp, url_prefix="/api/eligibility")

    # Phase 8: Automation Engine & Controls
    app.register_blueprint(automation_bp, url_prefix="/api/automation")

    # Phase 9: Application Tracking System (ATS) & Analytics
    app.register_blueprint(applications_bp, url_prefix="/api/applications")
