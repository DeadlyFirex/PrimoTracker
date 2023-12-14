from flask import Flask
from python_json_config import config_node

from services.config import Config
from services.database import verify_database
from services.utilities import generate_database_url

from secrets import token_hex


def create_app(config: config_node.Config = Config().get()) -> Flask:
    app = Flask(config.application.name)

    # Setup configuration
    app.config.from_mapping(
        NAME=config.application.name,
        DEBUG=config.application.debug,
        SECRET_KEY=token_hex(),
        DATABASE=generate_database_url(),
        SQLALCHEMY_DATABASE_URI=generate_database_url(),
        JWT_SECRET_KEY=token_hex(),
    )

    # Register JWT / Limiter / Marshmallow
    from services.authentication import jwt
    jwt.init_app(app)

    from services.limits import limiter
    limiter.init_app(app)

    # Configure blueprints/views and ratelimiting
    from flaskr import admin, auth, generics, user
    for limit, endpoint in [(config.ratelimit.limits.admin, admin.admin),
                            (config.ratelimit.limits.authentication, auth.auth),
                            (config.ratelimit.limits.default, generics.generics),
                            (config.ratelimit.limits.user, user.user)]:
        for counter in limit:
            limiter.limit(counter)(endpoint)
        app.register_blueprint(endpoint)

    from services.database import ma
    ma.init_app(app)

    # Check database status
    verify_database()

    return app


if __name__ == "__main__":
    from sys import argv
    app_config = Config(path=argv[1] if len(argv) > 1 else None).get()

    create_app().run(app_config.server.host, app_config.server.port, app_config.server.debug)
