from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import tasks.models as models, tasks.schemas as schemas

def owned(db: Session, user_id: int):
    return db.query(models.Task).filter(models.Task.user_id == user_id)

def get_owned(db: Session, user_id: int,task_id: int) -> models.Task | None:
    return owned(db, user_id).filter(models.Task.id == task_id).first()

def _now() -> datetime:
    return datetime.now(timezone.utc)

def create_task(db:Session, user_id: int, payload: schemas.TaskCreate)->models.Task:
    task = models.Task(
        user_id=user_id,
        task=payload.task,
        time=payload.time,
        importance=payload.importance
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_task(db:Session, user_id:int, task_id:int)->models.Task|None:
    return get_owned(db, user_id, task_id)

def update_task(db: Session, user_id:int, task_id:int, payload: schemas.TaskUpdate) -> models.Task:
    task = get_owned(db, user_id, task_id)
    if task is None:
        return None

    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    for field,value in changes.items():
        setattr(task, field, value)

    task.edited_on = _now()
    db.commit()
    db.refresh(task)
    return task

def get_all_tasks(
        db: Session,
        user_id: int,
        status: models.TaskStatus | None = None,
        importance: models.Priority | None = None,
        search: str | None = None,
        sort_by: str = "time",
        order: str = "asc",
        limit: int = 20,
        offset: int = 0) -> list[models.Task]:
    query = owned(db, user_id)
    if status is not None:
        query = query.filter(models.Task.status == status)
    if importance is not None:
        query = query.filter(models.Task.importance == importance)
    if search:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.filter(models.Task.task.ilike(f"%{escaped}%", escape="\\"))

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

def delete_task(db: Session,user_id:int, task_id: int) -> bool:
    db_task = get_owned(db, user_id, task_id)
    if db_task is None:
        return False

    db.delete(db_task)
    db.commit()
    return True

def complete_task(db: Session, user_id:int, task_id: int) -> models.Task | None:
    db_task = get_owned(db, user_id, task_id)
    if db_task is None:
        return None
    db_task.status = models.TaskStatus.completed
    db_task.edited_on = _now()
    db.commit()
    db.refresh(db_task)
    return db_task

def get_overdue_tasks(db: Session, user_id: int) -> list[models.Task]:
    return owned(db,user_id).filter(models.Task.status == models.TaskStatus.pending).filter(models.Task.time < _now()).order_by(models.Task.time).all()

def get_upcoming_tasks(db:Session, user_id:int, days: int = 7) -> list[models.Task]:
    now = _now()
    return owned(db, user_id).filter(models.Task.status == models.TaskStatus.pending).filter(models.Task.time >= now).filter(models.Task.time <= now + timedelta(days = days)).order_by(models.Task.time).all()
    
def delete_tasks_by_status(
        db: Session,
        user_id: int,
        status: models.TaskStatus,
) -> int:
    count = owned(db, user_id).filter(models.Task.status == status).delete(synchronize_session=False)
    db.commit()
    return count

def get_stats(db: Session, user_id: int) -> dict[str,int]:
    rows = (
        db.query(models.Task.status, func.count(models.Task.id)).filter(models.Task.user_id == user_id).group_by(models.Task.status).all()
    )

    stats = {s.value: 0 for s in models.TaskStatus}
    for status, count in rows:
        stats[status.value] = count

    stats["overdue"] = db.query(func.count(models.Task.id)).filter(models.Task.user_id == user_id).filter(models.Task.status == models.TaskStatus.pending).filter(models.Task.time < _now()).scalar()
    return stats

def duplicate_task(db: Session,user_id:int, task_id:int ) -> models.Task | None:
    original = get_owned(db, user_id, task_id)

    if original is None:
        return None

    copy = models.Task(
        user_id=user_id,
        task = original.task,
        time = original.time,
        importance = original.importance,
        status = models.TaskStatus.pending
    )

    db.add(copy)
    db.commit()
    db.refresh(copy)
    return copy