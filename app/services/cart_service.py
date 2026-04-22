from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository


class CartService:
    @staticmethod
    def get_cart(user_id: int):
        items = CartRepository.get_user_cart(user_id)
        total = sum(float(i.product.price) * i.quantity for i in items if i.product)
        return {
            "items": [
                i.to_dict() for i in items
            ],
            "total": round(total, 2),
            "item_count": len(items)
        }

    @staticmethod
    def add_item(user_id: int, product_id: int, quantity: int = 1):
        if quantity <= 0:
            return None, "Quantity must be at least 1."

        product = ProductRepository.find_by_id(product_id)
        if not product or not product.is_active:
            return None, "Product not found or unavailable"

        if product.stock < quantity:
            return None, f"Insufficient stock. Available: {product.stock}"

        item = CartRepository.add_or_update(user_id, product_id, quantity)
        return item.to_dict(), None

    @staticmethod
    def update_item(user_id: int, product_id: int, quantity: int):
        if quantity <= 0:
            return None, "Quantity must be at least 1."

        item = CartRepository.find_item(user_id, product_id)
        if not item:
            return None, "Item not in cart"

        product = ProductRepository.find_by_id(product_id)
        if not product or not product.is_active:
            return None, f"Insufficient stock. Available: {product.stock}"

        CartRepository.update_quantity(item, quantity)
        return item.to_dict(), None

    @staticmethod
    def remove_item(user_id: int, product_id: int):
        item = CartRepository.find_item(user_id, product_id)
        if not item:
            return False, "Item not in cart"

        CartRepository.remove_item(item)
        return True, None

    @staticmethod
    def clear_cart(user_id: int):
        CartRepository.clear_cart(user_id)
