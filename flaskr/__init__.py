from flask import Flask
from flask_limiter import Limiter
from flask_jwt_extended import JWTManager
from flask_limiter.util import get_remote_address
from sqlalchemy.exc import OperationalError

from flaskr import admin, auth, generics, user
from services.config import Config
from services.database import init_db, url_database
from services.utilities import Utilities

from os import system as os_system

# Get configuration, create Flask application
config = Config().get()


def create_app():
    app = Flask(config.application.name)

    # Set host configuration
    os_system(f"set FLASK_RUN_HOST={config.server.host}")
    os_system(f"set FLASK_RUN_PORT={config.server.port}")

    # Setup configuration
    app.config.from_mapping(
        DEBUG=config.application.debug,
        SECRET_KEY=Utilities.generate_secret(),
        DATABASE=url_database,
        SQLALCHEMY_DATABASE_URI=url_database,
        JWT_SECRET_KEY=Utilities.generate_secret(),
        RATELIMIT_ENABLED=True
    )

    # Configure blueprints/views and ratelimiting
    # TODO: Make every limit configurable
    limiter = Limiter(get_remote_address,
                      app=app,
                      default_limits=[config.ratelimiting.default],
                      storage_uri=f"{config.database.type}://{config.database.credentials.username}"
                                  f":{config.database.credentials.password}@{config.database.host}"
                                  f":{config.database.port}",
                      enabled=True,
                      headers_enabled=True
                      )

    limiter.limit(config.ratelimiting.default)(admin.admin)
    limiter.limit(config.ratelimiting.authorization)(auth.auth)
    limiter.limit(config.ratelimiting.default)(generics.generics)
    limiter.limit(config.ratelimiting.default)(user.user)

    app.register_blueprint(admin.admin)
    app.register_blueprint(auth.auth)
    app.register_blueprint(generics.generics)
    app.register_blueprint(user.user)

    # Register JWT
    JWTManager(app).init_app(app)

    # Check database status
    # TODO: Improve this function to be more flexible.
    def first_time_run():
        from models import user, index, audit
        app.logger.info("Checking for database initialization.")

        try:
            result = (user.User.query.all(), audit.AuditAction.query.all(), index.UUIDIndex.query.all())
        except OperationalError:
            init_db()
            app.logger.info("Performing new database initialization.")
            return
        if result in [None, []]:
            init_db()
            app.logger.info("Repopulating database tables.")
            return
        app.logger.info("Finished checking, no new initialization required.")

    first_time_run()

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {"status": 429, "message": f"Exceeded ratelimit: {e.description}"}, 429

    @app.errorhandler(422)
    def ratelimit_handler(e):
        return {"status": 422, "message": f"Unable to verify token, probably due to restart: {e.description}"}, 422

    return app


if __name__ == "__main__":
    create_app().run(config.server.host, config.server.port, config.server.debug)
