from app import db

from app.models import Product


class ProductRepository:
    @staticmethod
    def get_all(page=1, per_page=10, category_id=None, search=None, active_only=False):
        q = Product.query
        if active_only:
            q = q.filter_by(is_active=True)
        if category_id:
            q = q.filter_by(category_id=category_id)
        if search:
            q = q.filter(Product.name.ilike(f"%{search}%"))
        return q.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def find_by_id(product_id: int):
        return db.session.get(Product, product_id)

    @staticmethod
    def create(name, price, category_id, description=None, stock=0, image=None):
        product = Product(
            name=name,
            price=price,
            category_id=category_id,
            description=description,
            stock=stock,
            image=image,
        )
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def update(product: Product, **kwargs):
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        db.session.commit()
        return product

    @staticmethod
    def delete(product: Product):
        db.session.delete(product)
        db.session.commit()

    @staticmethod
    def decrement_stock(product: Product, quantity: int):
        product.stock = max(0, product.stock - quantity)
        db.session.commit()
