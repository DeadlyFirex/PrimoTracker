from bcrypt import hashpw, gensalt
from sqlalchemy.exc import IntegrityError

from flask import Blueprint

from models.user import User
from services.database import database_session
from services.utilities import response, ResponseType, generate_error, validate_format, validate_input
from services.authentication import admin_required

from markupsafe import escape
from secrets import token_hex
from uuid import UUID

# Configure blueprint
admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route("/user/add", methods=['POST'])
@admin_required()
@validate_input(username=str, name=str, email=str, admin=bool)
def post_admin_user_add(**kwargs):
    """
    Add a user, handling an HTTP POST request. \n
    This creates and adds a user to the database, if valid.

    :return: JSON status response.
    """

    raw_password = token_hex()

    try:
        new_user = User(
            name=(kwargs.get("__name")),
            username=(kwargs.get("__username")),
            email=validate_format("email", kwargs.get("__email")) or "invalid@email.com",
            admin=kwargs.get("__admin"),
            password=hashpw(raw_password.encode("UTF-8"), gensalt()).decode("UTF-8")
        )

        database_session.add(new_user)
        database_session.commit()

    except IntegrityError as error:
        return response(ResponseType.COMPLEX_ERROR, 400, "Bad request, check details",
                        error=generate_error("ADMIN_DATABASE_FAILURE",
                                             f"Generic database error, most likely - constraint failure",
                                             full=escape(error.args.__str__()),
                                             args=[escape(arg) for arg in error.args]))

    return response(ResponseType.RESULT, 201, f"Successfully created user {new_user.username}",
                    result={"uuid": new_user.uuid, "password": raw_password})


@admin.route("/user/delete/<uuid>", methods=['DELETE'])
@admin_required()
def post_admin_user_delete(uuid: str, **kwargs):
    """
    Deletes a user, handling an HTTP DELETE request.\n
    This deletes a user based on UUID, if they exist.

    :return: JSON status response.
    """

    if not validate_format("uuid", uuid):
        return response(ResponseType.ERROR, 400, "Bad request, check details",
                        error=generate_error("REQUEST_FIELD_INVALID_FORMAT", "Invalid UUID format", uuid=uuid))

    count = User.query.filter_by(uuid=UUID(uuid)).delete()

    if count < 1:
        return response(ResponseType.ERROR, 404, f"User <{escape(uuid)}> not found, unable to delete.",
                        error=generate_error("REQUEST_INVALID", "UUID not found", uuid=uuid))

    database_session.commit()

    return response(ResponseType.RESULT, 200, f"Deleted <{count}> user",
                    result={"uuid": uuid, "count": count})
