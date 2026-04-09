# Digital Product Passport

This repository contains the planning artifacts and implementation scaffold for the Digital Product Passport project.

The current state reflects Sprint 0 structure enablement plus a Docker Compose core stack baseline for local full-stack startup. A minimal FastAPI backend foundation is available; application business features are still intentionally deferred to follow-up Sprint 0 issues.

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

## Developer Onboarding

1. Read the planning overview in `doc/planning/README.md`.
2. Use the folder READMEs in `backend/`, `frontend/`, and `infra/` to understand the intended implementation boundaries.
3. Copy `.env.example` to `.env` before running the local stack.
4. Start the local core stack with `docker compose up -d`.
5. Stop and clean up with `docker compose down` (or `docker compose down -v` to remove persisted data).

## Current Boundaries

- The backend now includes a minimal runnable FastAPI foundation with configuration and health endpoints under `backend/app`.
- Frontend now includes a React/TypeScript foundation with build, lint, format, and test tooling; business feature implementation is still pending.
- The directory structure mirrors the architecture described in `doc/planning/05_system_architecture.md` and `doc/planning/07_modules.md`.
- The Compose `backend` service still uses a scaffold-safe placeholder command until dedicated containerization follow-up work is implemented.

## Local Core Stack (Sprint 0)

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

## Related Planning Documents

- `doc/planning/05_system_architecture.md`
- `doc/planning/07_modules.md`
- `doc/planning/08_backlog_roadmap.md`
- `doc/planning/10_operations_observability.md`