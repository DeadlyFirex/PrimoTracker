import blueprints.schemas.user as schemas

from flask import Blueprint

from models.user import User, UserSchema
from services.response import response, ResponseType
from services.authentication import user_required
from services.validation import validate_request

from markupsafe import escape
from uuid import UUID

# Configure blueprint
user = Blueprint('user', __name__, url_prefix='/user')
user_schema = UserSchema()


@user.route("/<uuid>", methods=['GET'])
@user_required()
@validate_request(query=schemas.UserGetQuerySchema())
def get_user_by_uuid(uuid, **kwargs):
    """
    Gets a single user by UUID and returns public information about them.

    :return: JSON result response with (user) data.
    """
    argument_user = User.query.filter_by(uuid=UUID(uuid)).first()

    if argument_user is None:
        return response(ResponseType.ERROR, 404, f"User <{escape(uuid)}> not found.")

    return response(ResponseType.RESULT, 200, "Fetched user successfully",
                    result=user_schema.dump(argument_user))


@user.route("/all", methods=['GET'])
@user_required()
def get_user_all(**kwargs):
    """
    Get all users and returns public information about them.

    :return: JSON result response with a (list of users) data.
    """
    users = User.query.all()

    if len(users) <= 0:
        return response(ResponseType.ERROR, 404, "No users were found.")

    return response(ResponseType.RESULT, 200, f"Successfully fetched {len(users)} users",
                    result=user_schema.dump(users, many=True))
