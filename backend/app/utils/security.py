from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Optional, Dict, Any
import bcrypt
import jwt
from flask import request, jsonify, current_app, g
from app.database.db import get_db_session
from app.models.user import User

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def generate_token(user_id: int, email: str, expires_in_hours: Optional[int] = None) -> str:
    """Generate a signed JWT access token for a user."""
    if expires_in_hours is None:
        expires_in_hours = current_app.config.get("JWT_EXPIRATION_HOURS", 24)
        
    secret_key = current_app.config.get("JWT_SECRET_KEY", "fallback_secret_key")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "user_id": user_id,
        "email": email,
        "iat": now,
        "exp": now + timedelta(hours=expires_in_hours),
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token."""
    secret_key = current_app.config.get("JWT_SECRET_KEY", "fallback_secret_key")
    return jwt.decode(token, secret_key, algorithms=["HS256"])

def jwt_required(f):
    """Decorator to enforce valid JWT Bearer authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return jsonify({"error": "Authorization header missing", "code": "AUTH_HEADER_MISSING"}), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Invalid Authorization header format. Expected 'Bearer <token>'", "code": "INVALID_TOKEN_FORMAT"}), 401

        token = parts[1]
        try:
            payload = decode_token(token)
            user_id = int(payload.get("user_id", payload.get("sub")))
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired", "code": "TOKEN_EXPIRED"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token", "code": "TOKEN_INVALID"}), 401

        session = get_db_session()
        user = session.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
        if not user:
            return jsonify({"error": "User not found or inactive", "code": "USER_NOT_FOUND"}), 401

        # Store authenticated user in Flask application context global `g`
        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function
