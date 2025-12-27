import re
from email_validator import validate_email, EmailNotValidError
from flask import request, jsonify


def validate_email_format(email: str) -> tuple[bool, str]:
    try:
        validate_email(email, check_deliverability=False)
        return True, ""
    except EmailNotValidError as e:
        return False, str(e)


def validate_phone(phone: str) -> tuple[bool, str]:
    pattern = r'^\+?[1-9]\d{1,14}$'
    if re.match(pattern, phone):
        return True, ""
    return False, "Phone number must be in E.164 format"


def validate_request_json():
    if not request.is_json:
        return None, jsonify({
            "error": "Invalid input",
            "reason": "Request must be JSON",
            "module": "validation",
            "safe_for_demo": True
        }), 400
    return request.get_json(), None, None

