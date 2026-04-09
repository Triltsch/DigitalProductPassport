"""Import relational models here so Alembic autogenerate can discover them."""

from app.infrastructure.db.base import metadata

__all__ = ["metadata"]
