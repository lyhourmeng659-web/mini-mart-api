from app import bcrypt
from app.repositories.user_repository import UserRepository
from app.utils.validators import validate_email, validate_password


class UserService:
    @staticmethod
    def get_all(page=1, per_page=10, search=None):
        pagination = UserRepository.get_all(
            page=page,
            per_page=per_page,
            search=search
        )
        return pagination.items, pagination.total

    @staticmethod
    def get_by_id(user_id: int):
        user = UserRepository.find_by_id(user_id)
        if not user:
            return None, "User not found"
        return user, None

    @staticmethod
    def create(name, email, password, role_name="customer", phone=None, address=None):
        if not name or not email or not password:
            return None, "Name, email, and password are required"

        if not validate_email(email):
            return None, "Invalid email format"

        valid, msg = validate_password(password)
        if not valid:
            return None, msg

        if UserRepository.find_by_email(email):
            return None, "Email already exists"

        role = UserRepository.get_or_create_role(role_name)
        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

        user = UserRepository.create(
            name=name,
            email=email,
            password_hash=password_hash,
            role_id=role.id,
            phone=phone,
            address=address
        )
        return user, None

    @staticmethod
    def update(user_id: int, **kwargs):
        user = UserRepository.find_by_id(user_id)
        if not user:
            return None, "User not found"

        if "email" in kwargs and kwargs["email"]:
            existing = UserRepository.find_by_email(kwargs["email"])
            if existing and existing.id != user.id:
                return None, "Email already use"

        if "role" in kwargs and kwargs["role"]:
            role = UserRepository.get_or_create_role(kwargs["role"])
            kwargs["role_id"] = role.id
            del kwargs["role"]

        UserRepository.update(
            user,
            **kwargs
        )
        return user, None

    @staticmethod
    def delete(user_id: int):
        user = UserRepository.find_by_id(user_id)
        if not user:
            return False, "User not found"

        UserRepository.delete(user)
        return True, None
