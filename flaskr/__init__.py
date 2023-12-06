from flask import Flask
from flask_limiter import Limiter
from flask_jwt_extended import JWTManager
from flask_limiter.util import get_remote_address
from sqlalchemy.exc import OperationalError

from flaskr import admin, auth, generics, user
from services.config import Config
from services.database import initialize_database
from services.utilities import generate_secret, generate_database_url, generate_storage_url

from secrets import token_hex

# Get configuration, create Flask application
config = Config().get()


def create_app():
    app = Flask(config.application.name)

    # Setup configuration
    app.config.from_mapping(
        DEBUG=config.application.debug,
        SECRET_KEY=token_hex(),
        DATABASE=generate_database_url(),
        SQLALCHEMY_DATABASE_URI=generate_database_url(),
        JWT_SECRET_KEY=token_hex(),
    )

    # Configure blueprints/views and ratelimiting
    # TODO: Make every limit configurable
    limiter = Limiter(get_remote_address,
                      app=app,
                      enabled=config.ratelimit.enabled,
                      default_limits=config.ratelimit.limits.default,
                      storage_uri=generate_storage_url(),
                      headers_enabled=config.ratelimit.headers
                      )

    for limit, endpoint in [(config.ratelimit.limits.admin, admin.admin),
                            (config.ratelimit.limits.authentication, auth.auth),
                            (config.ratelimit.limits.default, generics.generics),
                            (config.ratelimit.limits.user, user.user)]:
        for counter in limit:
            limiter.limit(counter)(endpoint)
        app.register_blueprint(endpoint)

    # Register JWT
    JWTManager(app).init_app(app)

    # Check database status
    # TODO: Improve this function to be more flexible.
    def first_time_run():
        from models import user, index, audit
        attempted = False
        if config.database.type == "memory":
            app.logger.warning("Warning: You are using a memory database. "
                               "Most functions besides starting will not function properly."
                               "Do NOT use this in production.")
        app.logger.info("Checking for database initialization.")

        try:
            if any(not table.query.all() for table in [user.User, audit.AuditAction, index.UUIDIndex]):
                initialize_database()
                attempted = True
                app.logger.info("Performing new database initialization or repopulating tables.")
        except OperationalError:
            if not attempted:
                initialize_database()
            app.logger.info("Performing new database initialization.")

    first_time_run()

    return app


if __name__ == "__main__":
    create_app().run(config.server.host, config.server.port, config.server.debug)
