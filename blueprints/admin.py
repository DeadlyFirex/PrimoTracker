import blueprints.schemas.admin as schemas

from sqlalchemy.exc import IntegrityError
from flask import Blueprint

from models.user import User, UserBodySchema, UserFullSchema
from services.database import database_session
from services.response import response, ResponseType, generate_error
from services.authentication import admin_required
from services.validation import validate_request

from markupsafe import escape
from secrets import token_hex
from uuid import UUID
from bcrypt import hashpw, gensalt

# Configure blueprint
admin = Blueprint('admin', __name__, url_prefix='/admin')
user_full_schema = UserFullSchema()
user_body_schema = UserBodySchema()


@admin.route("/user/add", methods=['POST'])
@admin_required()
@validate_request(body=user_body_schema)
def post_admin_user_add(**kwargs):
    """
    Add a user, handling an HTTP POST request. \n
    This creates and adds a user to the database, if valid.

    :return: JSON status response.
    """

    raw_password = token_hex()
    body = kwargs.get("*body")

    try:
        new_user = User(
            name=(body.get("name")),
            username=(body.get("username")),
            email=body.get("email"),
            admin=body.get("admin"),
            password=hashpw(raw_password.encode("UTF-8"), gensalt()).decode("UTF-8"),
            country=body.get("country"),
            tags=body.get("tags")
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


@admin.route("/user/<uuid>", methods=['GET'])
@admin_required()
@validate_request(query=schemas.AdminUserGetQuerySchema(), path=schemas.AdminUserGetPathSchema())
def get_admin_user(uuid: str, **kwargs):
    """
    Get a user, handling an HTTP GET request. \n
    This gets a user based on UUID, if they exist.

    :return: JSON status response.
    """
    user = User.query.filter_by(uuid=UUID(uuid)).first()

    if not user:
        return response(ResponseType.ERROR, 404, f"User <{escape(uuid)}> not found",
                        error=generate_error("REQUEST_INVALID", "UUID not found", uuid=uuid))

    return response(ResponseType.RESULT, 200, f"Successfully retrieved user {user.username}",
                    result=user_full_schema.dump(user))


@admin.route("/user/delete/<uuid>", methods=['DELETE'])
@admin_required()
@validate_request(query=schemas.AdminUserDeleteQuerySchema(), path=schemas.AdminUserDeletePathSchema())
def post_admin_user_delete(uuid: str, **kwargs):
    """
    Deletes a user, handling an HTTP DELETE request.\n
    This deletes a user based on UUID, if they exist.

    :return: JSON status response.
    """
    count = User.query.filter_by(uuid=UUID(uuid)).delete()

    if count < 1:
        return response(ResponseType.ERROR, 404, f"User <{escape(uuid)}> not found, unable to delete.",
                        error=generate_error("REQUEST_INVALID", "UUID not found", uuid=uuid))

    database_session.commit()

    return response(ResponseType.RESULT, 200, f"Deleted <{count}> user",
                    result={"uuid": uuid, "count": count})
