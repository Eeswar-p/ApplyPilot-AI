import re
from flask import Blueprint, request, jsonify, g
from app.database.db import get_db_session
from app.models.user import User
from app.models.profile import UserProfile
from app.models.job import JobPreference
from app.models.automation import AutomationSetting
from app.utils.security import hash_password, verify_password, generate_token, jwt_required

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user, create initial profile, preferences, and automation settings."""
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()

    if not email:
        return jsonify({"error": "Email is required", "field": "email"}), 400

    if not re.match(EMAIL_REGEX, email):
        return jsonify({"error": "Invalid email address format", "field": "email"}), 400

    if not password or len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long", "field": "password"}), 400

    session = get_db_session()
    existing_user = session.query(User).filter(User.email == email).first()
    if existing_user:
        return jsonify({"error": "An account with this email already exists", "field": "email"}), 409

    try:
        pw_hash = hash_password(password)
        new_user = User(email=email, password_hash=pw_hash, is_active=True)
        session.add(new_user)
        session.flush() # Flush to get new_user.id

        # Initialize empty profile
        profile = UserProfile(
            user_id=new_user.id,
            full_name=full_name or email.split("@")[0].capitalize(),
            country="India",
        )
        session.add(profile)

        # Initialize default job preferences
        preferences = JobPreference(
            user_id=new_user.id,
            desired_titles="Software Engineer, Full Stack Developer, Frontend Developer, Backend Developer",
            desired_locations="Remote, Bangalore, Hyderabad, Pune, Mumbai, Delhi NCR",
            fresh_graduate_friendly=True,
        )
        session.add(preferences)

        # Initialize default automation settings
        settings = AutomationSetting(
            user_id=new_user.id,
            max_applications_per_session=15,
            application_delay_seconds=5,
            require_approval=False,
            auto_submit=True,
        )
        session.add(settings)

        session.commit()

        token = generate_token(new_user.id, new_user.email)
        return jsonify({
            "message": "User registered successfully",
            "token": token,
            "user": new_user.to_dict(),
            "profile": profile.to_dict(),
        }), 201

    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Failed to register user: {str(e)}"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate a user with email and password, issuing a JWT token."""
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    session = get_db_session()
    user = session.query(User).filter(User.email == email).first()

    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return jsonify({"error": "Invalid email or password", "code": "INVALID_CREDENTIALS"}), 401

    token = generate_token(user.id, user.email)
    profile = user.profile.to_dict() if user.profile else None

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict(),
        "profile": profile,
    }), 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required
def logout():
    """Acknowledge logout for the authenticated user session."""
    return jsonify({"message": "Logout successful"}), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required
def get_current_user_info():
    """Return current authenticated user and profile information."""
    user: User = g.current_user
    profile_data = user.profile.to_dict() if user.profile else None
    return jsonify({
        "user": user.to_dict(),
        "profile": profile_data,
    }), 200
