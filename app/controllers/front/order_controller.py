from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.middleware.auth_middleware import jwt_required_custom
from app.services.order_service import OrderService
from app.utils.pagination import get_pagination_params
from app.utils.response import error_response, success_response, paginated_response

front_order_bp = Blueprint("front_order", __name__)


@front_order_bp.route("/checkout", methods=["POST"])
@jwt_required_custom
def checkout():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    order, err = OrderService.checkout(
        user_id=user_id,
        shipping_address=data.get("shipping_address"),
        notes=data.get("notes"),
    )
    if err:
        return error_response(err, 400)
    return success_response(order.to_dict(include_items=True), "Order placed successfully", 201)


@front_order_bp.route("", methods=["GET"])
@jwt_required_custom
def list_orders():
    user_id = int(get_jwt_identity())
    page, per_page = get_pagination_params()
    status = request.args.get("status")
    items, total = OrderService.get_user_order(
        user_id=user_id,
        page=page,
        per_page=per_page,
        status=status,
    )
    return paginated_response([
        o.to_dict()
        for o in items
    ],
        total,
        page,
        per_page
    )


@front_order_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required_custom
def get_order(order_id):
    user_id = int(get_jwt_identity())
    order, err = OrderService.get_order_detail(
        order_id,
        user_id=user_id,
    )
    if err:
        code = 403 if err == "Forbidden" else 404
        return error_response(err, code)
    return success_response(order.to_dict(include_items=True))
