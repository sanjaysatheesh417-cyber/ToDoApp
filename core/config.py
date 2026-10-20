from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
from typing import Literal
from sqlalchemy.engine import URL
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    SECRET_KEY: str
    JWT_ALGORITHM: Literal["HS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    ENVIRONMENT: Literal["development","production"] = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:5500"]

    RATE_LIMIT_LOGIN_ATTEMPTS: int = 10
    RATE_LIMIT_REGISTER_ATTEMPTS: int = 5

    LOG_LEVEL: str = "INFO"
    LOG_JSON_FORMAT: bool = False

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v:str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET KEY must be at least 32 characters")
        return v
    
    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: list[str]) -> list[str]:
        for origin in v:
            if origin == "*":
                raise ValueError("CORS wildcard '*' is not allowed. list exact origins used")
            if not origin.startswith(("http://", "https://")) or  origin.endswith("/"):
                raise ValueError(f"Bad CORS origin ,it needs to have scheme, no trailing slash")
        return v

    @model_validator(mode="after")
    def check_production(self):
        if self.ENVIRONMENT == 'production' and any(
            o.startswith("http://") for o in self.CORS_ORIGINS
        ):
            raise ValueError("Production CORS origins must use https://")
        return self
    
    @property
    def DATABASE_URL(self) -> URL:
        return URL.create(
            "postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        )

settings = Settings()