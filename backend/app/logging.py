"""Logging bootstrap with structured key-value output."""

import logging
import sys

from app.config import Settings


def configure_logging(settings: Settings) -> None:
    """Initialize root logger with an opinionated structured format."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stdout,
        force=True,
    )
