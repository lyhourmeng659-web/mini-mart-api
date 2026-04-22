from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity

from app.repositories.user_repository import UserRepository
from app.utils.response import error_response


def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            return error_response(str(e), 401)
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "admin":
                return error_response("Admin access required", 403)
        except Exception as e:
            return error_response(str(e), 401)
        return fn(*args, **kwargs)

    return wrapper


def get_current_user():
    user_id = get_jwt_identity()
    return UserRepository.find_by_id(int(user_id))
