from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable = False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default= lambda: datetime.now(timezone.utc), nullable=False)
    