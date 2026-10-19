from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, timezone
import re

class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("name cannot be empty")
        if len(v) > 255:
            raise ValueError("name too long ,can be within 255 characters")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v:str) -> str:
        problems = []
        if len(v) < 10:
            problems.append(f"Must be atleast 10 character long!!")
        if len(v) > 128:
            problems.append(f"Must be at most 126 characters long!!")
        if v.strip != v:
            problems.append("Must not start or end with a space!!")
        if re.fullmatch(r"/d+",v):
            problems.append("must not contain only digits")
        if problems:
            raise ValueError(" ".join(problems))
        return v.strip()

class LoginRequet(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str
    expires_in: int = 86400

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