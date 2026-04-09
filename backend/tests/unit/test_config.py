"""Unit tests for environment-backed backend configuration."""

from app.config import Settings, get_settings


def test_settings_use_env_override(monkeypatch) -> None:
    """Settings should reflect environment variables when provided."""
    get_settings.cache_clear()
    monkeypatch.setenv("DPP_SERVICE_NAME", "backend-test")
    monkeypatch.setenv("DPP_ENVIRONMENT", "test")
    monkeypatch.setenv("DPP_API_V1_PREFIX", "/api/custom")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@db:5432/dpp")
    monkeypatch.setenv("KEYCLOAK_ISSUER_URL", "http://keycloak:8080/realms/test")
    monkeypatch.setenv("JWT_AUDIENCE", "test-audience")
    monkeypatch.setenv("JWT_ALGORITHM", "RS256")
    monkeypatch.setenv("KEYCLOAK_FRONTEND_CLIENT_ID", "test-frontend")
    monkeypatch.setenv("KEYCLOAK_BACKEND_CLIENT_ID", "test-backend")

    settings = get_settings()

    assert settings.service_name == "backend-test"
    assert settings.environment == "test"
    assert settings.api_v1_prefix == "/api/custom"
    assert settings.database_url == "postgresql+asyncpg://test:test@db:5432/dpp"
    assert settings.alembic_database_url == "postgresql+psycopg://test:test@db:5432/dpp"
    assert settings.keycloak_issuer_url == "http://keycloak:8080/realms/test"
    assert settings.jwt_audience == "test-audience"
    assert settings.jwt_algorithm == "RS256"
    assert settings.keycloak_frontend_client_id == "test-frontend"
    assert settings.keycloak_backend_client_id == "test-backend"
    assert (
        settings.keycloak_openid_configuration_url
        == "http://keycloak:8080/realms/test/.well-known/openid-configuration"
    )
    assert (
        settings.keycloak_jwks_url
        == "http://keycloak:8080/realms/test/protocol/openid-connect/certs"
    )

    get_settings.cache_clear()


def test_alembic_database_url_passthrough_for_non_asyncpg(monkeypatch) -> None:
    """alembic_database_url should return the URL unchanged when it is not asyncpg."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@db:5432/dpp")

    settings = Settings()

    assert settings.alembic_database_url == "postgresql+psycopg://test:test@db:5432/dpp"


def test_keycloak_jwks_url_trims_trailing_slash() -> None:
    """Keycloak-derived URLs should remain stable when issuer values include a trailing slash."""
    settings = Settings(keycloak_issuer_url="http://keycloak:8080/realms/dpp/")

    assert settings.keycloak_openid_configuration_url == (
        "http://keycloak:8080/realms/dpp/.well-known/openid-configuration"
    )
    assert settings.keycloak_jwks_url == (
        "http://keycloak:8080/realms/dpp/protocol/openid-connect/certs"
    )
