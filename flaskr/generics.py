from flask import Blueprint

from services.config import Config
from services.utilities import response, ResponseType

# Configure blueprint
config = Config().get()
generics = Blueprint('generics', __name__, url_prefix='/')


@generics.route("/health", methods=['GET'])
def get_generics_health():
    """
    Simply checks the connection status and if the application exists.

    :return: JSON status response.
    """

    return response(code=200, msg="ok")


@generics.route("/version", methods=['GET'])
def get_generics_version():
    """
    Gets the current running version from the configuration, and uses it.

    :return: JSON detailed status response with (link/version) data.
    """

    return response(ResponseType.DETAILED_RESPONSE, 301, "ok", link=config.server.version)
