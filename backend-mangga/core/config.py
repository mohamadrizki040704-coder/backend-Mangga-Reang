from urllib.parse import urlsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "API Juragan Mangga Reang"
    VERSION: str = "1.0.0"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:3000"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        value = value.strip()
        scheme = urlsplit(value).scheme.lower()

        if scheme in {"http", "https"}:
            raise ValueError(
                "DATABASE_URL must be a PostgreSQL connection URL, not an HTTP API URL. "
                "Set it to the database's Internal Database URL in the backend service environment."
            )
        if not scheme:
            raise ValueError(
                "DATABASE_URL must include a database scheme, such as postgresql://."
            )
        if scheme == "postgres":
            return "postgresql://" + value[len("postgres://") :]

        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")


settings = Settings()
