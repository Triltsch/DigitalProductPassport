"""FastAPI app factory and application entrypoint."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.health import router as health_router
from app.config import get_settings
from app.dependencies import get_token_validator
from app.logging import configure_logging


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
        """Configure logging and optionally warm the JWKS cache on startup."""
        configure_logging(settings)
        if settings.keycloak_preload_jwks:
            try:
                get_token_validator().prime_jwks_cache()
            except Exception:
                logger.warning(
                    "Failed to preload Keycloak JWKS cache during startup.",
                    exc_info=True,
                )
        yield

    app = FastAPI(
        title=settings.service_name,
        version="0.1.0",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.include_router(health_router)
    return app


app = create_app()
