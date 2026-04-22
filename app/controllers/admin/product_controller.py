from flask import Blueprint, request
from app.middleware.auth_middleware import admin_required
from app.services.product_service import ProductService
from app.utils.pagination import get_pagination_params
from app.utils.response import paginated_response, error_response, success_response

admin_product_bp = Blueprint("admin_product", __name__)


@admin_product_bp.route("", methods=["GET"])
@admin_required
def list_products():
    page, per_page = get_pagination_params()
    category_id = request.args.get("category_id", type=int)
    search = request.args.get("search")
    items, total = ProductService.get_all(
        page=page, per_page=per_page, category_id=category_id, search=search
    )
    return paginated_response([p.to_dict() for p in items], total, page, per_page)


@admin_product_bp.route("/<int:product_id>", methods=["GET"])
@admin_required
def get_product(product_id):
    product, err = ProductService.get_by_id(product_id)
    if err:
        return error_response(err, 404)
    return success_response(product.to_dict())


@admin_product_bp.route("", methods=["POST"])
@admin_required
def create_product():
    if request.is_json:
        data = request.get_json() or {}
        image_file = None
    else:
        data = request.form.to_dict() if request.form else {}
        image_file = request.files.get("image")

    category_id = data.get("category_id")
    if category_id is not None:
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            return error_response("category_id must be a number", 400)

    product, err = ProductService.create(
        name=data.get("name"),
        price=data.get("price"),
        category_id=category_id,
        description=data.get("description"),
        stock=data.get("stock", 0),
        image_file=image_file,
    )
    if err:
        return error_response(err, 400)
    return success_response(product.to_dict(), "Product created", 201)


@admin_product_bp.route("/<int:product_id>", methods=["PUT"])
@admin_required
def update_product(product_id):
    data = request.form.to_dict() if request.form else (request.get_json() or {})
    image_file = request.files.get("image")

    category_id = data.get("category_id")
    if category_id is not None:
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            return error_response("category_id must be a number", 400)

    product, err = ProductService.update(
        product_id,
        image_file=image_file,
        name=data.get("name"),
        price=data.get("price"),
        category_id=category_id,
        description=data.get("description"),
        stock=data.get("stock"),
        is_active=data.get("is_active"),
    )
    if err:
        return error_response(err, 400)
    return success_response(product.to_dict(), "Product updated")


@admin_product_bp.route("/<int:product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id):
    success, err = ProductService.delete(product_id)
    if err:
        return error_response(err, 400)
    return success_response({}, "Product deleted")
