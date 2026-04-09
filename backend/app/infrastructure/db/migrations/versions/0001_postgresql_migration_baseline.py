"""Create the initial PostgreSQL migration baseline.

Revision ID: 0001_postgresql_migration_baseline
Revises:
Create Date: 2026-04-09 00:00:00
"""

from __future__ import annotations


revision = "0001_postgresql_migration_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Establish the initial migration baseline without schema objects yet."""

    pass


def downgrade() -> None:
    """Revert the initial migration baseline."""

    pass
