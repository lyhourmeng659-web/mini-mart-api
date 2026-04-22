from flask import Blueprint, request

from app.services.product_service import ProductService
from app.utils.pagination import get_pagination_params
from app.utils.response import success_response, paginated_response, error_response

front_product_bp = Blueprint("front_product", __name__)


@front_product_bp.route("", methods=["GET"])
def list_products():
    page, per_page = get_pagination_params()
    category_id = request.args.get("category_id", type=int)
    search = request.args.get("search")
    items, total = ProductService.get_all(
        page=page, per_page=per_page,
        category_id=category_id, search=search, active_only=True
    )
    return paginated_response([p.to_dict() for p in items], total, page, per_page)


@front_product_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product, err = ProductService.get_by_id(product_id)
    if err:
        return error_response(err, 404)
    if not product.is_active:
        return error_response("Product not available", 404)
    return success_response(product.to_dict())
