from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    task: str
    time: datetime
    importance: enumerate