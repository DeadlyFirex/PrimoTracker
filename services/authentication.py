from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, JWTManager

from services.response import response, ResponseType, generate_error

from functools import wraps
from uuid import UUID

jwt = JWTManager()


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
