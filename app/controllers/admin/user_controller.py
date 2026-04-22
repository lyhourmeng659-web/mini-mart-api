from flask import Blueprint, request
from app.services.user_service import UserService
from app.middleware.auth_middleware import admin_required
from app.utils.response import success_response, error_response, paginated_response
from app.utils.pagination import get_pagination_params

admin_user_bp = Blueprint("admin_user", __name__)


@admin_user_bp.route("", methods=["GET"])
@admin_required
def list_users():
    page, per_page = get_pagination_params()
    search = request.args.get("search")
    items, total = UserService.get_all(
        page=page,
        per_page=per_page,
        search=search,
    )
    return paginated_response(
        [
            u.to_dict() for u in items
        ],
        total,
        page,
        per_page
    )


@admin_user_bp.route("/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id: int):
    user, err = UserService.get_by_id(user_id)
    if err:
        return error_response(err, 404)
    return success_response(user.to_dict())


@admin_user_bp.route("", methods=["POST"])
@admin_required
def create_user():
    data = request.get_json() or {}
    user, err = UserService.create(
        name=data.get("name"),
        email=data.get("email"),
        password=data.get("password"),
        role_name=data.get("role_name", "customer"),
        phone=data.get("phone"),
        address=data.get("address"),
    )
    if err:
        return error_response(
            err, 400
        )
    return success_response(
        user.to_dict(),
        "User created successfully",
        201
    )


@admin_user_bp.route("/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    data = request.get_json() or {}
    user, err = UserService.update(
        user_id,
        name=data.get("name"),
        email=data.get("email"),
        phone=data.get("phone"),
        address=data.get("address"),
        role=data.get("role"),
        is_active=data.get("is_active"),
    )
    if err:
        return error_response(err, 400)
    return success_response(user.to_dict(), "User updated successfully")


@admin_user_bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    success, err = UserService.delete(user_id)
    if err:
        return error_response(err, 404)
    return success_response({}, "User deleted successfully")
