# Backend Service Foundation

This directory contains the initial FastAPI backend foundation for the DPP service.

## Intended Structure

```text
backend/
|-- app/
|   |-- main.py             FastAPI app factory and runtime entrypoint
|   |-- config.py           Environment-backed application settings
|   |-- logging.py          Logging bootstrap
|   |-- api/v1/             HTTP routers and request models
|   |-- api/health.py       `/health/live` and `/health/ready`
|   |-- domain/             Business logic without framework coupling
|   |-- services/           Application orchestration layer
|   |-- infrastructure/     Database, storage, and auth adapters
|   `-- tasks/              Background task entry points
|-- tests/
|   |-- unit/
|   |-- integration/
|   `-- e2e/
|-- app/infrastructure/db/base.py  SQLAlchemy metadata baseline for Alembic
|-- app/infrastructure/db/migrations Alembic environment and version scripts
|-- pyproject.toml         Project dependencies and pytest config
|-- Dockerfile             Added in a later Sprint 0 issue
`-- alembic.ini            Alembic configuration for PostgreSQL migrations
```

## Implemented in this foundation

- FastAPI app factory in `app/main.py`.
- Environment-variable configuration via Pydantic settings in `app/config.py`.
- Base structured logging initialization in `app/logging.py`.
- Health endpoints:
  - `GET /health/live`
  - `GET /health/ready`
- Initial backend tests for settings and health routes.
- Alembic migration baseline for future PostgreSQL-backed models.

## Local run

From the `backend/` folder:

```powershell
pip install -e .[test]
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Local tests

From the `backend/` folder:

```powershell
python -m pytest
```

## Local migrations

The backend uses Alembic for relational schema migrations.

From the `backend/` folder:

```powershell
pip install -e .[test]
alembic current
alembic revision -m "describe change"
alembic upgrade head
```

Notes:

- Alembic reads `DATABASE_URL` from the repository `.env` file via `app.config.Settings`.
- Async PostgreSQL URLs (`postgresql+asyncpg://...`) are converted automatically to a synchronous `psycopg` URL for migration runs.
- Migration scripts belong in `app/infrastructure/db/migrations/versions/`.
