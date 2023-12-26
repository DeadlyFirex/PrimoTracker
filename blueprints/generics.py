from flask import Blueprint, current_app

from services.response import response, ResponseType
from services.configuration import Config

# Configure blueprint
generics = Blueprint('generics', __name__, url_prefix='/')
cfg = Config()


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

    return response(ResponseType.DETAILED_RESPONSE, 301, "ok", link=cfg.server.version)
