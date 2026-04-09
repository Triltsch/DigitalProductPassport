"""Integration tests for backend health endpoints."""

from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_liveness_endpoint() -> None:
    """Liveness endpoint should signal process-level availability."""
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readiness_endpoint_contains_runtime_context(monkeypatch) -> None:
    """Readiness endpoint should expose basic service and environment context."""
    monkeypatch.setenv("DPP_SERVICE_NAME", "backend-integration")
    monkeypatch.setenv("DPP_ENVIRONMENT", "test")

    from app.config import get_settings

    get_settings.cache_clear()
    readiness_response = client.get("/health/ready")

    assert readiness_response.status_code == 200
    assert readiness_response.json() == {
        "status": "ready",
        "service": "backend-integration",
        "environment": "test",
    }

    get_settings.cache_clear()
