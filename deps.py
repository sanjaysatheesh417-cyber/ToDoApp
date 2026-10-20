from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from auth.models import User
from core.security import decode_access_token
from db import get_db

bearer = HTTPBearer(auto_error=False)

def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db)) -> User:
    unauthorised = HTTPException(
        status_code=401,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"}
    )
    if creds is None:
        raise unauthorised
    try:
        user_id = decode_access_token(creds.credentials)
    except ValueError:
        raise unauthorised
    user = db.get(User, user_id)
    if user is None:
        raise unauthorised
    return user