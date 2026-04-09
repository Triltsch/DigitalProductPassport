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
|-- pyproject.toml         Project dependencies and pytest config
|-- Dockerfile             Added in a later Sprint 0 issue
`-- alembic.ini            Added in a later Sprint 0 issue
```

## Implemented in this foundation

- FastAPI app factory in `app/main.py`.
- Environment-variable configuration via Pydantic settings in `app/config.py`.
- Base structured logging initialization in `app/logging.py`.
- Health endpoints:
	- `GET /health/live`
	- `GET /health/ready`
- Initial backend tests for settings and health routes.

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