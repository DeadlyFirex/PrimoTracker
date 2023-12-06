from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from services.config import Config

from typing import Union
from functools import wraps
from re import match
from datetime import datetime
from uuid import UUID

config = Config().get()


def response(status: int = 200, message: str = "This is a message"):
    """
    Generates an JSON response.
    Returns a dictionary.

    :return: Dictionary
    """
    result = {
        "status": status,
        "message": message
    }
    return result, status


def error_response(status: int = 200, message: str = "This is a message", error: Union[str, dict] = None):
    """
    Generates an JSON response.
    Returns a dictionary.

    :return: Dictionary
    """
    result = {
        "status": status,
        "message": message
    }
    result.update({"error": error})
    return result, status


def detailed_response(status: int = 200, message: str = "This is a message", details: Union[str, dict] = None):
    """
    Generates an JSON response.
    Returns a dictionary.

    :return: Dictionary
    """
    result = {
        "status": status,
        "message": message,
    }
    result.update({"details": details})
    return result, status


def custom_response(status: int = 200, message: str = "This is a message", custom: Union[str, dict] = None):
    """
    Generates a custom JSON response.\n
    Returns a dictionary.\n
    Appends a new dictionary to the standard one.\n

    :return: Dictionary
    """
    result = {
        "status": status,
        "message": message,
    }
    result.update(custom)
    return result, status


def return_result(status: int = 200, message: str = "This is a message", result: Union[str, dict, list] = None):
    """
    Generates an JSON response based on the successful result template.
    Returns a dictionary.

    :return: Dictionary
    """
    result = {
        "status": status,
        "message": message,
        "result": result
    }
    return result, status


def calculate_time(start: datetime, end: datetime = datetime.now()):
    """
    Calculates time difference in milliseconds.\n
    Returns the result in two decimal rounded string.

    :param start: Start datetime object
    :param end: End datetime object
    :return: Time difference in milliseconds, string.
    """
    return f"{round((end - start).total_seconds() * 1000, 2)}ms"


def validate_format(validation_type: any, value: str) -> Union[bool, ValueError]:
    """
    Validates if strings are in correct format.

    :param validation_type: Type to validate against
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
            return match("""^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\\.[a-z]{1,3}$""", value) is not None
        case "phone":
            return value.__len__() == 10 and value.isnumeric()
        case "postal_code":
            return match("""^[0-9]{4}[A-Z]{2}$""", value) is not None
        case _:
            raise ValueError(f"Unknown type {validation_type}")


def generate_database_url():
    match config.database.type:
        case "memory":
            return "sqlite:///:memory:"
        case "sqlite":
            return f"{config.database.type}:///{config.database.host}"
        case _:
            return (f"{config.database.type}://{config.database.credentials.username}"
                    f":{config.database.credentials.password}@{config.database.host}"
                    f":{config.database.port}/{config.database.name}")


def generate_storage_url():
    match config.ratelimit.storage.type:
        case "memory":
            return f"{config.ratelimit.storage.type}://"
        case "redis":
            return f"{config.ratelimit.storage.type}://{config.ratelimit.storage.host}:{config.ratelimit.storage.port}"
        case "etcd":
            return f"{config.ratelimit.storage.type}://{config.ratelimit.storage.host}:{config.ratelimit.storage.port}"
        case "mongodb":
            return (f"{config.ratelimit.storage.type}://"
                    f"{config.ratelimit.storage.credentials.username if config.ratelimit.storage.credentials.username else ''}"
                    f"{':' + config.ratelimit.storage.credentials.password + '@' if config.ratelimit.storage.credentials.password else ''}"
                    f"{config.ratelimit.storage.host}:{config.ratelimit.storage.port}"
                    f"/{config.ratelimit.storage.name if config.ratelimit.storage.name else ''}")
        case _:
            raise IOError("Unknown storage type")


def admin_required():
    """
    Wrapper that performs user tracking and JWT verification\n
    Only accessible by admins.

    :return: Sir, this is a decorator
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            from models.user import User
            user = User.query.filter_by(uuid=get_jwt_identity()).first()
            if user.admin:
                user.is_active(source=fn.__name__, address=request.remote_addr)
                return fn(*args, **kwargs)
            else:
                return response(403, "Forbidden, no rights to access resource")

        return decorator

    return wrapper


def user_required():
    """
    Wrapper that performs user tracking and JWT verification\n
    Accessible by users and admins.

    :return: Sir, this is a decorator
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            from models.user import User
            user = User.query.filter_by(uuid=UUID(get_jwt_identity())).first()
            if user:
                # user.mark_active()
                return fn(*args, **kwargs)
            else:
                return response(403, "Forbidden, no rights to access resource")

        return decorator

    return wrapper
