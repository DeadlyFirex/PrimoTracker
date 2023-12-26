from config import (Configuration, ConfigurationSet, EnvConfiguration,
                    TOMLConfiguration, JSONConfiguration)

from json import load
from os import listdir
from os.path import abspath, join, dirname, exists, isfile
from secrets import token_hex

# Get the absolute path of the config file
root_path = abspath(join(dirname(abspath(__file__)), '..'))


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Config(ConfigurationSet, metaclass=SingletonMeta):
    def __init__(self, sources: Configuration = None, app_name: str = None,
                 config_path: str = join(root_path, "config.json"),
                 secrets_path: str = join(root_path, "secrets.toml"),
                 validate: bool = True) -> None:
        self._path: str = config_path
        self._secrets: str = secrets_path
        self._raw: dict = load(open(self._path, 'r')) if exists(self._path) else None
        self._root: str = dirname(self._path)
        self._sources: list = [self._path, ]
        self._id: str = token_hex(8)

        if not isfile(self._path) or not isfile(self._secrets):
            raise FileNotFoundError(f"Failure to find configuration not found at {NotImplemented}")

        self._config_folder: str = abspath(join(self._root, self._raw.get("path").get("configuration")))
        self._name: str = app_name if app_name is not None else self._raw.get("application").get("name")

        if sources is None:
            for f in listdir(self._config_folder):
                if f.endswith(".json"):
                    self._sources.append(join(self._config_folder, f))

        self._validate_configuration() if validate else None

        super().__init__(
            EnvConfiguration(self._name.upper(), separator="_", lowercase_keys=True),
            TOMLConfiguration(self._secrets, True),
            *[JSONConfiguration(source, True) for source in self._sources]
        )

    def _validate_configuration(self) -> bool:
        pass
