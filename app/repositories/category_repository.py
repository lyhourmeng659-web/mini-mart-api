from app import db

from app.models import Category


class CategoryRepository:
    @staticmethod
    def get_all(page=1, per_page=10, active_only=False):
        q = Category.query
        if active_only:
            q = q.filter_by(is_active=True)
        return q.order_by(Category.name).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_all_active():
        return Category.query.filter_by(is_active=True).order_by(Category.name).all()

    @staticmethod
    def find_by_id(category_id: int):
        return db.session.get(Category, category_id)

    @staticmethod
    def find_by_name(name: str):
        return Category.query.filter_by(name=name).first()

    @staticmethod
    def create(name: str, description: str = None):
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def update(category: Category, **kwargs):
        for key, value in kwargs.items():
            if hasattr(category, key) and value is not None:
                setattr(category, key, value)
        db.session.commit()
        return category

    @staticmethod
    def delete(category: Category):
        db.session.delete(category)
        db.session.commit()
