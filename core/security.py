from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from jwt import InvalidTokenError

from core.config import settings

ph = PasswordHasher()

def hash_password(password:str)->str:
    return ph.hash(password)

def verify_password(password:str, hashed:str)-> bool:
    try:
        return ph.verify(hashed, password)
    except (VerificationError, InvalidHashError):
        return False

def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub":str(user_id),
        "iat":now,
        "exp":now+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str)->int:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require":["exp","sub"]},
        )
        return int(payload["sub"])
    except (InvalidTokenError, ValueError) as exc:
        raise ValueError("Invalid or expired token") from exc