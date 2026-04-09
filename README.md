# Digital Product Passport

This repository contains the planning artifacts and implementation scaffold for the Digital Product Passport project.

## Current Status

- Sprint 0 foundation is in place for infrastructure, backend, frontend, and CI quality gates.
- The backend includes a runnable FastAPI scaffold and an Alembic PostgreSQL migration baseline.
- Keycloak realm import and backend JWT validation foundations are prepared for upcoming auth flows.
- The frontend includes a React/TypeScript scaffold with lint, typecheck, format, test, and build tooling.
- Product features are intentionally deferred to follow-up sprint issues.

## Sprint 0 Scope

### Completed

- Core local platform via Docker Compose (`frontend`, `backend`, `postgres`, `mongo`, `minio`, `keycloak`, `traefik`).
- Backend scaffold under `backend/app` with health/config foundations.
- PostgreSQL migration baseline via Alembic in `backend/app/infrastructure/db/migrations`.
- Keycloak realm baseline in `infra/keycloak/realm-import/dpp-realm.json` and backend JWT validation primitives in `backend/app/infrastructure/keycloak`.
- Frontend foundation with Vite/React/TypeScript tooling.
- CI baseline at `.github/workflows/ci.yml` for backend and frontend verification.

### Next Steps

1. Replace the scaffold-safe backend container command with dedicated containerization work.
2. Implement first business feature slices aligned with planning documents.
3. Extend CI and runtime observability as feature modules are introduced.

## Quick Start

1. Read the planning overview in `doc/planning/README.md`.
2. Use folder READMEs in `backend/`, `frontend/`, and `infra/` for module boundaries.
3. Create a local Python virtual environment for backend work:
	- `python -m venv .aas_py`
4. Install backend dependencies with the venv interpreter:
	- `.\.aas_py\Scripts\python -m pip install -e ".\backend[test]"`
5. Copy `.env.example` to `.env`.
6. Start the stack: `docker compose up -d`.
7. Stop the stack: `docker compose down` (or `docker compose down -v` to remove persisted data).

## Local Core Stack

The root `docker-compose.yml` defines the Sprint 0 core services:

- `frontend`
- `backend`
- `postgres`
- `mongo`
- `minio`
- `keycloak`
- `traefik`

### Networks

- `dpp_internal`: internal-only bridge network for data and auth services.
- `dpp_public`: bridge network exposed through Traefik.

### Persistent Volumes

- `postgres_data`
- `mongo_data`
- `minio_data`
- `keycloak_data`

### Local Endpoints

- Frontend via Traefik: `http://dpp.localhost`
- Backend via Traefik: `http://api.dpp.localhost`
- Traefik dashboard: disabled by default in this scaffold for safer local defaults
- Keycloak direct access: `http://localhost:8080`
- MinIO API/Console: `http://localhost:9000` / `http://localhost:9001`

## Continuous Integration

The repository includes a CI workflow at `.github/workflows/ci.yml`.

- Trigger: pull requests to `main` and direct pushes to `main`
- Backend job: `python -m ruff check`, `python -m pytest`, and `python -m build --wheel`
- Frontend job: `npm run lint`, `npm run typecheck`, `npm run format:check`, `npm run test:run`, and `npm run build`

## Repository Layout

```text
.
|-- backend/        Python/FastAPI service scaffold and test layout
|-- doc/            Planning, seed material, and project documentation
|-- frontend/       React/TypeScript application scaffold layout
|-- infra/          Docker, auth, observability, and operations scaffold
|-- LEARNINGS.md    Repository learnings captured during implementation
`-- ensure-milestones.ps1
```

## Planning References

- `doc/planning/05_system_architecture.md`
- `doc/planning/07_modules.md`
- `doc/planning/08_backlog_roadmap.md`
- `doc/planning/10_operations_observability.md`