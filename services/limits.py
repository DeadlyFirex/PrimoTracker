from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from services.configuration import Config
from utilities.helpers import generate_url

config = Config()

limiter = Limiter(
    key_func=get_remote_address,
    enabled=config.ratelimit.enabled,
    default_limits=config.ratelimit.limits.default,
    storage_uri=generate_url("storage", config.ratelimit, True),
    headers_enabled=config.ratelimit.headers
)
