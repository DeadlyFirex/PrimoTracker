from python_json_config import ConfigBuilder
from python_json_config.validators import is_unreserved_port


class Config:
    def __init__(self, path: str = "./config.json", validate: bool = True,
                 builder: ConfigBuilder = ConfigBuilder()):
        self.path = path
        self.builder = builder
        self.config = None

        if validate:
            for field, field_type in {"server.host": str, "server.port": int, "server.version": str}.items():
                self.builder.validate_field_type(field, field_type)
            self.builder.validate_field_value('server.port', is_unreserved_port)

        # Parse if all valid
        self.config = self.builder.parse_config(self.path)

    def get(self):
        self.config = self.builder.parse_config(self.path)
        return self.config


class ExtendedConfig:
    # TODO: Figure out a better way to do this
    def __init__(self, path: str, builder: ConfigBuilder = ConfigBuilder()):
        self.path = path
        self.builder = builder
        self.config = self.builder.parse_config(self.path)

    def get(self):
        self.config = self.builder.parse_config(self.path)
        return self.config
