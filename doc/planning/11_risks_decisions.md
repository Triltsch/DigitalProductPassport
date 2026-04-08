# 11 — Risks & Decisions

## Part A: Architecture Decision Records (ADRs)

---

### ADR-001: Modular Monolith Over Microservices

**Status:** Accepted  
**Date:** 2025

**Context:**  
The DPP system requires multiple concerns (AAS management, auth, workflows, notifications) that could be separated into microservices. However, the team is small, the domain is being established, and distributed systems add significant operational overhead (service discovery, distributed tracing, network latency, eventual consistency).

**Decision:**  
Build a **modular monolith** where each concern is a clearly bounded internal module with defined interfaces. All modules run in a single Python process.

**Consequences:**
- Lower operational complexity (single process, single deployment unit)
- Simplified inter-module calls (direct function calls, no network)
- Well-defined module boundaries allow extraction to microservices later
- Risk: a bug in one module can affect the whole process (mitigated by robust error handling and per-module tests)

**Migration path:** If a specific module (e.g., notifications, export) needs independent scaling, it can be extracted while keeping the same API contracts.

---

### ADR-002: MongoDB for AAS Object Storage

**Status:** Accepted  
**Date:** 2025

**Context:**  
AAS shells and submodels are hierarchical JSON documents with variable schema. BaSyx Python SDK serializes them to JSON natively. Options considered:

| Option | Pros | Cons |
|--------|------|------|
| PostgreSQL (JSONB) | Single DB, ACID | Poor schema flexibility, JSON query limits |
| **MongoDB** | Native JSON, flexible schema, good query support | Eventual consistency risks, separate DB to operate |
| Object storage only | Simplest | No queryability |

**Decision:**  
Use **MongoDB** for AAS/Submodel document storage. PostgreSQL is retained for relational data (users, audit, metadata) where ACID transactions are required.

**Consequences:**
- Native JSON mapping to BaSyx SDK objects with no ORM impedance mismatch
- Flexible handling of user-defined submodels without schema migrations
- Need to carefully design indexing strategy for AAS lookup queries
- Operators must manage two database systems

---

### ADR-003: Keycloak as Identity Provider

**Status:** Accepted  
**Date:** 2025

**Context:**  
Authentication and authorization for a multi-tenant product system requires:
- OIDC / OAuth 2.0 compliant flows
- Multi-tenant role management
- Support for MFA
- Possibility to federate with enterprise identity systems (future)

Options: Custom JWT auth, Auth0, Keycloak, Authentik.

**Decision:**  
Use **Keycloak** as the central IdP.

**Rationale:**
- Full OIDC/OAuth 2.0 compliance
- Open source (Apache 2.0) — no vendor lock-in
- Mature multi-tenant and RBAC capabilities
- MFA (TOTP, WebAuthn) built-in
- Widely adopted in enterprise/industrial settings
- Docker image available; integrates cleanly with the container stack

**Consequences:**
- Adds operational complexity (Keycloak needs its own DB)
- Realm configuration must be version-controlled and importable (`realm-export.json`)
- Team needs Keycloak administration knowledge

---

### ADR-004: React (TypeScript) with shadcn/ui for Frontend

**Status:** Accepted  
**Date:** 2025

**Context:**  
The frontend requires role-adaptive views, complex form handling (submodel editors), and future extensibility. Options: React, Vue, Angular, SvelteKit.

**Decision:**  
Use **React 18 with TypeScript** and **shadcn/ui** (Radix UI + Tailwind CSS) as the component system.

**Rationale:**
- Largest ecosystem, most GitHub Copilot and AI tooling support
- TypeScript provides type safety aligned with the backend Pydantic models
- shadcn/ui components are fully accessible, customizable without a heavy opinionated design system
- Vite provides fast development builds
- TanStack Query simplifies server state management (caching, refetching)

---

### ADR-005: No Blockchain for Certificate Integrity

**Status:** Accepted  
**Date:** 2025

**Context:**  
Blockchain has been proposed for certificate and audit trail tamper-proofing (immutable ledger). Options: Ethereum/Hyperledger (on-chain), hash anchoring to public chain, centralized hash log.

**Decision:**  
**Do not use blockchain** in the current system. Use:
- PostgreSQL audit log with append-only rows (no application-level delete/update)
- SHA-256 hash of certificate documents stored alongside the document reference
- Audit log entries contain a hash of the previous entry (hash chain approach) for tamper evidence

**Rationale:**
- Blockchain adds significant complexity with minimal practical benefit for a centralized system
- Regulatory acceptance of blockchain-based DPPs is still evolving
- Hash chain in PostgreSQL provides comparable tamper evidence without blockchain infrastructure
- The architectural separation allows a future blockchain anchor layer to be added without redesign

**Reconsidered when:** A specific regulatory requirement mandates blockchain attestation, or a federated multi-party scenario requires decentralized trust.

---

### ADR-006: Traefik as Reverse Proxy

**Status:** Accepted  
**Date:** 2025

**Context:**  
A reverse proxy is needed for TLS termination, routing, and load balancing across services. Options: nginx, Traefik, Caddy, HAProxy.

**Decision:**  
Use **Traefik v3**.

**Rationale:**
- Native Docker Compose label-based configuration (no separate config files for routing)
- Built-in Let's Encrypt ACME support
- Dynamic routing without restart on container change
- Kubernetes-compatible (Traefik Ingress controller) for future migration
- Middleware support for rate limiting, auth, headers

---

### ADR-007: BaSyx Python SDK as AAS Library

**Status:** Accepted  
**Date:** 2025

**Context:**  
The BaSyx Python SDK is the reference implementation of the AAS metamodel for Python. It enables:
- Constructing AAS Part 1 v3.0 compliant objects
- JSON serialization (AAS Part 2)
- AASX packaging/unpacking

**Decision:**  
Use the **BaSyx Python SDK** as the primary AAS library. FastAPI provides the HTTP layer; the SDK is used as a library, not a standalone server.

**Consequences:**
- The system inherits the SDK's AAS standard compliance
- SDK updates may require domain model adjustments when AAS standard evolves
- SDK is open source (Eclipse Public License 2.0 / Apache 2.0); compatible with commercial use

---

## Part B: Risk Register

| ID | Risk | Probability | Impact | Severity | Mitigation | Owner |
|----|------|------------|--------|----------|-----------|-------|
| R-01 | BaSyx SDK API changes break domain integration | Medium | High | High | Pin SDK version; wrap SDK calls behind a dedicated adapter layer | Backend Lead |
| R-02 | AAS standard evolves (Part 1 v4.0) during development | Medium | Medium | Medium | Design AAS layer as versioned adapter; test against current version explicitly | Architect |
| R-03 | MongoDB performance degrades with large submodel hierarchies | Low | High | Medium | Benchmark with realistic data volumes early; add field-level indexing; consider document size limits | Backend Lead |
| R-04 | Keycloak configuration drift (realm config diverges from code) | Medium | High | High | Realm export is version-controlled; CI checks export matches live realm on every deployment | DevOps |
| R-05 | GDPR compliance gap (personal data in AAS content) | Low | High | Medium | Data classification analysis before submodel definition; GDPR review in security testing phase | Legal+Dev |
| R-06 | EU DPP regulation requirements shift (ESPR specifics not finalized) | High | Medium | High | Build extensible submodel architecture; ESPR mapping is a separate plugin, not core | Architect |
| R-07 | AASX import from third-party tools fails due to schema variants | Medium | Medium | Medium | Defensive AASX parser with detailed error reporting; validation before import; tested against known tools | Backend Lead |
| R-08 | Docker Compose scaling limitations at production load | Low | High | Low (MVP) | Stateless backend design allows Kubernetes migration; document Kubernetes target architecture | DevOps |
| R-09 | Certificate document storage in MinIO becomes single point of failure | Low | High | Medium | MinIO replication and daily backup to offsite; health check on MinIO in all workflows | DevOps |
| R-10 | Team lacks Keycloak expertise; misconfigured roles expose data | Medium | Critical | High | Keycloak setup documented step-by-step; backend auth layer enforced independently of Keycloak claims | Security Lead |

---

## Part C: Trade-offs

### Hybrid Persistence (PostgreSQL + MongoDB)

**Trade-off:** Operational complexity (two DB systems) vs. data model fit.

**Decision:** Accept the complexity because the two storage systems serve genuinely different data shapes. The relational schema (users, audit, workflow states) does not benefit from a document store, and the AAS document model does not benefit from a fixed relational schema.

**Monitoring indicator:** If > 60% of MongoDB queries use `$text` or `$where` instead of indexed field lookups, reconsider the model.

---

### Modular Monolith Startup Coupling

**Trade-off:** Fast startup and simple deployment vs. coupled module initialization.

**Decision:** Accept the coupling at startup (all modules boot together) because the alternative (separate services) adds too much complexity for MVP. Module independence is maintained at the code level; shared deployment is a runtime convenience.

**Exit trigger:** If any single module requires a different deployment cadence, scaling profile, or technology than the rest, extract it to a separate service with the same API interface.

---

### React SPA vs. Server-Side Rendering

**Trade-off:** Fast initial page load (SSR) vs. simpler architecture and better Copilot/tooling support (SPA).

**Decision:** Use SPA for MVP. The primary users (manufacturers, auditors) are authenticated dashboard users, not anonymous users who need SEO or first-load performance optimization.

**Reconsidered when:** Customer-facing public DPP views need fast indexing by search engines or sub-1s first contentful paint.
