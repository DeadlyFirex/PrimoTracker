from flask import request
from marshmallow import Schema, ValidationError

from services.response import response, ResponseType, generate_error

from functools import wraps
from re import compile
from uuid import UUID

alphanumeric_pattern = compile(r'^[a-zA-Z0-9_-]{2,50}$')
email_pattern = compile(r'^[a-zA-Z0-9-_]+@[a-zA-Z0-9.-]+\.[a-z]{1,15}$')
password_pattern = compile(
    r'^(?=.*[a-z])'  # At least one lowercase letter
    r'(?=.*[A-Z])'  # At least one uppercase letter
    r'(?=.*\d)'  # At least one digit
    r'(?=.*[@$!%*?&])'  # At least one special character
    r'[A-Za-z\d@$!%*?&]{8,50}$'  # Minimum length of 8 characters
)


def validate_alphanumeric(value: str) -> bool:
    """
    Validates if string is alphanumeric.

    :param value: String
    :return: Boolean
    """
    return bool(alphanumeric_pattern.match(value))


def validate_email(value: str) -> bool:
    """
    Validates if string is alphanumeric.

    :param value: String
    :return: Boolean
    """
    return bool(email_pattern.match(value)) and len(value) <= 75


def validate_password(value: str) -> bool:
    """
    Validates if string is alphanumeric.

    :param value: String
    :return: Boolean
    """
    return bool(password_pattern.match(value))


def validate_format(validation_type: str, value: str) -> bool:
    """
    Validates if strings are in correct format.

    :param validation_type: Type to validate
    :param value: String
    :return: Boolean
    """
    match validation_type:
        case "uuid":
            try:
                UUID(value)
            except ValueError:
                return False
            return True
        case "email":
            return bool(email_pattern.match(value))
        case "phone":
            return value.__len__() == 10 and value.isnumeric()
        case _:
            raise ValueError(f"Unknown type {validation_type}")


def validate_request(query: Schema = None, path: Schema = None,
                     headers: Schema = None, body: Schema = None):
    def decorator(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            body_content = request.get_json(silent=True)
            to_check = [(query, "query", request.args), (path, "path", request.view_args),
                        (headers, "headers", request.headers), (body, "body", body_content)]

            for schema, name, data in to_check:
                try:
                    kwargs[f"*{name}"] = schema.load(data) if schema is not None else None
                except ValidationError as error:
                    return response(ResponseType.ERROR, 400, "Bad request, check details",
                                    error=generate_error("REQUEST_INVALID", "Invalid request",
                                                         full=error.args.__str__(), args=error.args))
            return fn(*args, **kwargs)
        return decorated_function
    return decorator
