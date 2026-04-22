from app import db
from app.models.user import User, Role


class UserRepository:
    @staticmethod
    def find_by_email(email: str):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def find_by_id(user_id: int):
        return db.session.get(User, user_id)

    @staticmethod
    def get_all(page: 1, per_page: 10, search=None):
        q = User.query
        if search:
            q = q.filter(
                db.or_(
                    User.name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                )
            )
        return q.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def create(name, email, password_hash, role_id, phone=None, address=None):
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role_id=role_id,
            phone=phone,
            address=address
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(user: User, **kwargs):
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        db.session.commit()
        return user

    @staticmethod
    def delete(user: User):
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def get_role_by_name(name: str):
        return User.query.filter_by(name=name).first()

    @staticmethod
    def get_or_create_role(name: str):
        role = Role.query.filter_by(name=name).first()
        if not role:
            role = Role(name=name)
            db.session.add(role)
            db.session.commit()
        return role
