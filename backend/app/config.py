"""Application configuration sourced from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed runtime settings for the backend service."""

    service_name: str = Field(default="dpp-backend", alias="DPP_SERVICE_NAME")
    environment: str = Field(default="development", alias="DPP_ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="DPP_LOG_LEVEL")
    api_v1_prefix: str = Field(default="/api/v1", alias="DPP_API_V1_PREFIX")
    database_url: str = Field(
        default="postgresql+asyncpg://dpp:changeme@localhost:5432/dpp",
        alias="DATABASE_URL",
    )

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def alembic_database_url(self) -> str:
        """Return a synchronous SQLAlchemy URL suitable for Alembic."""

        if self.database_url.startswith("postgresql+asyncpg://"):
            return self.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)

        return self.database_url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cache settings so all modules share one consistent runtime view."""
    return Settings()
