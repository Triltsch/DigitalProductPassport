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
- Keycloak JWT validation primitives in `app/infrastructure/keycloak/` and FastAPI dependency helpers in `app/dependencies.py`.

## Local run

The recommended setup uses the repository-root virtual environment `.aas_py`.

From the repository root:

```powershell
python -m venv .aas_py
.\.aas_py\Scripts\python -m pip install -e ".\backend[test]"
```

From the `backend/` folder:

```powershell
..\.aas_py\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Local tests

From the `backend/` folder:

```powershell
..\.aas_py\Scripts\python -m pytest
```

## Local migrations

The backend uses Alembic for relational schema migrations.

From the `backend/` folder:

```powershell
..\.aas_py\Scripts\python -m alembic current
..\.aas_py\Scripts\python -m alembic revision -m "describe change"
..\.aas_py\Scripts\python -m alembic upgrade head
```

Notes:

- Alembic reads `DATABASE_URL` from the repository `.env` file via `app.config.Settings`.
- Async PostgreSQL URLs (`postgresql+asyncpg://...`) are converted automatically to a synchronous `psycopg` URL for migration runs.
- Migration scripts belong in `app/infrastructure/db/migrations/versions/`.

## Local authentication baseline

The backend now carries the configuration contract and validation primitives for Keycloak-issued JWTs.

Required environment variables:

- `KEYCLOAK_ISSUER_URL`
- `JWT_AUDIENCE`
- `JWT_ALGORITHM`
- `KEYCLOAK_FRONTEND_CLIENT_ID`
- `KEYCLOAK_BACKEND_CLIENT_ID`

Derived endpoints:

- OpenID configuration: `KEYCLOAK_ISSUER_URL/.well-known/openid-configuration`
- JWKS: `KEYCLOAK_ISSUER_URL/protocol/openid-connect/certs`

Implementation notes:

- `app.infrastructure.keycloak.auth.KeycloakTokenValidator` verifies signature, issuer, audience, and expiry.
- `app.dependencies.get_current_user` and `app.dependencies.require_roles(...)` are ready for future protected routers such as `/users/me`.
- The local development realm import is defined in `../infra/keycloak/realm-import/dpp-realm.json`.
