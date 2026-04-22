from flask_jwt_extended import create_access_token, create_refresh_token
from app import bcrypt, jwt_blacklist
from app.repositories.user_repository import UserRepository
from app.utils.validators import validate_email, validate_password


class AuthService:
    @staticmethod
    def register(name, email, password, role_name="customer", phone=None, address=None):
        if not name or not email or not password:
            return None, "Name, email, and password are required"

        if not validate_email(email):
            return None, "Invalid email format"

        valid, msg = validate_password(password)
        if not valid:
            return None, msg

        if UserRepository.find_by_email(email):
            return None, "Email already registered"

        role = UserRepository.get_or_create_role(role_name)
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
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
    def login(email, password):
        if not email or not password:
            return None, None, "Email and password are required"

        user = UserRepository.find_by_email(email)
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            return None, None, "Invalid email or password"

        if not user.is_active:
            return None, None, "Account is deactivated"

        identity = str(user.id)
        additional_claims = {
            "role": user.role.name
        }
        access_token = create_access_token(
            identity=identity,
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(
            identity=identity,
            additional_claims=additional_claims
        )
        return access_token, refresh_token, None

    @staticmethod
    def logout(jit: str):
        jwt_blacklist.add(jit)

    @staticmethod
    def reset_password(email, old_password, new_password):
        user = UserRepository.find_by_email(email)
        if not user:
            return None, "User not found"

        if not bcrypt.check_password_hash(user.password_hash, old_password):
            return None, "Current password is incorrect"

        valid, msg = validate_password(new_password)
        if not valid:
            return None, msg

        new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        UserRepository.update(
            user,
            password_hash=new_hash
        )
        return user, None
