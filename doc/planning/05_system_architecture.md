# 05 — System Architecture

## 1. Architecture Decision: Modular Monolith First

**Decision:** Start with a **modular monolith** (single deployable backend service with clearly bounded internal modules), not microservices.

**Rationale:**
- Reduces operational complexity significantly for a new project
- Bounded internal modules allow extraction to microservices later without rewriting business logic
- BaSyx Python SDK is a library, not a separate service, which fits a single process model
- All required capabilities (AAS API, auth, data management) fit within one process at MVP scale

**Migration path:** Individual modules (e.g., notification service, certificate service) can be extracted when team or scale requires it.

See [11_risks_decisions.md](./11_risks_decisions.md) — ADR-001.

---

## 2. Backend Architecture

### 2.1 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.11+ |
| Web framework | FastAPI | 0.110+ |
| AAS library | BaSyx Python SDK | latest stable |
| ORM | SQLAlchemy 2.x (async) | 2.x |
| DB migrations | Alembic | latest |
| Async runtime | asyncio / uvicorn | - |
| Task queue | Celery + Redis | (for notifications, async exports) |
| Validation | Pydantic v2 | - |
| Auth middleware | python-jose / authlib | - |

### 2.2 Backend Module Structure

```
backend/
├── app/
│   ├── main.py                   # FastAPI app factory
│   ├── config.py                 # Settings (Pydantic BaseSettings)
│   ├── dependencies.py           # FastAPI DI: db sessions, current user
│   │
│   ├── api/                      # API layer (routers)
│   │   ├── v1/
│   │   │   ├── aas.py            # AAS Shell endpoints
│   │   │   ├── submodels.py      # Submodel endpoints
│   │   │   ├── registry.py       # AAS Registry endpoints
│   │   │   ├── lifecycle.py      # Lifecycle event endpoints
│   │   │   ├── certificates.py   # Certificate endpoints
│   │   │   ├── workflows.py      # Certification workflow endpoints
│   │   │   ├── users.py          # User management endpoints
│   │   │   ├── organizations.py  # Tenant management endpoints
│   │   │   └── exports.py        # AASX / JSON-LD export endpoints
│   │   └── health.py             # /health/live and /health/ready
│   │
│   ├── domain/                   # Pure domain logic (no FastAPI, no DB)
│   │   ├── aas/
│   │   │   ├── shell.py          # AAS domain entity and business rules
│   │   │   ├── submodel.py       # Submodel domain logic
│   │   │   └── validator.py      # SMT validation against IDTA templates
│   │   ├── lifecycle/
│   │   │   └── events.py         # Lifecycle event domain logic
│   │   ├── certification/
│   │   │   ├── workflow.py       # Certification workflow state machine
│   │   │   └── certificate.py    # Certificate domain entity
│   │   └── access/
│   │       └── grants.py         # Access grant domain logic
│   │
│   ├── services/                 # Application services (orchestrate domain + infra)
│   │   ├── aas_service.py
│   │   ├── submodel_service.py
│   │   ├── lifecycle_service.py
│   │   ├── certification_service.py
│   │   ├── export_service.py      # AASX/JSON-LD packaging
│   │   └── notification_service.py
│   │
│   ├── infrastructure/           # DB, file storage, external integrations
│   │   ├── db/
│   │   │   ├── session.py        # Async SQLAlchemy session factory
│   │   │   ├── models/           # SQLAlchemy ORM models (persistence model)
│   │   │   │   ├── aas_model.py
│   │   │   │   ├── user_model.py
│   │   │   │   ├── event_model.py
│   │   │   │   └── …
│   │   │   └── migrations/       # Alembic migration scripts
│   │   ├── mongo/
│   │   │   ├── client.py         # Motor (async MongoDB) client
│   │   │   └── repositories/     # AAS object repositories (MongoDB)
│   │   ├── storage/
│   │   │   └── minio_client.py   # MinIO file storage client
│   │   └── keycloak/
│   │       └── auth.py           # JWT validation, user sync
│   │
│   └── tasks/                    # Celery async tasks
│       ├── export_tasks.py
│       └── notification_tasks.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── Dockerfile
├── pyproject.toml
└── alembic.ini
```

### 2.3 BaSyx Python SDK Integration

The BaSyx Python SDK is used as the **domain library** for:
- Constructing AAS and Submodel objects in-memory
- Serializing to/from JSON (AAS Part 2) and AASX formats
- Validating AAS structures (type checking, required attributes)

The SDK is **not** used as a server — FastAPI provides the HTTP layer. The BaSyx object model maps directly to the domain entities in `app/domain/aas/`.

```python
# Example: Using BaSyx SDK to construct an AAS
import basyx.aas.model as aas_model

shell = aas_model.AssetAdministrationShell(
    id="urn:acme-corp:battery:ACM-001:BT47-PRO:SN-001",
    asset_information=aas_model.AssetInformation(
        global_asset_id="urn:acme-corp:battery:ACM-001:BT47-PRO:SN-001",
        asset_kind=aas_model.AssetKind.INSTANCE,
    ),
)
```

### 2.4 API Design

All API endpoints follow the **IDTA AAS REST API Specification** where applicable. Custom DPP endpoints (workflows, access grants) follow the same RESTful conventions.

Base path: `/api/v1/`

| Endpoint Group | Base Path | Source |
|----------------|-----------|--------|
| AAS Registry | `/api/v1/registry/` | IDTA AAS API Part 2 |
| AAS Repository | `/api/v1/shells/` | IDTA AAS API Part 2 |
| Submodel Repository | `/api/v1/submodels/` | IDTA AAS API Part 2 |
| Lifecycle Events | `/api/v1/lifecycle/` | Custom DPP extension |
| Certifications | `/api/v1/certificates/` | Custom DPP extension |
| Certification Workflows | `/api/v1/workflows/` | Custom DPP extension |
| Access Grants | `/api/v1/access-grants/` | Custom DPP extension |
| Import/Export | `/api/v1/exports/`, `/api/v1/imports/` | Custom |
| Users | `/api/v1/users/` | Custom |
| Health | `/health/live`, `/health/ready` | Custom |

OpenAPI documentation is auto-generated by FastAPI and served at `/docs` (development only).

---

## 3. Persistence Architecture

### 3.1 Database Strategy: Hybrid Persistence

Two databases are used for different concerns:

#### PostgreSQL — Relational Store
**Used for:** Users, organizations, access grants, audit logs, workflow management, lifecycle event metadata, certificate records (metadata only, not binary).

**Rationale:** ACID transactions, rich querying, foreign key integrity, battle-tested for auth and workflow data.

#### MongoDB — Document Store
**Used for:** AAS shell objects, submodel objects, submodel element hierarchies as JSON documents.

**Rationale:**
- AAS/Submodel objects are naturally hierarchical JSON documents with variable schema
- BaSyx SDK serializes natively to JSON; document store avoids O/RM impedance mismatch
- Flexible submodel structure (user-defined submodels) maps poorly to fixed SQL schema
- MongoDB supports rich JSON querying including `semanticId` lookups

#### MinIO — Object Storage
**Used for:** Binary files (certificate PDFs, uploaded documents, AASX package files, product images).

**Rationale:** Decouples blob storage from both relational and document stores. S3-compatible API allows easy swap to AWS S3/GCS in production.

### 3.2 Data Model Separation

Three distinct model layers are maintained:

| Layer | Location | Purpose |
|-------|----------|---------|
| **Domain Model** | `app/domain/` + BaSyx SDK | Business rules, in-memory AAS objects |
| **Persistence Model** | `app/infrastructure/db/` | SQLAlchemy ORM for PostgreSQL; MongoDB documents |
| **API Model** | `app/api/v1/` + Pydantic schemas | Request/response contracts; never expose ORM models directly |

Domain ↔ Persistence mapping is done in service layer; services return domain objects, repositories translate to/from persistence models.

### 3.3 Migration Strategy

- **PostgreSQL schema** is managed with **Alembic**; migrations are auto-generated from ORM model changes and stored under `infrastructure/db/migrations/`.
- **MongoDB** does not use schema migrations; schema evolution is handled by:
  - Backward-compatible document evolution (add-only field approach)
  - Versioned AAS JSON serialization (BaSyx SDK handles version compatibility)
  - A migration utility for one-off structural changes when needed
- All database credentials are injected via environment variables; no hardcoded credentials.

---

## 4. Frontend Architecture

### 4.1 Technology Stack

| Component | Technology |
|-----------|-----------|
| Framework | React 18 (TypeScript) |
| State management | Zustand (lightweight, per-feature stores) |
| API client | TanStack Query (data fetching, caching) + Axios |
| UI component library | shadcn/ui (Radix UI + Tailwind CSS) |
| Routing | React Router v6 |
| Auth | OIDC client (`oidc-client-ts`) |
| Form handling | React Hook Form + Zod validation |
| Build tooling | Vite |
| Testing | Vitest + Testing Library |

### 4.2 Frontend Module Structure

```
frontend/
├── src/
│   ├── main.tsx                    # App entry point
│   ├── App.tsx                     # Root component, routing setup
│   │
│   ├── auth/                       # OIDC auth context and hooks
│   │   ├── AuthProvider.tsx
│   │   └── useAuth.ts
│   │
│   ├── features/                   # Feature-based organization
│   │   ├── dashboard/              # Role-adaptive dashboard
│   │   ├── dpp/                    # DPP list, detail, create/edit forms
│   │   ├── submodels/              # Per-submodel editors and viewers
│   │   ├── lifecycle/              # Lifecycle event timeline
│   │   ├── certifications/         # Certificate viewer and issuer
│   │   ├── workflows/              # Certification workflow UI
│   │   ├── access-management/      # Grant/revoke access UI
│   │   ├── import-export/          # AASX import/export UI
│   │   └── admin/                  # User, organization management
│   │
│   ├── components/                 # Shared UI components
│   │   ├── AASCard.tsx
│   │   ├── SubmodelViewer.tsx
│   │   ├── RoleGuard.tsx           # Conditional rendering by role
│   │   ├── QRCodeDisplay.tsx
│   │   └── …
│   │
│   ├── api/                        # TanStack Query hooks + Axios clients
│   │   ├── aas.api.ts
│   │   ├── submodels.api.ts
│   │   └── …
│   │
│   ├── types/                      # TypeScript types (domain + API models)
│   └── utils/                      # Helpers, formatters
│
├── Dockerfile
├── nginx.conf                      # nginx config for production SPA serving
├── vite.config.ts
├── tsconfig.json
└── package.json
```

### 4.3 Role-Adaptive Views

The `RoleGuard` component wraps any UI section with a role check:
```tsx
<RoleGuard roles={["MANUFACTURER", "ADMIN"]}>
  <EditSubmodelButton />
</RoleGuard>
```

The backend enforces the same permission rules independently. The frontend guard is a UX convenience only.

---

## 5. Docker Deployment Topology

### 5.1 Container Overview

See [10_operations_observability.md](./10_operations_observability.md) for full Docker Compose specification.

```
                    ┌─────────────────────────────────────────────────┐
Internet/Dev ──────▶│  traefik (port 80/443)                          │
                    └────┬────────────────────────────────────────────┘
                         │ routes by Host / path prefix
           ┌─────────────┼─────────────────────────────────────┐
           ▼             ▼                                      ▼
      ┌─────────┐  ┌──────────┐                        ┌──────────────┐
      │ frontend│  │ backend  │                        │  keycloak    │
      │ (nginx) │  │(FastAPI) │                        │  (OIDC IdP)  │
      └─────────┘  └────┬─────┘                        └──────┬───────┘
                        │                                     │
           ┌────────────┼──────────────┐                      │
           ▼            ▼              ▼                       ▼
      ┌──────────┐ ┌──────────┐ ┌──────────┐          ┌──────────────┐
      │ postgres │ │ mongodb  │ │  minio   │          │  keycloak_db │
      └──────────┘ └──────────┘ └──────────┘          │  (postgres)  │
                                                      └──────────────┘
      ┌──────────┐ ┌──────────┐ ┌──────────┐
      │  redis   │ │prometheus│ │ grafana  │
      └──────────┘ └──────────┘ └──────────┘
                                     │
                               ┌─────┴──────┐
                               │    loki    │
                               └────────────┘
```

### 5.2 Network Segmentation

- **Frontend network:** traefik ↔ frontend
- **Backend network:** traefik ↔ backend ↔ postgres, mongodb, minio, redis
- **Auth network:** traefik ↔ keycloak ↔ keycloak_db
- **Observability network:** prometheus ↔ backend, grafana ↔ prometheus, loki ↔ all

Database containers are **not exposed** to the traefik/public network.

---

## 6. Interfaces Summary

| Interface | Protocol | Standard | Consumer |
|-----------|----------|----------|----------|
| AAS REST API | HTTP/HTTPS | IDTA AAS API Part 2 | Frontend, External systems |
| DPP Custom API | HTTP/HTTPS | OpenAPI 3.1 | Frontend |
| Auth (OIDC) | HTTP/HTTPS | OAuth 2.0 / OIDC | Frontend, Backend |
| File storage | HTTP/HTTPS | S3-compatible | Backend |
| Event webhooks | HTTP/HTTPS | Custom (JSON payload) | External integrations |
| AASX Import/Export | File | AASX (ZIP+JSON) | Users, External systems |
| Metrics | HTTP | Prometheus exposition format | Prometheus |
| Logs | HTTP | Loki push API | Application containers |
