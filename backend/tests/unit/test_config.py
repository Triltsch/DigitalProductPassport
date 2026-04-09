"""Unit tests for environment-backed backend configuration."""

from app.config import get_settings


def test_settings_use_env_override(monkeypatch) -> None:
    """Settings should reflect environment variables when provided."""
    get_settings.cache_clear()
    monkeypatch.setenv("DPP_SERVICE_NAME", "backend-test")
    monkeypatch.setenv("DPP_ENVIRONMENT", "test")
    monkeypatch.setenv("DPP_API_V1_PREFIX", "/api/custom")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@db:5432/dpp")

    settings = get_settings()

    assert settings.service_name == "backend-test"
    assert settings.environment == "test"
    assert settings.api_v1_prefix == "/api/custom"
    assert settings.database_url == "postgresql+asyncpg://test:test@db:5432/dpp"
    assert settings.alembic_database_url == "postgresql+psycopg://test:test@db:5432/dpp"

    get_settings.cache_clear()
