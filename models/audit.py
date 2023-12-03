from sqlalchemy import DateTime, Column, String, Integer, ForeignKey, Boolean, Uuid, JSON, Enum
from sqlalchemy.orm import scoped_session, relationship

from services.database import Base
from services.database_utilities import gen_uuid
from services.config import ExtendedConfig, Config

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from inspect import currentframe

config = Config().get()
db_config = ExtendedConfig(path=config.configuration.database_path).get()


@dataclass
class Audit(Base):
    __tablename__ = db_config.table_names.audit_log
    __child_name__ = db_config.table_names.audit_actions
    __related_name__ = db_config.table_names.users

    id: int = Column(Integer, primary_key=True)
    uuid: UUID = Column(Uuid, nullable=False, unique=True, default=lambda: gen_uuid(db_config.table_names.audit_log))
    user_uuid: UUID = Column(Uuid, ForeignKey(f'{__related_name__}.uuid'), nullable=False)
    action_uuid: UUID = Column(Uuid, ForeignKey(f'{__child_name__}.uuid'), nullable=False)

    endpoint: str = Column(String(100), nullable=False, default=currentframe().f_back.f_code.co_name)
    parameters: dict = Column(JSON, nullable=True, default=None)
    response: dict = Column(JSON, nullable=True, default=None)
    response_code: int = Column(Integer, nullable=False, default=200)
    severity: str = Column(Enum(*db_config.audit.priorities), nullable=False, default="INFO")
    timestamp: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    # user = relationship("User", back_populates="audit")

    # @staticmethod
    # def create_entry(db_session: scoped_session, user_uuid: str, action_uuid: int, is_user_action: bool,
    #                  endpoint: str, parameters: dict, response: dict, response_code: int):
    #     db_session.add(Audit(**{key: locals()[key] for key in
    #                             ["user_uuid", "action_uuid", "is_user_action", "endpoint", "parameters", "response",
    #                              "response_code"]}))
    #     db_session.commit()
    #     return True

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
        return f"<Audit {str(self.uuid)[24:]}>"


@dataclass
class AuditAction(Base):
    __tablename__ = db_config.table_names.audit_actions
    __parent_name__ = db_config.table_names.audit_log

    id: int = Column(Integer, primary_key=True)
    uuid: UUID = Column(Uuid, nullable=False, unique=True, default=lambda: gen_uuid(db_config.table_names.audit_actions))
    name: str = Column(String(36), nullable=False, unique=True)

    priority: str = Column(Enum(*db_config.audit.priorities), nullable=False, default="INFO")
    default: bool = Column(Boolean, nullable=False, default=False)
    permission_level: str = Column(Integer, nullable=False)
    permissions: dict = Column(JSON, nullable=True, default=None)

    @staticmethod
    def __database_init__(db_session: scoped_session):
        from json import load

        results = load(open(config.initialization.audit_path, "r"))
        for entry in results[db_config.table_names.audit_actions]:
            db_session.add(AuditAction(**{key: UUID(entry[key]) if key.__contains__("uuid") else entry[key] for key in
                                          ["name", "priority", "default", "permission_level", "permissions"]}))
        return True

    def __repr__(self):
        return f"<AuditAction {self.name}>"
