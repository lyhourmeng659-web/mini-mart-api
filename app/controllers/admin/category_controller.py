from flask import Blueprint, request

from app.middleware.auth_middleware import admin_required
from app.services.category_service import CategoryService
from app.utils.pagination import get_pagination_params
from app.utils.response import paginated_response, error_response, success_response

admin_category_bp = Blueprint("admin_category", __name__)


@admin_category_bp.route("", methods=["GET"])
@admin_required
def list_categories():
    page, per_page = get_pagination_params()
    items, total = CategoryService.get_all(page=page, per_page=per_page)
    return paginated_response([
        c.to_dict() for c in items
    ], total, page, per_page
    )


@admin_category_bp.route("/<int:category_id>", methods=["GET"])
@admin_required
def get_category(category_id):
    cat, err = CategoryService.get_by_id(category_id)
    if err:
        return error_response(err, 404)
    return success_response(cat.to_dict())


@admin_category_bp.route("", methods=["POST"])
def create_category():
    data = request.get_json() or {}
    cat, err = CategoryService.create(
        name=data.get("name"),
        description=data.get("description")
    )
    if err:
        return error_response(err, 400)
    return success_response(cat.to_dict(), "Category created", 201)


@admin_category_bp.route("/<int:category_id>", methods=["PUT"])
@admin_required
def update_category(category_id):
    data = request.get_json() or {}
    cat, err = CategoryService.update(
        category_id,
        name=data.get("name"),
        description=data.get("description"),
        is_active=data.get("is_active")
    )
    if err:
        return error_response(err, 400)
    return success_response(cat.to_dict(), "Category updated")


@admin_category_bp.route("/<int:category_id>", methods=["DELETE"])
@admin_required
def delete_category(category_id):
    success, err = CategoryService.delete(category_id)
    if err:
        return error_response(err, 400)
    return success_response({}, "Category deleted")
