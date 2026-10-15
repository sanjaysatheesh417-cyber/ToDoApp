from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import enum
from models import Priority, TaskStatus

class TaskCreate(BaseModel):
    task: str
    time: datetime
    importance: Priority = Priority.moderate
    status: TaskStatus = TaskStatus.pending

    @field_validator('task')
    @classmethod
    def validate_task(cls, v:str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("task cannot be empty")
        if len(v) > 255:
            raise ValueError("task is too long, please limit to 255 characters!!")
        return v

class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task: str
    time: datetime
    importance: Priority
    status: TaskStatus
    added_on: datetime
    edited_on: datetime | None = None

class TaskUpdate(BaseModel):
    task: str
    time: datetime
    importance: Priority
    status: TaskStatus

    @field_validator('task')
    @classmethod
    def validate_task(cls, v:str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("task cannot be empty")
        if len(v) > 255:
            raise ValueError("task is too long, please limit to 255 characters!!")
        return v