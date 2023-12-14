from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from services.config import Config
from services.utilities import generate_storage_url

config = Config().get()

limiter = Limiter(
    key_func=get_remote_address,
    enabled=config.ratelimit.enabled,
    default_limits=config.ratelimit.limits.default,
    storage_uri=generate_storage_url(),
    headers_enabled=config.ratelimit.headers
)
