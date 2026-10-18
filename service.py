from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
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
        search: str | None = None,
        sort_by: str = "time",
        order: str = "asc",
        limit: int = 20,
        offset: int = 0) -> list[models.Task]:
    query = db.query(models.Task)
    if status is not None:
        query = query.filter(models.Task.status == status)
    if importance is not None:
        query = query.filter(models.Task.importance == importance)
    if search is not None:
        query = query.filter(models.Task.task.ilike(f"%{search}%"))
    sort_columns = {
        "time": models.Task.time,
        "added_on": models.Task.added_on,
        "importance": models.Task.importance
    }
    column = sort_columns[sort_by]
    if order == "desc":
        column = column.desc()
    else:
        column = column.asc()
    return query.order_by(column, models.Task.id).offset(offset).limit(limit).all()

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
    
def delete_completed_tasks(
        db: Session,
        status: models.TaskStatus,
) -> int:
    count = (db.query(models.Task).filter(models.Task.status == status).delete(synchronize_session=False))
    db.commit()
    return count

def get_stats(db: Session) -> dict[str,int]:
    rows = (
        db.query(models.Task.status, func.count(models.Task.id)).group_by(models.Task.status).all()
    )

    stats = {s.value: 0 for s in models.TaskStatus}
    for status, count in rows:
        stats[status.value] = count

    stats["overdue"] = db.query(func.count(models.Task.id)).filter(models.Task.status == models.TaskStatus.pending).filter(models.Task.time < datetime.now(timezone.utc)).scalar()
    return stats

def duplicate_task(db: Session, task_id:int ) -> models.Task | None:
    original = db.get(models.Task, task_id)

    if original is None:
        return None

    copy = models.Task(
        task = original.task,
        time = original.time,
        importance = original.importance,
        status = models.TaskStatus.pending
    )

    db.add(copy)
    db.commit()
    db.refresh(copy)
    return copy
