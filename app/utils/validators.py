# regular expression
import re


def validate_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, str]:
    if len(password < 8):
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    return True, ""


def validate_required_fields(data: dict, fields: list) -> list:
    missing = [f for f in fields if not data.get(f)]
    return missing


def validate_positive_number(value, field_name="Value") -> tuple[bool, str]:
    try:
        num = float(value)
        if num < 0:
            return False, f"{field_name} must be non-negative"
        return True, ""
    except (TypeError, ValueError):
        return False, f"{field_name} must be a valid number"
