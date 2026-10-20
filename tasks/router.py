from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Literal

from sqlalchemy.orm import Session
from auth.models import User
from db import get_db
from deps import get_current_user
import tasks.service as service, tasks.schemas as schemas ,tasks.models as models

router = APIRouter(tags=["ToDoApp"], prefix="/ToDoApp")

NOT_FOUND = HTTPException(status_code=404, detail="task not found")

@router.post("/tasks", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
async def new_task(
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    task = service.create_task(db, user.id, payload)
    return task

@router.get("/tasks",response_model=list[schemas.TaskOut])
def list_tasks(
    status: models.TaskStatus | None = None,
    importance: models.Priority | None = None,
    search: str | None = Query(None, max_length=100),
    sort_by: Literal["time","added_on","importance"] = "time",
    order: Literal["asc", "desc"] = "asc",
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db:Session=Depends(get_db),
    user: User = Depends(get_current_user)):
    return service.get_all_tasks(db, user.id, status, importance, search, sort_by, order, limit, offset)

@router.get("/tasks/stats", response_model=dict[str,int])
def task_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.get_stats(db, user.id)

@router.get("/tasks/overdue", response_model=list[schemas.TaskOut])
def overdue(
    db:Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return service.get_overdue_tasks(db, user.id)

@router.get("/tasks/upcoming",response_model=list[schemas.TaskOut])
def upcoming(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return service.get_upcoming_tasks(db, user.id, days)

@router.delete("/tasks")
def clear_tasks(status: models.TaskStatus, db:Session = Depends(get_db), user: User = Depends(get_current_user)):
    return {"deleted": service.delete_tasks_by_status(db, user.id, status)}

@router.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def show_task(
    task_id: int,
    db: Session=Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_task = service.get_task(db, user.id, task_id)
    if db_task is None:
        raise NOT_FOUND
    return db_task

@router.patch("/tasks/{task_id}",response_model=schemas.TaskOut, status_code=status.HTTP_200_OK)
async def edit_task(
    task_id: int,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    task = service.update_task(db, user.id, task_id, payload)
    if task is None:
        raise NOT_FOUND
    return task

@router.patch("/tasks/{task_id}/complete", response_model = schemas.TaskOut)
def mark_complete(
    task_id: int,
    db: Session=Depends(get_db),
    user: User = Depends(get_current_user)
):
    task = service.complete_task(db, user.id, task_id)
    if task is None:
        raise NOT_FOUND
    return task

@router.post("/task/{task_id}/duplicate",
            response_model=schemas.TaskOut,
            status_code=status.HTTP_201_CREATED)
def duplicate(task_id: int ,db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = service.duplicate_task(db, user.id, task_id)
    if task is None:
        raise NOT_FOUND
    return task

@router.delete("/tasks/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    deleted = service.delete_task(db, user.id, task_id)
    if not deleted:
        raise NOT_FOUND

