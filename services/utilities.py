from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from services.config import Config

from typing import Union
from functools import wraps
from re import match
from datetime import datetime
from uuid import UUID
from enum import Enum

config = Config().get()


class ResponseType(Enum):
    """
    Enum for response types
    """
    RESPONSE = "response"
    DETAILED_RESPONSE = "detailed_response"
    RESULT = "result"
    ERROR = "complex_error"


def response(response_type: ResponseType = ResponseType.RESPONSE,
             code: int = 200, msg: str = "This is a message", **kwargs):
    """
    Generates an JSON response.
    Returns a dictionary.

    :return: Dictionary
    """
    return {
        "code": code,
        "msg": msg,
        "type": response_type.name.lower(),
        **kwargs
    }, code


def generate_error(error_type: str = "UNKNOWN", msg: str = "No details given.", **kwargs):
    """
    Generates an JSON response.
    Returns a dictionary.

    :return: Dictionary
    """
    return {
        "error": error_type,
        "msg": msg,
        "details": {
            **kwargs
        }
    }


def calculate_time(start: datetime, end: datetime = datetime.now()) -> float:
    """
    Calculates time difference in milliseconds.\n
    Returns the result in two decimal rounded string.

    :param start: Start datetime object
    :param end: End datetime object
    :return: Time difference in milliseconds, string.
    """
    return round((end - start).total_seconds() * 1000, 2)


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


def validate_input(**expected_args):
    def decorator(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            json_object = request.get_json(silent=True)

            if json_object is None:
                return response(ResponseType.ERROR, 400, "Bad request, check details",
                                error=generate_error("REQUEST_JSON_INVALID", "No JSON object found"))

            error_object = [error for error in [
                generate_error("REQUEST_JSON_FIELD_INVALID", f"Field {arg} expected, but not found", field=arg)
                if arg not in json_object else
                generate_error("REQUEST_JSON_TYPE_INVALID",
                               f"Expected str, instead got {type(json_object[arg])} for field <{arg}>",
                               field=arg, expected=f"{expected_args[arg]}", received=f"{type(json_object[arg])}")
                if not isinstance(json_object[arg], expected_args[arg]) else None
                for arg in expected_args
            ] if error is not None]

            if error_object:
                response(ResponseType.ERROR, 400,"Bad request, check details", error=error_object)

            for key, value in json_object.items():
                kwargs[f"__{key}"] = value

            return fn(*args, **kwargs)

        return decorated_function

    return decorator


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
            user = User.query.filter_by(uuid=UUID(get_jwt_identity())).first()
            if user.admin:
                kwargs["*jwt_user"] = user
                return fn(*args, **kwargs)
            else:
                return response(ResponseType.ERROR, 403, "Forbidden, no rights to access resource",
                                error=generate_error("REQUEST_FORBIDDEN",
                                                     "Forbidden, no rights to access resource"))

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
                kwargs["*jwt_user"] = user
                return fn(*args, **kwargs)
            else:
                return response(ResponseType.ERROR, 401, "Unauthorized, no rights to access resource",
                                error=generate_error("REQUEST_UNAUTHORIZED",
                                                     "Unauthorized, no rights to access resource"))

        return decorator

    return wrapper
