from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from services.config import Config, ExtendedConfig

from uuid import uuid4

# TODO: Verify if the engine properly works
# TODO: Verify if scoped_session is optimal

config = Config().get()
db_config = ExtendedConfig(path=config.configuration.database_path).get()

engine = create_engine(f"{config.database.type}://{config.database.credentials.username}"
                       f":{config.database.credentials.password}@{config.database.host}"
                       f":{config.database.port}/{config.database.name}")
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))


def gen_uuid(table_name=None):
    import models.index as index
    attempt = 0

    while attempt < db_config.uuid.max_attempts:
        unique_uuid = uuid4()
        if not index.UUIDIndex.query.filter_by(table_uuid=unique_uuid).first():
            obj = index.TableIndex.query.filter_by(name=table_name).first()

            if obj is not None:
                db_session.add(index.UUIDIndex(uuid=unique_uuid, table_name=obj.name, table_uuid=obj.uuid))
                db_session.commit()
            return unique_uuid
        attempt += 1
    raise Exception(f"Could not generate unique UUID after { db_config.uuid_max_attempts} attempts")
