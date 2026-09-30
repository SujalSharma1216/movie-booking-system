import re
from datetime import datetime

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def require_text(value: str, field: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{field} cannot be empty.")
    return value


def validate_email(email: str) -> str:
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        raise ValueError("Please enter a valid email address.")
    return email


def validate_password(password: str) -> str:
    if len(password) < 6:
        raise ValueError("Password must contain at least 6 characters.")
    return password


def validate_positive_int(value: str, field: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be a whole number.") from exc
    if number <= 0:
        raise ValueError(f"{field} must be greater than 0.")
    return number


def validate_rating(value: str) -> float:
    try:
        rating = float(value)
    except ValueError as exc:
        raise ValueError("Rating must be a number between 0 and 10.") from exc
    if not 0 <= rating <= 10:
        raise ValueError("Rating must be between 0 and 10.")
    return rating


def validate_price(value: str) -> float:
    try:
        price = float(value)
    except ValueError as exc:
        raise ValueError("Price must be a number.") from exc
    if price < 0:
        raise ValueError("Price cannot be negative.")
    return round(price, 2)


def validate_date(value: str) -> str:
    value = value.strip()
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Date must be in YYYY-MM-DD format.") from exc
    return value


def validate_time(value: str) -> str:
    value = value.strip()
    try:
        datetime.strptime(value, "%H:%M")
    except ValueError as exc:
        raise ValueError("Time must be in HH:MM (24-hour) format.") from exc
    return value
