from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from flask_marshmallow import Marshmallow

from services.config import Config, ExtendedConfig
from services.utilities import generate_database_url

from uuid import uuid4, UUID
from json import load
from logging import getLogger

config = Config().get()
logger = getLogger(config.application.name)
db_config = ExtendedConfig(path=config.configuration.database_path).get()
index_data = load(open(config.initialization.index_path, "r"))

engine = create_engine(generate_database_url())
ma = Marshmallow()

Base = declarative_base()
database_session = scoped_session(sessionmaker(autoflush=True, bind=engine))
Base.query = database_session.query_property()
index_session = scoped_session(sessionmaker(autoflush=True, bind=engine))


def generate_uuid(table_name: str, session: scoped_session = index_session, init: bool = True):
    from models.index import UUIDIndex
    attempt = 0

    while attempt < db_config.uuid.max_attempts:
        unique_uuid = uuid4()
        table_uuid = None

        if config.database.type == "memory":
            session = database_session

        if UUIDIndex.query.filter_by(table_uuid=unique_uuid).first():
            continue

        for entry in index_data[db_config.table_names.table_index]:
            if entry["name"] == table_name:
                table_uuid = UUID(entry["uuid"])

        if not table_uuid:
            raise Exception("table_name invalid")

        session.add(UUIDIndex(uuid=unique_uuid, table_name=table_name, table_uuid=table_uuid))
        if init:
            session.commit()

        return unique_uuid
    raise Exception(f"Could not generate unique UUID after {db_config.uuid_max_attempts} attempts")


def verify_database():
    from models import user, index, audit

    if config.database.type == "memory":
        logger.warning("Warning: You are using a memory database.\n"
                       "Most functions besides starting will not function properly.\n"
                       "Do NOT use this in production.")
    logger.info(" - Checking for database initialization.")

    try:
        if any(not table.query.all() for table in [user.User, audit.AuditAction, index.UUIDIndex]):
            initialize_database()
            logger.warning(" = Performing new database initialization.")
        else:
            logger.warning(" * Database does not need initialization.")
    except OperationalError:
        initialize_database()
        logger.warning(" = Performing new database initialization.")


def initialize_database():
    # TODO: Verify database integrity
    from models import user, index, audit, transactions
    to_init = [index.TableIndex, index.UUIDIndex, audit.Audit, audit.AuditAction,
               transactions.Transaction, transactions.TransactionType, transactions.SourceType,
               transactions.UsageType, transactions.MaterialType, transactions.ExchangeType, user.User]

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    Base.metadata.reflect(bind=engine)

    # TODO: Verify this function
    for model in to_init:
        model.__database_init__(session=database_session)
        if model in [index.UUIDIndex, index.TableIndex]:
            database_session.commit()

    Base.metadata.reflect(bind=engine)
    database_session.commit()
