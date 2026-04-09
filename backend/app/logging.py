"""Logging bootstrap with key-value formatted output."""

import logging
import sys

from app.config import Settings


def configure_logging(settings: Settings) -> None:
    """Initialize root logger with an opinionated key-value format."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="ts=%(asctime)s level=%(levelname)s logger=%(name)s msg=%(message)s",
        stream=sys.stdout,
    )
