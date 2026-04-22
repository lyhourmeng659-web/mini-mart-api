from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity

from app.middleware.auth_middleware import jwt_required_custom
from app.services.cart_service import CartService
from app.utils.response import success_response, error_response

front_cart_bp = Blueprint("front_cart", __name__)


@front_cart_bp.route("", methods=["GET"])
@jwt_required_custom
def get_cart():
    user_id = int(get_jwt_identity())
    cart = CartService.get_cart(user_id)
    return success_response(cart)


@front_cart_bp.route("/add", methods=["POST"])
@jwt_required_custom
def add_to_cart():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return error_response("product_id is required", 400)

    item, err = CartService.add_item(user_id, int(product_id), int(quantity))
    if err:
        return error_response(err, 400)
    return success_response(item, "Item added to cart", 201)


@front_cart_bp.route("/update", methods=["PUT"])
@jwt_required_custom
def update_cart():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id or quantity is None:
        return error_response("product_id and quantity is required", 400)

    item, err = CartService.update_item(user_id, int(product_id), int(quantity))
    if err:
        return error_response(err, 400)
    return success_response(item, "Cart updated")


@front_cart_bp.route("/remove/<int:product_id>", methods=["DELETE"])
@jwt_required_custom
def remove_from_cart(product_id):
    user_id = int(get_jwt_identity())
    success, err = CartService.remove_item(user_id, product_id)
    if err:
        return error_response(err, 400)
    return success_response({}, "Item removed from cart")


@front_cart_bp.route("/clear", methods=["DELETE"])
@jwt_required_custom
def clear_cart():
    user_id = int(get_jwt_identity())
    CartService.clear_cart(user_id)
    return success_response({}, "Cart cleared")
