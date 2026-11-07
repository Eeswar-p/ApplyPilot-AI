import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import config_by_name
from app.database.db import init_db, create_all_tables, SessionLocal
# Import models to ensure they are registered with Base metadata
import app.models # noqa: F401
from app.routes import register_routes

def create_app(config_name: str = None) -> Flask:
    """Application factory for ApplyPilot AI Flask API."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    config_obj = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(config_obj)

    # Initialize CORS for frontend and extensions
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "chrome-extension://*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    # Ensure storage folders exist
    os.makedirs(app.config["RESUME_STORAGE_DIR"], exist_ok=True)
    os.makedirs(app.config["LOGS_STORAGE_DIR"], exist_ok=True)

    # Initialize database
    init_db(app.config["SQLALCHEMY_DATABASE_URI"])
    create_all_tables()

    # Register routes
    register_routes(app)

    # Clean up database sessions at end of request
    @app.teardown_appcontext
    def remove_session(exception=None):
        if SessionLocal:
            SessionLocal.remove()

    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found", "status_code": 404}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error", "status_code": 500}), 500

    return app
