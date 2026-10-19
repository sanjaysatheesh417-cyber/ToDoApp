from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from ..db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable = False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan", lazy="select", order_by="Token.expires_at", single_parent=True)

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_jti = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("user", back_populates="tokens")    