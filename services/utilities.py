from typing import Union

from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from flask import request

from secrets import choice
from functools import wraps
from uuid import UUID
from re import match

from services.config import Config
from datetime import datetime
from uuid import UUID

config = Config().get()


class Utilities:

    @staticmethod
    def generate_secret(length=config.security.secret_length):
        """
        Creates a secret-key based on the character-set passed by the configuration.
        Returns a string.

        :return: String, secret-key
        """
        return ''.join(choice(config.security.character_list) for _ in range(length))

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def calculate_time(start: datetime, end: datetime = datetime.now()):
        """
        Calculates time difference in milliseconds.\n
        Returns the result in two decimal rounded string.

        :param start: Start datetime object
        :param end: End datetime object
        :return: Time difference in milliseconds, string.
        """
        return f"{round((end - start).total_seconds() * 1000, 2)}ms"

    @staticmethod
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

    @staticmethod
    def flatten_json(input_dict: dict) -> dict:
        """
        Flatten a nested JSON dictionary and return a list of unique values.
        :param input_dict: Nested JSON dictionary
        :return: Flattened dictionary
        """
        result_dict = {}

        for key, inner_dict in input_dict.items():
            result_dict[key] = list(set(value for sublist in inner_dict.values() for value in sublist))

        return result_dict

    @staticmethod
    def convert_json(input_json: dict, values_only: bool = False) -> Union[dict, list]:
        """
        Converts a nested JSON dictionary to its keys.
        :param input_json: Nested JSON dictionary
        :param values_only: Convert to list of values
        :return: Flattened dictionary, or list of values
        """
        output_json = {}
        for key, value in input_json.items():
            output_json[key] = list(value.keys())

        if values_only:
            output_list = []
            for category, subcategories in input_json.items():
                output_list.extend(subcategories.keys())
            return output_list

        return output_json


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
                return Utilities.response(403, "Forbidden, no rights to access resource")
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
                user.is_active(source=fn.__name__, address=request.remote_addr)
                return fn(*args, **kwargs)
            else:
                return Utilities.response(403, "Forbidden, no rights to access resource")
        return decorator
    return wrapper
