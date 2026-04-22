from flask import Blueprint, request
from app.middleware.auth_middleware import admin_required
from app.services.order_service import OrderService
from app.utils.pagination import get_pagination_params
from app.utils.response import success_response, paginated_response, error_response

admin_order_bp = Blueprint("admin_order", __name__)


@admin_order_bp.route("", methods=["GET"])
@admin_required
def list_orders():
    page, per_page = get_pagination_params()
    status = request.args.get("status")
    items, total = OrderService.get_all_orders(
        page=page,
        per_page=per_page,
        status=status,
    )
    return paginated_response(
        [
            o.to_dict() for o in items
        ],
        total,
        page,
        per_page
    )


@admin_order_bp.route("/<int:order_id>/status", methods=["GET"])
@admin_required
def get_order(order_id):
    order, err = OrderService.get_order_detail(
        order_id
    )
    if err:
        return success_response(err, 404)
    return success_response(order.to_dict(include_item=True))


@admin_order_bp.route("/<int:order_id>/status", methods=["PUT"])
@admin_required
def update_status(order_id):
    data = request.get_json() or {}
    status = data.get("status")

    if not status:
        return error_response("Status is required", 400)

    order, err = OrderService.update_status(
        order_id,
        status,
    )
    if err:
        return error_response(err, 400)
    return success_response(
        order.to_dict(include_items=True),
        f"Order status updated to '{status}'"
    )
