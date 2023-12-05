from sqlalchemy import DateTime, Column, String, Integer, Uuid, ForeignKey
from sqlalchemy.orm import scoped_session

from services.database import Base
from services.config import ExtendedConfig, Config

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

config = Config().get()
db_config = ExtendedConfig(path=config.configuration.database_path).get()


@dataclass
class UUIDIndex(Base):
    __tablename__ = db_config.table_names.uuid_index
    __child_name__ = db_config.table_names.table_index

    id: int = Column(Integer, primary_key=True)
    uuid: UUID = Column(Uuid, nullable=False, unique=True)
    table_name: str = Column(String(30), ForeignKey(f"{__child_name__}.name"), nullable=False)
    table_uuid: UUID = Column(Uuid, ForeignKey(f"{__child_name__}.uuid"), nullable=False)
    timestamp: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __ref__(self):
        from models import user, audit, transactions
        match self.table_name:
            case db_config.table_names.users:
                return user.User.query.filter_by(uuid=self.uuid).first()
            case db_config.table_names.audit_log:
                return audit.Audit.query.filter_by(uuid=self.uuid).first()
            case db_config.table_names.transaction_log:
                return transactions.Transaction.query.filter_by(uuid=self.uuid).first()
            case _:
                return None

    @staticmethod
    def __database_init__(session: scoped_session):
        from json import load

        results = load(open(config.initialization.index_path, "r"))
        for entry in results[db_config.table_names.uuid_index]:
            session.add(UUIDIndex(**{key: UUID(entry[key]) if key.__contains__("uuid") else entry[key] for key in
                                     ["uuid", "table_name", "table_uuid"]}))
        return True

    def __repr__(self):
        return f"<UUIDIndex {str(self.uuid)[24:]}>"


class TableIndex(Base):
    __tablename__ = db_config.table_names.table_index

    id: int = Column(Integer, primary_key=True)
    uuid: UUID = Column(Uuid, nullable=False, unique=True)
    name: str = Column(String(30), nullable=False, unique=True)
    model: str = Column(String(40), nullable=False, unique=True)

    @staticmethod
    def __database_init__(session: scoped_session):
        from json import load

        results = load(open(config.initialization.index_path, "r"))
        for entry in results[db_config.table_names.table_index]:
            session.add(TableIndex(**{key: UUID(entry[key]) if key.__contains__("uuid") else entry[key] for key in
                                      ["uuid", "name", "model"]}))
        return True

    def __repr__(self):
        return f"<TableIndex {self.name}>"
