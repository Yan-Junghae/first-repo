"""Small validation helpers shared by routes and services."""
import re
from datetime import date, datetime, time
from app.domain.exceptions import ValidationError


def required_text(value, label, max_length=200):
    value = (value or "").strip()
    if not value:
        raise ValidationError([f"{label} is required."])
    if len(value) > max_length:
        raise ValidationError([f"{label} must be {max_length} characters or fewer."])
    return value


def parse_birth_date(value):
    try:
        result = date.fromisoformat(value or "")
    except ValueError:
        raise ValidationError(["Enter a valid date of birth."])
    if result > date.today():
        raise ValidationError(["Date of birth cannot be in the future."])
    return result


def normalize_phone(value):
    value = required_text(value, "Phone number", 30)
    normalized = re.sub(r"[\s()-]", "", value)
    if not re.fullmatch(r"\+?\d{7,15}", normalized):
        raise ValidationError(["Enter a valid phone number (7–15 digits, optional leading +)."])
    return normalized


def parse_appointment_time(value):
    try:
        result = datetime.fromisoformat(value or "")
    except ValueError:
        raise ValidationError(["Enter a valid appointment date and time."])
    if result <= datetime.now():
        raise ValidationError(["Appointment must be in the future."])
    if result.second or result.microsecond:
        result = result.replace(second=0, microsecond=0)
    return result
