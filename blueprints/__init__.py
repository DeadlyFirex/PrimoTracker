from flask import Flask

from services.configuration import Config, root_path

from secrets import token_hex
from os.path import join


def create_app(config: str = join(root_path, "config.json"),
               secrets: str = join(root_path, "secrets.toml")) -> Flask:
    config = Config(config_path=config, secrets_path=secrets)
    app = Flask(config.application.name)

    from services.database import database_url
    # Setup configuration
    app.config.from_mapping(
        NAME=config.application.name,
        DEBUG=config.server.debug,
        SECRET_KEY=token_hex(),
        DATABASE=database_url,
        SQLALCHEMY_DATABASE_URI=database_url,
        JWT_SECRET_KEY=token_hex(),
        CONFIG=config
    )

    # Register JWT / Limiter / Marshmallow
    from services.authentication import jwt
    jwt.init_app(app)

    from services.limits import limiter
    limiter.init_app(app)

    # Configure blueprints/views and ratelimiting
    from blueprints import admin, auth, generics, user
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
    from services.database import verify_database
    verify_database()

    return app


if __name__ == "__main__":
    from sys import argv
    app_config = Config(config_path=argv[1] if len(argv) > 1 else None)

    create_app().run(app_config.server.host, app_config.server.port, app_config.server.debug)
