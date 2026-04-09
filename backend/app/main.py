"""FastAPI app factory and application entrypoint."""

from fastapi import FastAPI

from app.api.health import router as health_router
from app.config import get_settings
from app.logging import configure_logging


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.service_name,
        version="0.1.0",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.on_event("startup")
    def setup_logging() -> None:
        configure_logging(settings)

    app.include_router(health_router)
    return app


app = create_app()
