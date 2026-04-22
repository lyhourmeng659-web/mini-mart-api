from app import db
from app.models.cart import Cart


class CartRepository:
    @staticmethod
    def get_user_cart(user_id: int):
        return Cart.query.filter_by(user_id=user_id).all()

    @staticmethod
    def find_item(user_id: int, product_id: int):
        return Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    @staticmethod
    def add_or_update(user_id: int, product_id: int, quantity: int):
        item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
        if item:
            item.quantity = quantity
        else:
            item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
            db.session.add(item)
        db.session.commit()
        return item

    @staticmethod
    def update_quantity(cart_item: Cart, quantity: int):
        cart_item.quantity = quantity
        db.session.commit()
        return cart_item

    @staticmethod
    def remove_item(cart_item: Cart):
        db.session.delete(cart_item)
        db.session.commit()

    @staticmethod
    def clear_cart(user_id: int):
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
