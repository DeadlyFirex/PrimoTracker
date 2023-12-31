from flask import Blueprint, request
from flask_jwt_extended import create_access_token, get_jwt_identity

from models.user import User

from services.config import Config
from services.database import database_session
from services.utilities import admin_required, user_required, response, detailed_response, custom_response

from datetime import timedelta
from bcrypt import checkpw
from uuid import UUID

# Configure blueprint
auth = Blueprint('auth', __name__, url_prefix='/auth')
config = Config().get()


@auth.route("/login", methods=['POST'])
def post_auth_login():
    """
    Logs a user in.\n
    Returns a ``JWT`` token for authentication.

    :return: JSON detailed status response with (login) data.
    """
    try:
        username = request.json.get("username", None)
        password = request.json.get("password", None)

        if not isinstance(username, str):
            raise ValueError(f"Expected str, instead got {type(username)} for field <username>")
        if not isinstance(password, str):
            raise ValueError(f"Expected str, instead got {type(password)} for field <password>")

    except (AttributeError, ValueError) as e:
        return detailed_response(400, "Bad request, see details.", {"error": e.__str__()})

    user = User.query.filter_by(username=username).first()

    if user is None or checkpw(password.encode("UTF-8"), user.password.encode("UTF-8")) is False:
        return response(401, "Unauthorized, wrong username/password")

    lifetime = timedelta(seconds=config.security.token_lifetime)
    user.token = create_access_token(identity=user.uuid, fresh=False, expires_delta=lifetime,
                                     additional_claims={"username": user.username, "admin": user.admin})
    database_session.commit()

    user.mark_active(session=database_session)

    return custom_response(200, f"Successfully logged in as {user.username}",
                           {"login": {"uuid": user.uuid, "token": user.token,
                                      "lifetime": lifetime.total_seconds()}})


@auth.route("/test", methods=['GET'])
@user_required()
def get_auth_test():
    """
    Simply checks if you're properly logged in.

    :return: JSON status response.
    """
    current_user = User.query.filter_by(uuid=UUID(get_jwt_identity())).first()

    if current_user is None:
        return response(401, "Unauthorized")

    return custom_response(200, f"Logged in as {current_user.username}",
                           {"login": {"uuid": current_user.uuid, "admin": current_user.admin}})


@auth.route("/admin/test", methods=['GET'])
@admin_required()
def get_auth_admin_test():
    """
    Simply checks if you're properly logged in as an administrator.

    :return: JSON status response.
    """
    current_user = User.query.filter_by(uuid=get_jwt_identity()).first()

    if current_user is None:
        return response(401, "Unauthorized")

    return custom_response(200, f"Logged in as {current_user.username}",
                           {"login": {"uuid": current_user.uuid, "admin": current_user.admin}})
