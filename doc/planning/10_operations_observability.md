# 10 — Operations & Observability

## 1. Docker Compose Architecture

The full system is orchestrated via Docker Compose. Two profiles are maintained:

- **`dev`** (default): All core services + file storage + auth + optional observability
- **`prod`**: Same as `dev` with production-grade secrets injection, TLS, and hardened configuration

### 1.1 Full Docker Compose Service Map

```yaml
# docker-compose.yml (conceptual — annotated overview)

services:
  # ── Core Services ────────────────────────────────────────────────
  
  traefik:                      # Reverse proxy, TLS termination, routing
    image: traefik:v3
    ports: ["80:80", "443:443"]
    networks: [proxy]

  frontend:                     # React SPA (nginx-served)
    build: ./frontend
    networks: [proxy]
    labels: [traefik routing for ui.dpp.local]

  backend:                      # FastAPI + BaSyx DPP service
    build: ./backend
    networks: [proxy, backend]
    environment:
      - DATABASE_URL
      - MONGODB_URI
      - MINIO_ENDPOINT
      - KEYCLOAK_ISSUER_URL
      - JWT_AUDIENCE
    depends_on: [postgres, mongo, minio, keycloak]

  worker:                       # Celery background task worker
    build: ./backend
    command: celery -A app.tasks worker
    networks: [backend]
    depends_on: [redis, postgres]

  # ── Persistence ──────────────────────────────────────────────────

  postgres:                     # Relational DB (users, metadata, audit)
    image: postgres:16-alpine
    volumes: [postgres_data:/var/lib/postgresql/data]
    networks: [backend, auth]
    environment:
      - POSTGRES_DB
      - POSTGRES_USER
      - POSTGRES_PASSWORD

  mongo:                        # Document store (AAS objects, submodels)
    image: mongo:7
    volumes: [mongo_data:/data/db]
    networks: [backend]

  redis:                        # Celery broker + result backend
    image: redis:7-alpine
    networks: [backend]

  minio:                        # S3-compatible file storage
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    volumes: [minio_data:/data]
    networks: [backend, proxy]
    labels: [traefik routing for files.dpp.local]

  # ── Auth ─────────────────────────────────────────────────────────

  keycloak:                     # OIDC Identity Provider
    image: quay.io/keycloak/keycloak:24
    command: start-dev --import-realm
    volumes: [./infra/keycloak/realm-export.json:/opt/keycloak/data/import/realm.json]
    networks: [proxy, auth]
    depends_on: [keycloak_db]
    labels: [traefik routing for auth.dpp.local]

  keycloak_db:                  # Dedicated Postgres for Keycloak
    image: postgres:16-alpine
    networks: [auth]

  # ── Observability (profile: observability) ───────────────────────

  prometheus:
    image: prom/prometheus:latest
    profiles: [observability]
    volumes: [./infra/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml]
    networks: [monitoring]

  grafana:
    image: grafana/grafana:latest
    profiles: [observability]
    volumes: [grafana_data:/var/lib/grafana]
    networks: [monitoring, proxy]
    labels: [traefik routing for grafana.dpp.local]

  loki:
    image: grafana/loki:latest
    profiles: [observability]
    networks: [monitoring]

  promtail:
    image: grafana/promtail:latest
    profiles: [observability]
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks: [monitoring]

networks:
  proxy:         # Traefik-facing; frontend, backend, keycloak, minio
  backend:       # Internal: backend ↔ postgres, mongo, redis, minio
  auth:          # Auth: keycloak ↔ postgres ↔ backend
  monitoring:    # Observability: prometheus, grafana, loki, promtail

volumes:
  postgres_data:
  mongo_data:
  minio_data:
  grafana_data:
```

---

## 2. Local Development Environment

### 2.1 Getting Started

```bash
# 1. Clone repository
git clone https://github.com/Triltsch/DigitalProductPassport.git
cd DigitalProductPassport

# 2. Copy and populate environment file
cp .env.example .env
# Edit .env with local secrets (see .env.example for required variables)

# 3. Start core services
docker compose up -d

# 4. Run database migrations
docker compose exec backend alembic upgrade head

# 5. (Optional) Start with observability
docker compose --profile observability up -d
```

### 2.2 Development Mode (Hot Reload)

For active development, each service can be run locally with hot reload while databases run in Docker:

```bash
# Start only infrastructure containers
docker compose up -d postgres mongo redis minio keycloak keycloak_db traefik

# Backend (hot reload)
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Frontend (hot reload)
cd frontend
npm install
npm run dev  # Vite dev server on port 5173
```

A `docker-compose.override.yml` file is provided for development that:
- Mounts source directories into containers (no rebuild needed)
- Enables debug ports
- Disables TLS for local convenience
- Sets `LOG_LEVEL=DEBUG`

### 2.3 Keycloak Development Setup

The Keycloak development realm is pre-configured via `infra/keycloak/realm-export.json`:
- Realm: `dpp`
- Pre-configured clients: `dpp-frontend` (PKCE), `dpp-backend` (confidential)
- Pre-created test users per role (see `infra/keycloak/README.md`)
- Default passwords for dev only — never use in production

### 2.4 Environment Variables

All services read configuration from environment variables. A `.env.example` file documents all required variables without real values:

```bash
# Backend
DATABASE_URL=postgresql+asyncpg://dpp:changeme@postgres:5432/dpp
MONGODB_URI=mongodb://mongo:27017/dpp
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=changeme
KEYCLOAK_ISSUER_URL=http://keycloak:8080/realms/dpp
JWT_AUDIENCE=dpp-backend
CELERY_BROKER_URL=redis://redis:6379/0
LOG_LEVEL=INFO
SECRET_KEY=changeme-long-random-string

# Keycloak DB
KEYCLOAK_DB_NAME=keycloak
KEYCLOAK_DB_USER=keycloak
KEYCLOAK_DB_PASSWORD=changeme

# Postgres (DPP)
POSTGRES_DB=dpp
POSTGRES_USER=dpp
POSTGRES_PASSWORD=changeme
```

---

## 3. Production Deployment

### 3.1 Secrets Management

- In production, replace `.env` file values with **Docker Secrets** (Swarm mode) or mount from a secrets manager (HashiCorp Vault, AWS Parameter Store).
- `docker-compose.prod.yml` overrides the base Compose file with secrets file references:
  ```yaml
  services:
    backend:
      secrets:
        - db_password
        - jwt_secret
  secrets:
    db_password:
      external: true  # Pre-created via `docker secret create`
    jwt_secret:
      external: true
  ```

### 3.2 TLS in Production

- Traefik handles TLS with **Let's Encrypt** via ACME challenge.
- Domain names are configured in `traefik/traefik.yml` or via Traefik labels.
- Local dev uses a self-signed cert generated at startup.

### 3.3 Container Health Checks

All application containers define `HEALTHCHECK` instructions:
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health/live || exit 1
```

Compose `depends_on` conditions use `service_healthy` to ensure correct startup order.

---

## 4. Monitoring

### 4.1 Metrics (Prometheus + Grafana)

The backend exposes a `/metrics` endpoint (Prometheus exposition format) via `prometheus-fastapi-instrumentator`:

**Key metrics exposed:**

| Metric | Description |
|--------|-------------|
| `http_requests_total` | Request count by method, path, status |
| `http_request_duration_seconds` | Request duration histogram |
| `dpp_shells_total` | Total AAS shells by state |
| `dpp_submodels_total` | Total submodels by type |
| `dpp_lifecycle_events_total` | Events recorded |
| `dpp_certifications_total` | Certifications by status |
| `celery_tasks_total` | Task count by type and result |
| `db_pool_size` / `db_pool_checked_out` | Database connection pool |

**Grafana Dashboards** (provisioned via `infra/grafana/dashboards/`):
- DPP Overview: total passports, events, certifications
- API Performance: request rate, latency percentiles (p50, p95, p99)
- Database Health: connection pool, slow queries
- Celery Worker: task queue depth, failure rate

---

## 5. Logging

### 5.1 Structured Logging

All services use **structured JSON logging**:

```json
{
  "timestamp": "2025-09-01T14:23:11.123Z",
  "level": "INFO",
  "service": "dpp-backend",
  "logger": "app.services.aas_service",
  "message": "AAS shell published",
  "correlation_id": "c3a1b9f2-...",
  "user_id": "a1b2c3...",
  "tenant_id": "t1x2y3...",
  "aas_id": "urn:acme-corp:...",
  "duration_ms": 142
}
```

**Logging rules:**
- Log level `INFO` for all business-significant operations (create, publish, approve, etc.)
- Log level `WARNING` for non-critical failures (validation errors, denied access attempts)
- Log level `ERROR` for unhandled exceptions (always include `traceback`)
- Log level `DEBUG` for detailed tracing — disabled in production by default
- Never log raw JWT tokens, passwords, or full request bodies containing sensitive data
- All requests are tagged with a `correlation_id` (generated at the API gateway or by the backend)

### 5.2 Log Aggregation (Loki)

Promtail scrapes Docker container logs and forwards to Loki with the following labels:
- `service`: container name
- `level`: extracted from JSON log
- `environment`: `dev` / `prod`

Grafana is pre-configured to query Loki with the DPP log dashboard.

---

## 6. Backup & Recovery

### 6.1 Database Backup Strategy

| Database | Method | Schedule | Retention |
|----------|--------|----------|-----------|
| PostgreSQL | `pg_dump` daily backup to MinIO | Daily 03:00 UTC | 30 days |
| MongoDB | `mongodump` daily backup to MinIO | Daily 03:30 UTC | 30 days |
| MinIO | Versioned bucket (self-backup) + rsync to offsite | Daily | 30 days |

Backup scripts are located in `infra/backup/` and run as Compose one-shot containers on a cron schedule.

### 6.2 Recovery Procedure

Recovery runbooks are documented in `infra/runbooks/database-recovery.md`. At minimum, the runbook covers:
1. Stop affected containers gracefully
2. Restore from the most recent backup
3. Verify data integrity
4. Restart services and confirm health checks pass

---

## 7. Configuration Management

- All environment-specific configuration is externalized to `.env` files and environment variables.
- Configuration is centralized in the backend at `app/config.py` using `pydantic-settings`:
  ```python
  class Settings(BaseSettings):
      database_url: str
      mongodb_uri: str
      keycloak_issuer_url: str
      # ...
      class Config:
          env_file = ".env"
  ```
- Feature flags (e.g., `ENABLE_WEBHOOKS=true`) are supported at the settings level.
- No application logic reads from files at runtime (except mounted secrets); all config through env vars.
