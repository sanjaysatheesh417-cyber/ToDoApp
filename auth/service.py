from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from auth import models, schemas
from core.security import hash_password, verify_password

DUMMY_HASH = hash_password("dummy-password-for-timing")

class UsernameTaken(Exception):
    pass

def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    user = models.User(
        username = payload.username,
        hashed_password = hash_password(payload.password)
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise UsernameTaken()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username:str, password: str) -> models.User | None:
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        verify_password(password,DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
