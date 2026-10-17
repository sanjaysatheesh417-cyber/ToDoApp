import asyncio
import time
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks, Query
from typing import Literal
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import models, schemas

from db import get_db

import service, schemas ,models

router = APIRouter(tags=["ToDoApp"], prefix="/ToDoApp")

@router.post("/tasks", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
async def new_task(
    request: schemas.TaskCreate,
    db: Session = Depends(get_db),
):
    task = service.create_task(request,db)
    return task

@router.get("/tasks/stats", response_model=dict[str,int])
def task_stats(db: Session = Depends(get_db)):
    return service.get_stats(db)

@router.get("/tasks/overdue", response_model=list[schemas.TaskOut])
def overdue(
    db:Session = Depends(get_db)
):
    return service.get_overdue_tasks(db)

@router.get("/tasks/upcoming",response_model=list[schemas.TaskOut])
def upcoming(
    db: Session = Depends(get_db)
):
    return service.get_upcoming_tasks(db)

@router.patch("/tasks/{task_id}",response_model=schemas.TaskOut, status_code=status.HTTP_200_OK)
async def edit_task(
    task_id: int,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db)
):
    task = service.update_task(db, task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task

@router.get("/task/{task_id}/duplicate",
            response_model=schemas.TaskOut,
            status_code = status.HTTP_201_CREATED)
def duplicate(task_id: int ,db: Session = Depends(get_db)):
    task = service.duplicate_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task Not Found")
    return task

@router.get("/tasks",response_model=list[schemas.TaskOut])
def list_tasks(
    status: models.TaskStatus | None = None,
    importance: models.Priority | None = None,
    search: str | None = None,
    sort_by: Literal["time","added_on","importance"] = "time",
    order: Literal["asc", "desc"] = "asc",
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db:Session=Depends(get_db)):
    return service.get_all_tasks(db, status, importance, search, sort_by, order, limit, offset)

@router.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def show_task(
    task_id: int,
    db: Session=Depends(get_db)
):
    db_task = db.get(models.Task, task_id)
    return db_task

@router.patch("/tasks/{task_id}/complete", response_model = schemas.TaskOut)
def get_completed_tasks(
    task_id: int,
    db: Session=Depends(get_db)
):
    task = service.complete_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task No Found")
    return task

@router.delete("/tasks")
def clear_tasks(status: models.TaskStatus, db:Session = Depends(get_db)):
    deleted = service.delete_completed_tasks(db, status)
    return {"deleted": deleted}

@router.delete("/tasks/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
def remove_task(task_id: int, db: Session = Depends(get_db)):
    deleted = service.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task Not Found")

