from flask import Blueprint

from services.config import Config
from services.utilities import Utilities

# Configure blueprint
config = Config().get()
generics = Blueprint('generics', __name__, url_prefix='/')


@generics.route("/health", methods=['GET'])
def get_generics_health():
    """
    Simply checks the connection status and if the application exists.

    :return: JSON status response.
    """

    return Utilities.response(200, "ok")


@generics.route("/version", methods=['GET'])
def get_generics_version():
    """
    Gets the current running version from the configuration, and uses it.

    :return: JSON detailed status response with (link/version) data.
    """

    return Utilities.detailed_response(301, "ok", {"link": config.server.version})


@generics.route("/ping", methods=['GET'])
def get_generics_ping():
    """
    Returns a 204, no content to the sender. Exempt from limiters.

    :return: Nothing.
    """

    return "", 204
