import blueprints.schemas.auth as schemas

from flask import Blueprint
from flask_jwt_extended import create_access_token

from models.user import User
from services.database import database_session
from services.response import response, ResponseType
from services.validation import validate_request
from services.authentication import user_required, admin_required
from services.configuration import Config

from datetime import timedelta
from bcrypt import checkpw

# Configure blueprint
auth = Blueprint('auth', __name__, url_prefix='/auth')
cfg = Config()


@auth.route("/login", methods=['POST'])
@validate_request(body=schemas.AuthLoginBodySchema())
def post_auth_login(**kwargs):
    """
    Logs a user in.\n
    Returns a ``JWT`` token for authentication.

    :return: JSON detailed status response with (login) data.
    """
    body = kwargs.get("*body")
    user = User.query.filter_by(username=(body.get("username"))).first()

    if user is None or checkpw(body.get("password").encode("UTF-8"), user.password.encode("UTF-8")) is False:
        return response(ResponseType.ERROR, 401, "Unauthorized, wrong username/password")

    lifetime = timedelta(seconds=cfg.security.token.lifetime)
    user.token = create_access_token(identity=user.uuid, fresh=False, expires_delta=lifetime,
                                     additional_claims={"username": user.username, "admin": user.admin})
    database_session.commit()

    user.mark_active(session=database_session)

    return response(ResponseType.RESULT, 200, f"Logged in as {user.username}",
                    login={"uuid": user.uuid, "username": user.username,
                           "token": user.token, "lifetime": lifetime.total_seconds()})


@auth.route("/test", methods=['GET'])
@user_required()
def get_auth_test(**kwargs):
    """
    Simply checks if you're properly logged in.

    :return: JSON status response.
    """
    current_user = kwargs.get("*jwt_user")

    return response(ResponseType.DETAILED_RESPONSE, 200, f"Logged in as {current_user.username}",
                    login={"uuid": current_user.uuid, "admin": current_user.admin})


@auth.route("/admin/test", methods=['GET'])
@admin_required()
def get_auth_admin_test(**kwargs):
    """
    Simply checks if you're properly logged in as an administrator.

    :return: JSON status response.
    """
    current_user = kwargs.get("__user")

    return response(ResponseType.DETAILED_RESPONSE, 200, f"Logged in as {current_user.username}",
                    login={"uuid": current_user.uuid, "admin": current_user.admin})
