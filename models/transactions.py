from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Uuid, Text, JSON
from sqlalchemy.orm import scoped_session, relationship

from services.database import Base
from services.database_utilities import gen_uuid
from services.config import ExtendedConfig, Config

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

config = Config().get()
db_config = ExtendedConfig(path=config.configuration.database_path).get()
game_config = ExtendedConfig(path=config.configuration.game_path).get()


@dataclass
class Transaction(Base):
    __tablename__ = db_config.table_names.transaction_log
    __child_name__ = db_config.table_names.transaction_types
    __child1_name__ = db_config.table_names.source_types
    __child2_name__ = db_config.table_names.material_types
    __child3_name__ = db_config.table_names.exchange_types
    __child4_name__ = db_config.table_names.usage_types
    __related_name__ = db_config.table_names.users

    id: int = Column(Integer, primary_key=True)
    uuid: UUID = Column(Uuid, nullable=False, unique=True,
                        default=lambda: gen_uuid(db_config.table_names.transaction_log))
    user_uuid: UUID = Column(Uuid, ForeignKey(f'{__related_name__}.uuid'), nullable=False)
    type_uuid: UUID = Column(Uuid, ForeignKey(f'{__child_name__}.uuid'), nullable=True)

    amount: int = Column(Integer, nullable=False)
    description: str = Column(Text(1000), nullable=True)
    timestamp: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    details: dict = Column(JSON, nullable=False)

    source: str = Column(String(40), ForeignKey(f'{__child1_name__}.name'), nullable=True)
    material: str = Column(String(40), ForeignKey(f'{__child2_name__}.name'), nullable=False)
    exchange: str = Column(String(40), ForeignKey(f'{__child3_name__}.name'), nullable=True)
    exchange_result: str = Column(String(40), ForeignKey(f'{__child2_name__}.name'), nullable=True)
    destination: str = Column(String(40), ForeignKey(f'{__child4_name__}.name'), nullable=True)

    # user = relationship("User", back_populates="transactions")

    @staticmethod
    def __database_init__(db_session: scoped_session):
        """
        This method is called when the database is initialized. \n
        This model does not need to be initialized.
        :param db_session: ignored
        :return: None
        """
        return True

    def __repr__(self):
        return f"<Transaction {str(self.uuid)[24:]}>"


@dataclass
class TransactionType(Base):
    __tablename__ = db_config.table_names.transaction_types

    id: int = Column(Integer, primary_key=True)
    uuid: UUID = Column(Uuid, nullable=False, unique=True,
                        default=lambda: gen_uuid(db_config.table_names.transaction_types))
    name: str = Column(String(40), nullable=False, unique=True)
    description: str = Column(String(200), nullable=False)
    uses: dict = Column(JSON, nullable=False)

    @staticmethod
    def __database_init__(db_session: scoped_session):
        from json import load

        results = load(open(config.initialization.transactions_path, "r"))
        for entry in results[db_config.table_names.transaction_types]:
            db_session.add(TransactionType(**{key: UUID(entry[key]) if key.__contains__("uuid") else entry[key]
                                              for key in ["name", "description", "uses"]}))
        return True

    def __repr__(self):
        return f"<TransactionType {self.name}>"


@dataclass
class SourceType(Base):
    __tablename__ = db_config.table_names.source_types

    id: int = Column(Integer, primary_key=True)
    uuid: UUID = Column(Uuid, nullable=False, unique=True, default=lambda: gen_uuid(db_config.table_names.source_types))
    name: str = Column(String(40), nullable=False, unique=True)
    description: str = Column(String(200), nullable=True, unique=True)
    categories: list = Column(JSON, nullable=False)
    rewards: list = Column(JSON, nullable=False)

    @staticmethod
    def __database_init__(db_session: scoped_session):
        from json import load

        results = load(open(config.initialization.transactions_path, "r"))
        for entry in results[db_config.table_names.source_types]:
            db_session.add(SourceType(**{key: UUID(entry[key]) if key.__contains__("uuid") else entry[key]
                                         for key in ["name", "description", "categories", "rewards"]}))
        return True

    def __repr__(self):
        return f"<SourceType {self.name}>"


@dataclass
class MaterialType(Base):
    __tablename__ = db_config.table_names.material_types

    id: int = Column(Integer, primary_key=True)
    uuid: UUID = Column(Uuid, nullable=False, unique=True,
                        default=lambda: gen_uuid(db_config.table_names.material_types))
    name: str = Column(String(40), nullable=False, unique=True)
    description: str = Column(String(200), nullable=True, unique=True)
    sources: list = Column(JSON, nullable=False)
    exchanges: list = Column(JSON, nullable=False)
    exchange_results: list = Column(JSON, nullable=False)
    usages: list = Column(JSON, nullable=False)

    @staticmethod
    def __database_init__(db_session: scoped_session):
        from json import load

        results = load(open(config.initialization.transactions_path, "r"))
        for entry in results[db_config.table_names.material_types]:
            db_session.add(MaterialType(**{key: UUID(entry[key]) if key.__contains__("uuid") else entry[key]
                                           for key in ["name", "description", "sources", "exchanges",
                                                       "exchange_results", "usages"]}))
        return True

    def __repr__(self):
        return f"<MaterialType {self.name}>"


@dataclass
class ExchangeType(Base):
    __tablename__ = db_config.table_names.exchange_types

    id: int = Column(Integer, primary_key=True)
    uuid: UUID = Column(Uuid, nullable=False, unique=True,
                        default=lambda: gen_uuid(db_config.table_names.exchange_types))
    name: str = Column(String(40), nullable=False, unique=True)
    description: str = Column(String(200), nullable=True)
    sources: list = Column(JSON, nullable=False)
    results: list = Column(JSON, nullable=False)

    @staticmethod
    def __database_init__(db_session: scoped_session):
        from json import load

        results = load(open(config.initialization.transactions_path, "r"))
        for entry in results[db_config.table_names.exchange_types]:
            db_session.add(ExchangeType(**{key: UUID(entry[key]) if key.__contains__("uuid") else entry[key]
                                           for key in ["name", "description", "sources", "results"]}))
        return True

    def __repr__(self):
        return f"<ExchangeType {self.name}>"


@dataclass
class UsageType(Base):
    __tablename__ = db_config.table_names.usage_types

    id: int = Column(Integer, primary_key=True)
    uuid: UUID = Column(Uuid, nullable=False, unique=True, default=lambda: gen_uuid(db_config.table_names.usage_types))
    name: str = Column(String(40), nullable=False, unique=True)
    description: str = Column(String(200), nullable=True)
    item: list = Column(JSON, nullable=False)
    results: list = Column(JSON, nullable=False)

    @staticmethod
    def __database_init__(db_session: scoped_session):
        from json import load

        results = load(open(config.initialization.transactions_path, "r"))
        for entry in results[db_config.table_names.usage_types]:
            db_session.add(UsageType(**{key: UUID(entry[key]) if key.__contains__("uuid") else entry[key]
                                        for key in ["name", "description", "item", "results"]}))
        return True

    def __repr__(self):
        return f"<UsageType {self.name}>"
