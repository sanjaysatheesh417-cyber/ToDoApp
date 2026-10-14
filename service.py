from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import models, schemas

def create_task(request: schemas.TaskCreate, db:Session):
    new_task = models.Task(
        task=request.task,
        time=request.time,
        importance=request.importance
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task