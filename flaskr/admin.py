from bcrypt import hashpw, gensalt
from sqlalchemy.exc import IntegrityError

from flask import Blueprint, request

from models.user import User
from services.database import database_session
from services.utilities import (admin_required, detailed_response,
                                validate_format, custom_response, response)

from markupsafe import escape
from secrets import token_hex

# Configure blueprint
admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route("/user/add", methods=['POST'])
@admin_required()
def post_admin_user_add():
    """
    Add a user, handling an HTTP POST request. \n
    This creates and adds a user to the database, if valid.

    :return: JSON status response.
    """

    try:
        username: str = request.json.get("username", None)
        name: str = request.json.get("name", None)
        email: str = request.json.get("email", None)
        phone_number: str = request.json.get("phone_number", None)
        postal_code: str = request.json.get("postal_code", None)
        address: str = request.json.get("address", None)

        if not all(isinstance(i, str) for i in [username, name, email, phone_number, postal_code, address]):
            raise ValueError(
                f"Expected str, instead got [{type(username), type(name), type(email), type(phone_number), type(postal_code), type(address)}]")

    except (AttributeError, ValueError) as e:
        return detailed_response(400, "Bad request, see details.", {"error": e.__str__()})

    raw_password = token_hex()

    try:
        new_user = User(
            name=name,
            username=username,
            email=validate_format("email", email) or "invalid@email.com",
            admin=False,
            password=hashpw(raw_password.encode("UTF-8"), gensalt()).decode("UTF-8")
        )

        database_session.add(new_user)
        database_session.commit()

    except IntegrityError as error:
        return custom_response(400, f"Bad request, check details for more info",
                               {"error": error.args[0],
                                "constraint": error.args[0].split(":")[1].removeprefix(" ")})

    return custom_response(201, f"Successfully created user {new_user.username}",
                           {"login": {"uuid": new_user.uuid, "password": raw_password}})


@admin.route("/user/delete/<uuid>", methods=['DELETE'])
@admin_required()
def post_admin_user_delete(uuid: str):
    """
    Deletes a user, handling an HTTP DELETE request.\n
    This deletes a user based on UUID, if they exist.

    :return: JSON status response.
    """

    if not validate_format("uuid", uuid):
        return response(400, "Bad request, given value is not a UUID.")

    count = User.query.filter_by(uuid=uuid).delete()

    if count < 1:
        return response(404, f"User <{escape(uuid)}> not found, unable to delete.")

    database_session.commit()

    return detailed_response(200, f"Successfully deleted {count} user", {"uuid": uuid})
