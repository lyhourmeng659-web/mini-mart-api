from datetime import datetime, timezone
from app import db


class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (db.UniqueConstraint("user_id", "product_id", name="uq_user_product"),)

    def to_dict(self):
        product = self.product
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": product.name if product else None,
            "price": float(product.price) if product else 0,
            "quantity": self.quantity,
            "subtotal": float(product.price) * self.quantity if product else 0,
            "image_url": product.image_url() if product else None,
        }

    def __repr__(self):
        return f"<Cart user={self.user_id} product={self.product_id}>"