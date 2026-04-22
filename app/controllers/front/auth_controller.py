from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from app.middleware.auth_middleware import jwt_required_custom, get_current_user
from app.services.auth_service import AuthService
from app.utils.response import error_response, success_response

front_auth_bp = Blueprint("front_auth", __name__)


@front_auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    user, err = AuthService.register(
        name=data.get("name"),
        email=data.get("email"),
        password=data.get("password"),
        phone=data.get("phone"),
        address=data.get("address"),
        role_name="customer"
    )
    if err:
        return error_response(err, 400)
    return success_response(user.to_dict(), "Registration successful", 201)


@front_auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    access_token, refresh_token, err = AuthService.login(
        data.get("email"),
        data.get("password")
    )
    if err:
        return error_response(err, 401)
    return success_response(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, "Login successful"
    )


@front_auth_bp.route("/logout", methods=["POST"])
@jwt_required_custom
def logout():
    jti = get_jwt()["jti"]
    AuthService.logout(jti)
    return success_response({}, "Logged out successfully")


@front_auth_bp.route("/me", methods=["GET"])
@jwt_required_custom
def me():
    user = get_current_user()
    return success_response(user.to_dict())


@front_auth_bp.route("/reset-password", methods=["POST"])
@jwt_required_custom
def reset_password():
    data = request.get_json() or {}
    user = get_current_user()

    # Validate required fields
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    if not old_password or not new_password:
        return error_response("old_password and new_password are required", 400)

    _, err = AuthService.reset_password(
        email=user.email,
        old_password=old_password,
        new_password=new_password,
    )
    if err:
        return error_response(err, 400)
    return success_response({}, "Password reset successfully")
