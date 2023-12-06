from sqlalchemy import Boolean, DateTime, Column, Integer, String, JSON, Uuid
from sqlalchemy.orm import scoped_session

from services.database import Base, generate_uuid
from services.config import ExtendedConfig, Config

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

config = Config().get()
db_config = ExtendedConfig(path=config.configuration.database_path).get()


@dataclass
class User(Base):
    """
    User model representing a user.
    """
    __tablename__ = db_config.table_names.users
    __related_name__ = db_config.table_names.audit_log
    # __related1_name__ = db_config.table_names.wish_log

    # User-specific information
    id: int = Column(Integer, primary_key=True)
    uuid: UUID = Column(Uuid, nullable=False, unique=True,
                        default=lambda: generate_uuid(db_config.table_names.users))
    username: str = Column(String(50), nullable=False, unique=True)
    name: str = Column(String(50), nullable=False)
    email: str = Column(String(50), nullable=False, unique=True)
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    country: str = Column(String(2), nullable=True, default="XX")

    # Security & authentication
    tags: dict = Column(JSON, nullable=False, default={"tags": db_config.field_init.users.tags})
    permissions: dict = Column(JSON, nullable=False, default={"permissions": db_config.field_init.users.permissions})
    permission_level: int = Column(Integer, nullable=False, default=3)
    admin: bool = Column(Boolean, nullable=False, default=False)
    password: str = Column(String(60), nullable=False)
    token: str = Column(String(500), nullable=True, unique=True, default=None)

    # Content
    total_gains: int = Column(Integer, nullable=True, default=0)
    total_spending: int = Column(Integer, nullable=True, default=0)
    total_wishes: int = Column(Integer, nullable=True, default=0)
    balance: dict = Column(JSON, nullable=True,
                           default={"balance": db_config.field_init.users.balance._ConfigNode__node_dict})

    # Tracking
    active_until: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    def mark_active(self, session: scoped_session):
        self.active_until += timedelta(seconds=config.security.activity_timeout)
        session.commit()

    @staticmethod
    def __database_init__(session: scoped_session):
        from json import load

        results = load(open(config.initialization.users_path, "r"))
        for user in results[db_config.table_names.users]:
            session.add(User(**{key: UUID(user[key]) if key.__contains__("uuid") else user[key] for key in
                                ["uuid", "username", "name", "password", "email", "country", "admin"]}))
        return True

    def __repr__(self):
        return f"<User {self.username}>"
