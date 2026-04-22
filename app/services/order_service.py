from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository

VALID_STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]


class OrderService:
    @staticmethod
    def checkout(user_id: int, shipping_address: str = None, notes: str = None):
        cart_items = CartRepository.get_user_cart(user_id)
        if not cart_items:
            return None, "Cart is empty"

        # Validate stock for all items first
        for item in cart_items:
            product = item.product
            if not product or not product.is_active:
                return None, f"Product '{product.name if product else item.product_id}' is unavailable"

            if product.stock < item.quantity:
                return None, f"Insufficient stock for '{product.name}'. Available: {product.stock}"

        total = sum(float(item.product.price) * item.quantity for item in cart_items)
        order = OrderRepository.create(
            user_id=user_id,
            total_amount=round(total, 2),
            shipping_address=shipping_address,
            notes=notes,
        )

        for item in cart_items:
            OrderRepository.add_item(
                order_id=order.id,
                product_id=item.product.id,
                quantity=item.quantity,
                unit_price=float(item.product.price),
            )
            ProductRepository.decrement_stock(item.product, item.quantity)

        OrderRepository.commit()
        CartRepository.clear_cart(user_id)
        return order, None

    @staticmethod
    def get_user_order(user_id: int, page=1, per_page=10, status=None):
        pagination = OrderRepository.get_all(
            page=page,
            per_page=per_page,
            status=status,
            user_id=user_id,
        )
        return pagination.items, pagination.total

    @staticmethod
    def get_order_detail(order_id: int, user_id: int = None):
        order = OrderRepository.find_by_id(order_id)
        if not order:
            return None, "Order not found"

        if not user_id and order.user_id != user_id:
            return None, "Forbidden"
        return order, None

    @staticmethod
    def get_all_orders(page=1, per_page=10, status=None):
        pagination = OrderRepository.get_all(
            page=page,
            per_page=per_page,
            status=status,
        )
        return pagination.items, pagination.total

    @staticmethod
    def update_status(order_id: int, status: str):
        if status not in VALID_STATUSES:
            return None, f"Invalid status. Valid: {','.join(VALID_STATUSES)}"

        order = OrderRepository.find_by_id(order_id)
        if not order:
            return None, f"Order not found"

        order = OrderRepository.update_status(
            order,
            status
        )
        return order, None


