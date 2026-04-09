# Infrastructure Scaffold

This directory contains the infrastructure layout for local development, deployment support, and operations assets.

## Intended Structure

```text
infra/
|-- backup/                Backup automation and helper scripts
|-- grafana/dashboards/    Provisioned dashboards
|-- keycloak/              Realm export and auth bootstrap material
|-- prometheus/            Metrics scrape configuration
|-- runbooks/              Recovery and operational procedures
`-- traefik/               Reverse proxy configuration
```

Sprint 0 now includes a root-level `docker-compose.yml` that wires the local core stack (`frontend`, `backend`, `postgres`, `mongo`, `minio`, `keycloak`, `traefik`).

## Compose-Related Infrastructure Assets

- `infra/traefik/traefik.yml`: static Traefik configuration used by the Compose `traefik` service.
- `infra/keycloak/realm-import/`: optional realm JSON import location mounted into Keycloak at startup.

## Network and Persistence Model

- `dpp_internal` (internal bridge): `postgres`, `mongo`, `minio`, `keycloak`, `backend`
- `dpp_public` (public bridge): `traefik`, `frontend`, `backend`

Persistent Docker volumes:

- `postgres_data`
- `mongo_data`
- `minio_data`
- `keycloak_data`

## Standardized Local Workflow

1. Copy `.env.example` to `.env` in the repository root.
2. Run `docker compose up -d` from the repository root.
3. Check status with `docker compose ps`.
4. Stop with `docker compose down`.
5. Reset persisted data with `docker compose down -v` when needed.