from datetime import datetime
from sqlalchemy import Column , Integer, String, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from db import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, nullable=False)
    added_on = Column(DateTime, default=datetime.utcnow, nullable=False)
    edited_on = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime, nullable = False)
    