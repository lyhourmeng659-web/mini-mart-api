from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from app.middleware.auth_middleware import admin_required
from app.services.auth_service import AuthService
from app.utils.response import error_response, success_response

admin_auth_bp = Blueprint("admin_auth", __name__)


@admin_auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    access_token, refresh_token, err = AuthService.login(
        data.get("email"),
        data.get("password")
    )

    # Verify admin role
    from flask_jwt_extended import decode_token
    try:
        decoded = decode_token(access_token)
        if decoded.get("role") != "admin":
            return error_response("Admin access required", 403)
    except Exception:
        return error_response("Token error", 500)

    return success_response(
        {
            "refresh_token": refresh_token,
            "access_token": access_token,
        },
        "Admin login successful"
    )


@admin_auth_bp.route("/logout", methods=["POST"])
@admin_required
def logout():
    jti = get_jwt()["jti"]
    AuthService.logout(jti)
    return success_response(
        {},
        "Logged out successfully"
    )
