from flask import Blueprint
from flask_jwt_extended import get_jwt_identity

from models.user import User
from services.utilities import validate_format, user_required, response, ResponseType

from markupsafe import escape
# Configure blueprint
user = Blueprint('user', __name__, url_prefix='/user')


@user.route("/<uuid>", methods=['GET'])
@user_required()
def get_user_by_uuid(uuid):
    """
    Gets a single user by UUID and returns public information about them.

    :return: JSON result response with (user) data.
    """
    if not validate_format("uuid", uuid):
        return response(ResponseType.ERROR, 400, "Expected UUID, received something else.")

    current_user = User.query.filter_by(uuid=get_jwt_identity()).first()

    if current_user is None:
        return response(ResponseType.ERROR, 401, "Unauthorized")

    argument_user = User.query.filter_by(uuid=uuid).first()

    if argument_user is None:
        return response(ResponseType.ERROR, 404, f"User <{escape(uuid)}> not found.")

    return response(ResponseType.RESULT, 200, "Fetched user successfully",
                    result={"uuid": argument_user.uuid, "name": argument_user.name, "username": argument_user.username,
                            "country": argument_user.country, "admin": argument_user.admin, "tags": argument_user.tags,
                            "active": argument_user.active})


@user.route("/all", methods=['GET'])
@user_required()
def get_user_all():
    """
    Get all users and returns public information about them.

    :return: JSON result response with a (list of users) data.
    """
    current_user = User.query.filter_by(uuid=get_jwt_identity()).first()

    if current_user is None:
        return response(ResponseType.ERROR, 401, "Unauthorized")

    fetched_users = User.query.all()

    if fetched_users is None or []:
        return response(ResponseType.ERROR, 404, "No users were found.")

    result = []

    for fetched_user in fetched_users:
        result.append({"uuid": fetched_user.uuid, "name": fetched_user.name, "username": fetched_user.username,
                       "country": fetched_user.country, "admin": fetched_user.admin, "tags": fetched_user.tags,
                       "active": fetched_user.active})

    return response(ResponseType.RESULT, 200, f"Successfully fetched {len(result)} users", result=result)
