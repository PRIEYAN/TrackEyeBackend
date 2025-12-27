import bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt
from app.models.user import User


def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_token(user: User) -> dict:
    access_token = create_access_token(
        identity=user.email,
        additional_claims={"role": user.role}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800,  # 30 minutes
        "user": user.to_dict()
    }


def get_current_user():
    email = get_jwt_identity()
    return User.objects(email=email).first()


def require_role(*roles):
    from functools import wraps
    from flask_jwt_extended import verify_jwt_in_request
    
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')
            if user_role not in roles:
                from flask import jsonify
                return jsonify({
                    "error": "Forbidden",
                    "reason": "Insufficient permissions",
                    "module": "auth",
                    "safe_for_demo": True
                }), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

