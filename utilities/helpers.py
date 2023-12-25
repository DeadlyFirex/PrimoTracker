from sqlalchemy import URL

from services.configuration import Config

from datetime import datetime
from typing import Union


def calculate_time(start: datetime, end: datetime = datetime.now()) -> float:
    """
    Calculates time difference in milliseconds.\n
    Returns the result in two decimal rounded string.

    :param start: Start datetime object
    :param end: End datetime object
    :return: Time difference in milliseconds, string.
    """
    return round((end - start).total_seconds() * 1000, 2)


def generate_url(url_type: str, db_config: Config, force_string: bool = False) -> Union[URL, str]:
    if url_type not in ["database", "storage"]:
        raise ValueError(f"Invalid url_type <{url_type}>")
    storage_type = db_config.type

    to_assign = [(db_config.host, "host"), (db_config.port, "port"),
                 (db_config.name, "database"), (db_config.credentials.username, "username"),
                 (db_config.credentials.password, "password")]
    for value, name in to_assign:
        locals()[name] = value if value != "" else None

    if storage_type == "memory":
        return "sqlite:///:memory:" if url_type == "database" else "memory://"
    elif storage_type == "sqlite" and url_type == "database":
        return f"{db_config.type}:///{db_config.host}"
    else:
        url = URL.create(
            drivername=storage_type,
            username=locals()["username"],
            password=locals()["password"],
            host=locals()["host"],
            port=locals()["port"],
            database=locals()["database"]
        )
        return url if not force_string else url.render_as_string(False)
