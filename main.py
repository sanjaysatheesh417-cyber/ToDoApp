from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from db import Base, engine,health_check
from contextlib import asynccontextmanager
from core.config import settings
from core.limiter import limiter
from core.logging_config import setup_logging
import logging

import auth.models
import tasks.models

from auth.router import router as auth_router
from tasks.router import router as tasks_router

setup_logging(settings.LOG_LEVEL, settings.LOG_JSON_FORMAT)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.begin() as conn:
        conn.execute(text("SELECT pg_advisory_xact_lock(724001)"))
        Base.metadata.create_all(bind=conn)
        logger.info("startup complete environment=%s", settings.ENVIRONMENT)
    yield

prod = settings.ENVIRONMENT == "production"
app = FastAPI(
    title = "ToDoApp",
    lifespan=lifespan,
    docs_url=None if prod else "/docs",
    redoc_url=None,
    openapi_url=None if prod else "/openapi.json"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET","POST","PATCH","DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/health", include_in_schema=False)
def health():
    if not health_check():
        return JSONResponse({"status":"unavailable"}, status_code=503)
    return {"status":"ok"}