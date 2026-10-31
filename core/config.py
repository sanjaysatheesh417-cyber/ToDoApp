from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url
from pydantic import field_validator, model_validator
from typing import Literal
from sqlalchemy.engine import URL
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    DATABASE_URL: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_SERVER: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_DB: str | None = None

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
    
    @model_validator(mode="after")
    def configure_database_url(self):
        if self.DATABASE_URL:
            value = self.DATABASE_URL

            if value.startswith("postgres://"):
                value = "postgresql+psycopg://" + value[len("postgres://"):]
            elif value.startswith("postgresql://"):
                value = "postgresql+psycopg://" + value[len("postgresql://"):]
            parsed_url = make_url(value)

            if self.ENVIRONMENT == "production" and "sslmode" not in parsed_url.query:
                parsed_url = parsed_url.update_query_dict({"sslmode": "require"})

            self.DATABASE_URL = parsed_url.render_as_string(hide_password=False)
            return self

        if all((
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_SERVER,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
        )):
            local_url = URL.create(
                "postgresql+psycopg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                database=self.POSTGRES_DB,
                query={"sslmode": "require"} if self.ENVIRONMENT == "production" else {},
            )
            self.DATABASE_URL = local_url.render_as_string(hide_password=False)
            return self

        raise ValueError("Set DATABASE_URL or all POSTGRES_* database settings.")

settings = Settings()