from datetime import datetime ,timezone
from sqlalchemy import Column , Integer, String, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from db import Base
import enum

class Priority(str, enum.Enum):
    high = "high"
    moderate = "moderate"
    low = "low"

class TaskStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, nullable=False)
    added_on = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    edited_on = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    time = Column(DateTime(timezone=True), nullable = False)
    importance = Column(Enum(Priority, name="importance_enum"), default=Priority.moderate, nullable= False)
    status = Column(Enum(TaskStatus, name="status_enum"), default=TaskStatus.pending, nullable=False)
