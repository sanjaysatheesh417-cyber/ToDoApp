from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import tasks.router as router
from db import Base, engine
import tasks.models as models
from contextlib import asynccontextmanager
from sqlalchemy import text
from core.config import settings
import logging


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET","POST","PATCH","DELETE"],
    allow_headers=["Content-Type", "Authorisation"],
)



app.include_router(router.router)