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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cache settings so all modules share one consistent runtime view."""
    return Settings()
