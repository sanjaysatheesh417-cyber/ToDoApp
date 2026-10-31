import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from auth import models,schemas,service
from core.config import settings
from core.limiter import limiter
from core.security import create_access_token
from db import get_db
from deps import get_current_user

router = APIRouter(prefix="/Auth", tags=["auth"])
audit = logging.getLogger("audit")

def ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"

@router.post("/register", response_model=schemas.ShowUser, status_code=status.HTTP_201_CREATED)
@limiter.limit(f"{settings.RATE_LIMIT_REGISTER_ATTEMPTS}/hour")
def register(request: Request, payload: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user = service.create_user(db, payload)
    except service.UsernameTaken:
        raise HTTPException(status_code=409, detail="Username already taken")
    audit.info("registered user_id=%s ip=%s", user.id, ip(request))
    return user

@router.post("/login", response_model=schemas.TokenResponse)
@limiter.limit(f"{settings.RATE_LIMIT_LOGIN_ATTEMPTS}/minute")
def login(request: Request, payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = service.authenticate_user(db, payload.username,payload.password)
    if user is None:
        audit.warning("login failed username=%r ip=%s", payload.username, ip(request))
        raise HTTPException(
            status_code=401,
            detail="invalid username and password!!",
            headers={"WWW-Authenticate": "Bearer"}
        )
    audit.info("login ok user_id=%s ip=%s", user.id, ip(request))
    return schemas.TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES*60
    )

@router.get("/me",response_model=schemas.ShowUser)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user