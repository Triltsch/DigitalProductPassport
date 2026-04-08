# 08 — Backlog & Roadmap

## 1. MVP Definition

The Minimum Viable Product (MVP) delivers a **complete, deployable DPP system** for the industrial manufacturing use case, covering the full end-to-end flow from DPP creation through publication, sharing, and public viewing.

### MVP Scope

**In MVP:**
- AAS shell lifecycle management (create, edit, publish, archive) — `F-AAS-01` to `F-AAS-05`
- Core submodels: Technical Data, Sustainability, Nameplate, Certifications (basic)
- User authentication via Keycloak (OIDC), all 6 roles
- Role-based frontend: Manufacturer and Customer views (full); Auditor view (read-only)
- Submodel validation against IDTA templates (basic required-field check)
- Lifecycle event recording and timeline view
- Basic certification workflow (request → review → approve/reject)
- Access grant management (share DPP with supplier/auditor)
- AASX import/export
- Docker Compose full-stack deployment
- Unit tests (≥ 80% backend), basic E2E tests

**Not in MVP (Phase 2+):**
- Webhook notifications to external systems
- CSV bulk import
- ERP/MES integration adapters
- In-app notification system
- Advanced regulatory exports (JSON-LD, EU Battery Regulation format)
- MFA enforcement (Keycloak config-ready, but not enforced in UX)
- Full Supplier view in frontend
- Monitoring/observability stack (optional Compose profile)

---

## 2. GitHub Issues Structure

Issues are organized in GitHub using the following labels:

| Label | Meaning |
|-------|---------|
| `type: feat` | New feature |
| `type: fix` | Bug fix |
| `type: chore` | Infrastructure, DevOps, tooling |
| `type: doc` | Documentation |
| `type: test` | Tests only |
| `layer: backend` | Backend-only change |
| `layer: frontend` | Frontend-only change |
| `layer: infra` | Docker, CI/CD, config |
| `priority: must` | MVP blocker |
| `priority: should` | Post-MVP target |
| `priority: may` | Optional extension |
| `sprint: N` | Sprint assignment |

---

## 3. Sprint Roadmap

### Sprint 0 — Project Setup (1 week)

| Issue | Type | Description |
|-------|------|-------------|
| #001 | chore/infra | Initialize repository structure (backend/, frontend/, doc/, infra/) |
| #002 | chore/infra | Set up Docker Compose with all containers (PostgreSQL, MongoDB, MinIO, Keycloak, Traefik) |
| #003 | chore/backend | Initialize FastAPI application with health endpoints, config, logging |
| #004 | chore/frontend | Initialize React/Vite project with TypeScript, prettier, eslint |
| #005 | chore/infra | Set up GitHub Actions CI: lint, test, build on every PR |
| #006 | chore/backend | Configure Alembic for PostgreSQL migrations |
| #007 | chore/backend | Keycloak realm configuration and JWT validation middleware |

**Exit criteria:** `docker compose up` launches all services; backend health check returns 200; frontend build succeeds; CI pipeline runs.

---

### Sprint 1 — Core AAS & User Foundation (2 weeks)

| Issue | Type | Description |
|-------|------|-------------|
| #010 | feat/backend | User and Organization domain model + PostgreSQL tables |
| #011 | feat/backend | User sync from Keycloak JWT (`/users/me` endpoint) |
| #012 | feat/backend | AAS Shell CRUD API (MongoDB repository + FastAPI endpoints) |
| #013 | feat/backend | AAS Registry (lookup by assetId) |
| #014 | feat/backend | AAS lifecycle state machine (DRAFT → ACTIVE → ARCHIVED) |
| #015 | feat/backend | BaSyx SDK integration: AAS/Submodel construction and JSON serialization |
| #016 | feat/frontend | Auth flow with Keycloak OIDC (PKCE) — login, logout, token refresh |
| #017 | feat/frontend | Role-adaptive dashboard shell (navigation, role context) |
| #018 | feat/frontend | DPP list page (Manufacturer view) |
| #019 | test/backend | Unit tests for AAS domain model and repository layer |

**Exit criteria:** Authenticated manufacturer can create and list AAS shells via both API and UI.

---

### Sprint 2 — Submodels (2 weeks)

| Issue | Type | Description |
|-------|------|-------------|
| #020 | feat/backend | Submodel CRUD API and MongoDB repository |
| #021 | feat/backend | IDTA Submodel Template definitions for: TechnicalData, Sustainability, Nameplate |
| #022 | feat/backend | Submodel validation (required fields against SMT) |
| #023 | feat/backend | SubmodelElement path addressing (`/submodels/{id}/submodel-elements/{idShortPath}`) |
| #024 | feat/frontend | DPP detail view with submodel sections |
| #025 | feat/frontend | TechnicalData submodel editor form |
| #026 | feat/frontend | Sustainability submodel editor form |
| #027 | feat/frontend | Nameplate submodel viewer |
| #028 | test/backend | Unit + integration tests for Submodel module |

**Exit criteria:** Manufacturer can create a DPP with TechnicalData and Sustainability submodels; validation errors are shown; submodel data persists.

---

### Sprint 3 — Access Control & Sharing (1 week)

| Issue | Type | Description |
|-------|------|-------------|
| #030 | feat/backend | AccessGrant domain model and PostgreSQL table |
| #031 | feat/backend | `AccessPolicy` enforcement in AAS and Submodel services |
| #032 | feat/backend | Access grant CRUD endpoints |
| #033 | feat/frontend | Access management UI (grant, revoke, list) |
| #034 | test/backend | Permission matrix test suite (all role×action combinations) |

**Exit criteria:** Manufacturer can share a DPP with an auditor; auditor sees only granted content; unauthorized access returns 403.

---

### Sprint 4 — Certification & Lifecycle (2 weeks)

| Issue | Type | Description |
|-------|------|-------------|
| #040 | feat/backend | Lifecycle event model and append-only PostgreSQL table |
| #041 | feat/backend | Lifecycle event API endpoints |
| #042 | feat/backend | Certification workflow state machine + API |
| #043 | feat/backend | Certificate issuance and storage (MinIO for documents) |
| #044 | feat/frontend | Lifecycle event timeline component |
| #045 | feat/frontend | Lifecycle event recording form |
| #046 | feat/frontend | Auditor review workflow UI (findings input, approve/reject) |
| #047 | feat/frontend | Certificate viewer with document download |
| #048 | test/backend | Certification workflow state machine tests |

**Exit criteria:** End-to-end flow: Manufacturer submits for certification → Auditor reviews and approves → Certificate attached to DPP.

---

### Sprint 5 — Import/Export & Public View (1 week)

| Issue | Type | Description |
|-------|------|-------------|
| #050 | feat/backend | AASX export (BaSyx SDK packaging) |
| #051 | feat/backend | AASX import with validation |
| #052 | feat/backend | Public DPP endpoint (no auth required, filtered to disclosed fields) |
| #053 | feat/frontend | AASX import UI with preview |
| #054 | feat/frontend | Export buttons (AASX, JSON) |
| #055 | feat/frontend | Public DPP view (Customer view, QR code) |
| #056 | test/backend | Round-trip AASX import/export tests |

**Exit criteria:** Manufacturer can export and re-import an AASX; customer can view public DPP without authentication.

---

### Sprint 6 — Hardening & Production Readiness (1 week)

| Issue | Type | Description |
|-------|------|-------------|
| #060 | chore/backend | Security hardening: rate limiting, CORS config, CSP headers |
| #061 | chore/infra | Production Docker Compose with secrets management |
| #062 | chore/infra | Optional Compose profile: Prometheus + Grafana + Loki |
| #063 | chore/backend | Structured logging (JSON) + request correlation IDs |
| #064 | test | End-to-end (E2E) test suite for MVP user journeys |
| #065 | doc | OpenAPI documentation review and augmentation |
| #066 | chore/infra | Database backup scripts and documentation |

**Exit criteria:** All MVP user journeys covered by E2E tests; Docker Compose production profile starts cleanly; OpenAPI docs are complete.

---

## 4. Post-MVP Roadmap

### Phase 2 — Collaboration & Supplier Integration (Q3)

- Full Supplier frontend view and data submission workflow
- In-app notification system (Celery + WebSocket / SSE)
- Webhook outbound integration for DPP lifecycle events
- Regulator frontend view with structured export
- MFA enforcement for manufacturer/auditor roles
- Submodel template registry (custom SMT upload)

### Phase 3 — Advanced Compliance & Integrations (Q4)

- EU Battery Regulation structured export (JSON-LD, Annex XIII format)
- ESPR product category extensions (additional submodel templates)
- CSV bulk product import
- ERP REST integration adapter (SAP / Odoo plugin)
- ABAC (attribute-based access control) for field-level disclosure

### Phase 4 — Scale & Ecosystem (Q1 next year)

- Kubernetes Helm chart for production deployment
- Multi-region data residency support
- AAS Federation: cross-system registry lookup
- IoT event ingestion (MQTT bridge for live lifecycle events)
- Mobile consumer view (PWA or native wrapper)

---

## 5. Milestones

| Milestone | Target Sprint | Deliverable |
|-----------|--------------|-------------|
| M1: Foundation | Sprint 0 | Running dev environment, CI/CD |
| M2: AAS Core | Sprint 1 | AAS CRUD with auth |
| M3: Full Submodels | Sprint 2 | TechnicalData + Sustainability submodels |
| M4: Access Control | Sprint 3 | RBAC + access grants enforced |
| M5: Certification | Sprint 4 | End-to-end certification workflow |
| M6: MVP | Sprint 6 | Complete, tested, deployable MVP |
| M7: Phase 2 | Phase 2 | Supplier workflow, notifications, webhooks |
| M8: Compliance | Phase 3 | EU Battery Regulation export |
