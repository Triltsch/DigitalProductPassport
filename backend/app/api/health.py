"""Health endpoints for liveness and readiness checks."""

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def get_liveness() -> dict[str, str]:
    """Return liveness state for container and process checks."""
    return {"status": "alive"}


@router.get("/ready")
def get_readiness() -> dict[str, str]:
    """Return readiness state once mandatory configuration is available."""
    settings = get_settings()
    return {
        "status": "ready",
        "service": settings.service_name,
        "environment": settings.environment,
    }
