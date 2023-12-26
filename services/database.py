from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from flask_marshmallow import Marshmallow

from services.configuration import Config, root_path
from utilities.helpers import generate_url

from uuid import uuid4, UUID
from json import load
from logging import getLogger
from os.path import join, abspath

config = Config()
logger = getLogger(config.application.name)
index_data = load(open(abspath(join(root_path, config.path.init.index)), "r"))
initialized = False

database_url = generate_url("database", config.database)
engine = create_engine(database_url, pool_size=config.database.pool.min, max_overflow=config.database.pool.max,
                       pool_pre_ping=config.database.pool.pre_ping, pool_recycle=config.database.pool.recycle,
                       pool_timeout=config.database.pool.timeoutMilliseconds)

Base = declarative_base()
database_session = scoped_session(sessionmaker(autoflush=True, bind=engine))
Base.query = database_session.query_property()
index_session = scoped_session(sessionmaker(autoflush=True, bind=engine))
ma = Marshmallow()


def generate_uuid(table_name: str = None,
                  session: scoped_session = index_session, init: bool = True):
    from models.index import UUIDIndex
    attempt = 0

    while attempt < config.database.uuid.max_attempts:
        unique_uuid = uuid4()
        table_uuid = None

        if config.database.type == "memory":
            session = database_session

        if UUIDIndex.query.filter_by(table_uuid=unique_uuid).first():
            continue

        for entry in index_data[config.database.table.table_index]:
            if entry["name"] == table_name:
                table_uuid = UUID(entry["uuid"])

        if not table_uuid:
            raise Exception("table_name invalid")

        session.add(UUIDIndex(uuid=unique_uuid, table_name=table_name, table_uuid=table_uuid))
        session.commit() if init else None

        return unique_uuid
    raise Exception(f"Could not generate unique UUID after {config.database.uuid.max_attempts} attempts")


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
    except (OperationalError, ProgrammingError):
        initialize_database()
        logger.warning(" = Performing new database initialization.")
    finally:
        globals()["initialized"] = True


def initialize_database():
    # TODO: Verify database integrity
    from models import user, index, audit, transactions
    init_config = config.path.init
    to_init = [(index.TableIndex, init_config.index), (index.UUIDIndex, init_config.index),
               (audit.Audit, init_config.audit), (audit.AuditAction, init_config.audit),
               (transactions.TransactionType, init_config.transactions),
               (transactions.Transaction, init_config.transactions),
               (transactions.SourceType, init_config.transactions), (transactions.UsageType, init_config.transactions),
               (transactions.MaterialType, init_config.transactions),
               (transactions.ExchangeType, init_config.transactions),
               (user.User, init_config.users)]

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    Base.metadata.reflect(bind=engine)

    # TODO: Verify this function
    for model, init in to_init:
        model.__database_init__(session=database_session, init=abspath(join(root_path, init)))
        if model in [index.UUIDIndex, index.TableIndex]:
            database_session.commit()

    Base.metadata.reflect(bind=engine)
    database_session.commit()
