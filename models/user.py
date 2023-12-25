from sqlalchemy import Boolean, DateTime, Column, Integer, String, JSON, Uuid
from sqlalchemy.orm import scoped_session
from marshmallow import Schema, fields
from marshmallow.utils import RAISE

from services.database import Base, ma, generate_uuid
from services.configuration import Config
from services.validation import validate_alphanumeric, validate_email, validate_password

from datetime import datetime, timedelta
from uuid import UUID

config = Config()
db_config = config.database

# Initialization
default_tags = {"tags": config.default.tags}
default_permissions = {"permissions": config.default.permissions}
default_balance = {"balance": config.default.balance.as_dict()}


class User(Base):
    """
    User model representing a user.
    """
    __tablename__ = db_config.table.users
    __related_name__ = db_config.table.audit_log

    # User-specific information
    id: int = Column(Integer, primary_key=True)
    uuid: UUID = Column(Uuid, nullable=False, unique=True, default=lambda: generate_uuid(db_config.table.users))
    username: str = Column(String(50), nullable=False, unique=True)
    name: str = Column(String(50), nullable=False)
    email: str = Column(String(75), nullable=False, unique=True)
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    country: str = Column(String(2), nullable=True, default="XX")

    # Security & authentication
    tags: dict = Column(JSON, nullable=False, default=default_tags)
    permissions: dict = Column(JSON, nullable=False, default=default_permissions)
    permission_level: int = Column(Integer, nullable=False, default=3)
    admin: bool = Column(Boolean, nullable=False, default=False)
    password: str = Column(String(60), nullable=False)
    token: str = Column(String(500), nullable=True, unique=True, default=None)

    # Content
    total_gains: int = Column(Integer, nullable=True, default=0)
    total_spending: int = Column(Integer, nullable=True, default=0)
    total_wishes: int = Column(Integer, nullable=True, default=0)
    balance: dict = Column(JSON, nullable=True, default=default_balance)

    # Tracking
    active_until: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)

    def mark_active(self, session: scoped_session):
        self.active_until = datetime.utcnow() + timedelta(seconds=config.security.tracking.activity_timeout)
        session.commit()

    @staticmethod
    def __database_init__(session: scoped_session, init: str):
        from json import load

        results = load(open(init, "r"))
        for user in results[db_config.table.users]:
            session.add(User(**{key: UUID(user[key]) if key.__contains__("uuid") else user[key] for key in
                                ["uuid", "username", "name", "password", "email", "country", "admin"]}))
        return True

    def __repr__(self):
        return f"<User {self.username}>"


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ("id", "email", "password", "token", "permissions",
                   "permission_level", "balance")
        datetimeformat = "%Y-%m-%d %H:%M:%S.%f"
        unknown = RAISE


class UserFullSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ("password", "token")
        datetimeformat = "%Y-%m-%d %H:%M:%S.%f"
        unknown = RAISE


class UserBodySchema(Schema):
    name = fields.Str(required=True, validate=validate_alphanumeric)
    username = fields.Str(required=True, validate=validate_alphanumeric)
    email = fields.Str(required=True, validate=validate_email)
    admin = fields.Bool(required=False, default=False)
    password = fields.Str(required=False, validate=validate_password)
    country = fields.Str(required=False, default="XX", validate=validate_alphanumeric)
    tags = fields.Dict(required=False, default=default_tags)
