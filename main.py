from fastapi import FastAPI

from db import Base, engine
import models
from contextlib import asynccontextmanager
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app):
    with engine.begin() as conn:
        conn.execute(text("SELECT pg_advisory_xact_lock(724001)"))
        Base.metadata.create_all(bind=conn)
    yield

app = FastAPI(
    title = "ToDoApp",
    lifespan=lifespan
)