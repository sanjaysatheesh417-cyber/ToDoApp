from pydantic import BaseModel, field_validator, Field
from datetime import datetime, timezone
import re

USERNAME_RE = re.compile(r"^[a-z0-9_.-]{3,32}$")

def clean_username(v: str) -> str:
    return v.strip().lower()
class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = clean_username(v)
        if not USERNAME_RE.fullmatch(v):
            raise ValueError("Username must be 3-32 characters: letters, digits, _ . -")
        return v
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v:str) -> str:
        problems = []
        if len(v) < 10:
            problems.append(f"Must be atleast 10 character long!!")
        if len(v) > 128:
            problems.append(f"Must be at most 128 characters long!!")
        if v.strip != v:
            problems.append("Must not start or end with a space!!")
        if re.fullmatch(r"/d+",v):
            problems.append("must not contain only digits")
        if problems:
            raise ValueError(" ".join(problems))
        return v

class LoginRequest(BaseModel):
    username: str
    password: str = Field(max_length=128)

    @field_validator("username")
    @classmethod
    def normalize(cls, v:str) -> str:
        return clean_username(v)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class ShowUser(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class HealthCheckResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    timestamp: datetime