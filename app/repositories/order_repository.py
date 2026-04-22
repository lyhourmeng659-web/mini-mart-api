import uuid
from datetime import datetime, timezone

from app import db

from app.models import Order, OrderItem


class OrderRepository:
    @staticmethod
    def generate_order_number():
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        uid = uuid.uuid4().hex[:6].upper()
        return f"ORD-{ts}-{uid}"

    @staticmethod
    def get_all(page=1, per_page=10, status=None, user_id=None):
        q = Order.query
        if status:
            q = q.filter_by(status=status)
        if user_id:
            q = q.filter_by(user_id=user_id)
        return q.order_by(Order.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

    @staticmethod
    def find_by_id(order_id: int):
        return db.session.get(Order, order_id)

    @staticmethod
    def find_by_number(order_number: str):
        return Order.query.filter_by(order_number=order_number).first()

    @staticmethod
    def create(user_id, total_amount, shipping_address=None, notes=None):
        order = Order(
            order_number=OrderRepository.generate_order_number(),
            user_id=user_id,
            total_amount=total_amount,
            shipping_address=shipping_address,
            notes=notes,
        )
        db.session.add(order)
        db.session.commit()
        return order

    @staticmethod
    def add_item(order_id, product_id, quantity, unit_price):
        item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=unit_price * quantity
        )
        db.session.add(item)
        return item

    @staticmethod
    def update_status(order: Order, status: str):
        order.status = status
        db.session.commit()
        return order

    @staticmethod
    def commit():
        db.session.commit()

    # Reporting
    @staticmethod
    def sales_by_period(start: datetime, end: datetime):
        from sqlalchemy import func
        return (
            db.session.query(
                func.date(Order.created_at).label("date"),
                func.count(Order.id).label("order_count"),
                func.sum(Order.total_amount).label("revenue")
            )
            .filter(Order.created_at >= start, Order.created_at <= end)
            .filter(Order.status != "cancelled")
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
            .all()
        )

    @staticmethod
    def sales_by_product(start: datetime, end: datetime):
        from sqlalchemy import func
        from app.models.product import Product
        return (
            db.session.query(
                Product.id,
                Product.name,
                func.sum(OrderItem.quantity).label("total_qty"),
                func.sum(OrderItem.subtotal).label("revenue")
            )
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(Order.created_at >= start, Order.created_at <= end)
            .filter(Order.status != "cancelled")
            .group_by(Product.id, Product.name)
            .order_by(db.desc("revenue"))
            .all()
        )

    @staticmethod
    def sales_by_category(start: datetime, end: datetime):
        from sqlalchemy import func
        from app.models.product import Product
        from app.models.category import Category
        return (
            db.session.query(
                Category.id,
                Category.name,
                func.sum(OrderItem.quantity).label("total_qty"),
                func.sum(OrderItem.subtotal).label("revenue")
            )
            .join(Product, Product.category_id == Category.id)
            .join(OrderItem, OrderItem.product_id == Product.id)
            .join(Order, Order.id == OrderItem.order_id)
            .filter(Order.created_at >= start, Order.created_at <= end)
            .filter(Order.status != "cancelled")
            .group_by(Category.id, Category.name)
            .order_by(db.desc("revenue"))
            .all()
        )
