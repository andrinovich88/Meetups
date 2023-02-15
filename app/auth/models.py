from config.database import Base
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        sql)
from sqlalchemy.dialects.postgresql import UUID


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(40), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    password_hash = Column(String(256))
    confirmed = Column(Boolean(), server_default=sql.expression.false())
    first_name = Column(String(64))
    last_name = Column(String(64))
    is_active = Column(Boolean(), server_default=sql.expression.false())
    avatar_url = Column(String(256))
    is_super = Column(Boolean(), server_default=sql.expression.false())


class Tokens(Base):
    __tablename__ = "tokens"

    id = Column(Integer(), primary_key=True)
    token = Column(
        UUID(as_uuid=False),
        unique=True,
        nullable=False,
        index=True
    )
    expires = Column(DateTime())
    user_id = Column(ForeignKey("users.id", ondelete='CASCADE'))
