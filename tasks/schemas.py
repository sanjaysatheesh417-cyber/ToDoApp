from pydantic import BaseModel, field_validator, ConfigDict
from datetime import datetime
from tasks.models import Priority, TaskStatus

def clean_task(v: str| None)->str|None:
    if v is None:
        return v
    v = v.strip()
    if not v:
        raise ValueError("task cannot be empty")
    if len(v) > 255:
        raise ValueError("task is too long, please limit it to 255 characters")
    return v
class TaskCreate(BaseModel):
    task: str
    time: datetime
    importance: Priority = Priority.moderate

    check_task = field_validator("task")(clean_task)
class TaskUpdate(BaseModel):
    task: str | None = None
    time: datetime | None = None
    importance: Priority | None = None 
    status: TaskStatus | None = None

    check_task = field_validator("task")(clean_task)

class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task: str
    time: datetime
    importance: Priority
    status: TaskStatus
    added_on: datetime
    edited_on: datetime | None = None