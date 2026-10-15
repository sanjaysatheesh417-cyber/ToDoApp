import asyncio
import time
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks, Query

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

@router.get("/tasks",response_model=list[schemas.TaskOut])
def list_tasks(
    status: models.TaskStatus | None = None,
    importance: models.Priority | None = None,
    db:Session=Depends(get_db)):
    return service.get_all_tasks(db, status, importance)