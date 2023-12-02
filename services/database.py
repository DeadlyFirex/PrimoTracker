from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from services.config import Config

# TODO: Verify if the engine properly works
# TODO: Verify if scoped_session is optimal
config = Config().get()
url_database = (f"{config.database.type}://{config.database.credentials.username}"
                f":{config.database.credentials.password}@{config.database.host}"
                f":{config.database.port}/{config.database.name}")

engine = create_engine(url_database)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # TODO: Verify database integrity
    from models import user, index, audit, transactions
    to_init = [index.TableIndex, index.UUIDIndex, audit.Audit, audit.AuditAction,
               transactions.Transaction, transactions.TransactionType, transactions.SourceType,
               transactions.UsageType, transactions.MaterialType, transactions.ExchangeType, user.User]

    Base.metadata.create_all(bind=engine)

    for model in to_init:
        # TODO: Verify if this works
        # TODO: Verify if committing here is better
        model.__database_init__(db_session=db_session)
        db_session.commit()
