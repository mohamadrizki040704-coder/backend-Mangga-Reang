import pytest
from pydantic import ValidationError

from core.config import Settings


def test_database_url_rejects_http_api_url() -> None:
    with pytest.raises(ValidationError, match="not an HTTP API URL"):
        Settings(
            DATABASE_URL="https://api.example.com",
            SECRET_KEY="test-secret",
        )


def test_database_url_normalizes_postgres_scheme() -> None:
    settings = Settings(
        DATABASE_URL="postgres://user:password@localhost:5432/mangga",
        SECRET_KEY="test-secret",
    )

    assert settings.DATABASE_URL == "postgresql://user:password@localhost:5432/mangga"
