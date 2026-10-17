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

def update_task(db: Session, task_id:int, payload: schemas.TaskUpdate) -> models.Task:
    db_task = db.get(models.Task, task_id)
    if db_task is None:
        return None

    changes = payload.model_dump(exclude_unset=True)
    for field,value in changes.items():
        setattr(db_task, field, value)

    db_task.edited_on = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_all_tasks(
        db: Session,
        status: models.TaskStatus | None = None,
        importance: models.Priority | None = None,
        search: str | None = None) -> list[models.Task]:
    query = db.query(models.Task)
    if status is not None:
        query = query.filter(models.Task.status == status)
    if importance is not None:
        query = query.filter(models.Task.importance == importance)
    if search is not None:
        query = query.filter(models.Task.task.ilike(f"%{search}%"))
    return query.order_by(models.Task.time).all()

def delete_task(db: Session, task_id: int) -> bool:
    db_task = db.get(models.Task, task_id)
    if db_task is None:
        return False

    db.delete(db_task)
    db.commit()
    return True

def complete_task(db: Session, task_id: int) -> models.Task | None:
    db_task = db.get(models.Task, task_id)
    if db_task is None:
        return None
    db_task.status = models.TaskStatus.completed
    db_task.edited_on = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_overdue_tasks(db: Session) -> list[models.Task]:
    return db.query(models.Task).filter(models.Task.status == models.TaskStatus.pending).filter(models.Task.time < datetime.now(timezone.utc)).order_by(models.Task.time).all()

def get_upcoming_tasks(db:Session) -> list[models.Task]:
    return db.query(models.Task).filter(models.Task.status == models.TaskStatus.pending).filter(models.Task.time > datetime.now(timezone.utc)).order_by(models.Task.time).all()
    