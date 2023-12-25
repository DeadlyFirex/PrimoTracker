from enum import Enum


class ResponseType(Enum):
    """
    Enum for response types
    """
    RESPONSE = "response"
    DETAILED_RESPONSE = "detailed_response"
    RESULT = "result"
    ERROR = "error"
    COMPLEX_ERROR = "complex_error"


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
