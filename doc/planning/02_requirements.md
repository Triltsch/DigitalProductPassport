# 02 — Requirements

## 1. Functional Requirements

Requirements are classified as:
- **MUST** — mandatory for MVP
- **SHOULD** — high priority, target v1.1
- **MAY** — optional extension

### 1.1 AAS / Digital Product Passport Management

| ID | Priority | Requirement |
|----|----------|-------------|
| F-AAS-01 | MUST | The system shall create, read, update, and delete AAS instances conforming to AAS Part 1 v3.0 |
| F-AAS-02 | MUST | Each AAS shall have a globally unique `assetId` (URI) and a human-readable `idShort` |
| F-AAS-03 | MUST | AAS instances shall support lifecycle states: `DRAFT`, `ACTIVE`, `ARCHIVED`, `RECALLED` |
| F-AAS-04 | MUST | The system shall expose an AAS-compliant REST API as defined by IDTA API specification |
| F-AAS-05 | MUST | AASX package import/export shall be supported |
| F-AAS-06 | SHOULD | The system shall support AAS registry for discoverability of AAS instances by `assetId` |
| F-AAS-07 | SHOULD | AAS instances shall be versionable; each version is immutable after publication |
| F-AAS-08 | MAY | AAS instances may be linked to form hierarchical product structures (BOM) |

### 1.2 Submodel Management

| ID | Priority | Requirement |
|----|----------|-------------|
| F-SM-01 | MUST | The system shall support creation and management of the following submodels: Technical Data, Sustainability, Provenance/Traceability, Certifications, Lifecycle Events |
| F-SM-02 | MUST | Submodels shall be validated against their respective IDTA Submodel Template (SMT) definitions |
| F-SM-03 | MUST | Submodels shall be independently accessible via the AAS API (`/submodels/{id}`) |
| F-SM-04 | SHOULD | Custom/domain-specific submodels shall be addable without core system changes |
| F-SM-05 | SHOULD | Submodel elements shall support semantic annotations via IRI-based `semanticId` references |
| F-SM-06 | MAY | Submodel Templates shall be stored in a template registry for reuse |

### 1.3 User & Role Management

| ID | Priority | Requirement |
|----|----------|-------------|
| F-UA-01 | MUST | Users shall authenticate via OIDC (Keycloak) |
| F-UA-02 | MUST | Role-based access control (RBAC) shall be enforced for all API endpoints |
| F-UA-03 | MUST | Manufacturers shall be able to grant and revoke access to specific DPPs for external parties |
| F-UA-04 | MUST | All authentication events shall be logged in the audit trail |
| F-UA-05 | SHOULD | Multi-factor authentication (MFA) shall be supported for MANUFACTURER and AUDITOR roles |
| F-UA-06 | MAY | Fine-grained attribute-based access control (ABAC) may be introduced for field-level data disclosure |

### 1.4 Frontend / User Interface

| ID | Priority | Requirement |
|----|----------|-------------|
| F-UI-01 | MUST | The web UI shall provide role-adaptive views (different layouts and data exposure per role) |
| F-UI-02 | MUST | Manufacturers shall be able to create and edit DPPs via a guided form-based interface |
| F-UI-03 | MUST | All users shall be able to view the DPP detail view with all authorized submodels |
| F-UI-04 | MUST | The UI shall display validation errors from the backend clearly to the user |
| F-UI-05 | SHOULD | The UI shall support QR code generation linking to a public DPP view |
| F-UI-06 | SHOULD | A dashboard view summarizing owned/accessible DPPs and compliance status shall be available |
| F-UI-07 | SHOULD | Auditors shall have a dedicated review and annotation workflow in the UI |
| F-UI-08 | MAY | The UI may support internationalization (i18n) for at least English and German |

### 1.5 Lifecycle Event Tracking

| ID | Priority | Requirement |
|----|----------|-------------|
| F-LE-01 | MUST | The system shall record lifecycle events linked to a DPP (manufacture, shipment, inspection, end-of-life) |
| F-LE-02 | MUST | Lifecycle events shall be timestamped and attributed to the creating user/organization |
| F-LE-03 | MUST | Lifecycle events shall be append-only (no editing or deletion after creation) |
| F-LE-04 | SHOULD | Events shall support structured payloads defined by the Lifecycle Events Submodel Template |

### 1.6 Certification & Approval Workflows

| ID | Priority | Requirement |
|----|----------|-------------|
| F-CW-01 | MUST | Manufacturers shall be able to submit a DPP for external certification review |
| F-CW-02 | MUST | Auditors shall be able to approve, reject, or request changes to a submitted DPP |
| F-CW-03 | MUST | Certificates issued by auditors shall be attached to the DPP with a digital signature reference |
| F-CW-04 | SHOULD | Workflow state changes shall trigger notifications (email / in-app) |
| F-CW-05 | MAY | Certificate revocation shall be supported with an explanation and audit trail |

### 1.7 Import / Export & Integrations

| ID | Priority | Requirement |
|----|----------|-------------|
| F-IE-01 | MUST | The system shall export DPPs in AASX format |
| F-IE-02 | MUST | The system shall import DPPs from AASX files |
| F-IE-03 | SHOULD | JSON-LD export following AAS Part 2 serialization rules shall be supported |
| F-IE-04 | SHOULD | Webhook support shall allow external systems to subscribe to DPP lifecycle events |
| F-IE-05 | MAY | A CSV-based bulk import for product data shall be available |
| F-IE-06 | MAY | REST integration adapters for common ERP systems (SAP, Odoo) may be added as plugins |

---

## 2. Non-Functional Requirements

### 2.1 Performance

| ID | Requirement |
|----|-------------|
| NF-P-01 | API response time for read operations (single AAS) shall be < 500 ms at p95 under normal load |
| NF-P-02 | API response time for write operations shall be < 2 s at p95 |
| NF-P-03 | The system shall support at least 200 concurrent users in MVP without degradation |
| NF-P-04 | Database read-heavy queries shall use indexed lookups; no full-table scans on hot paths |

### 2.2 Scalability

| ID | Requirement |
|----|-------------|
| NF-SC-01 | Backend services shall be stateless to allow horizontal scaling behind a load balancer |
| NF-SC-02 | The persistence layer shall support at least 1 million AAS objects without architectural changes |
| NF-SC-03 | Docker Compose shall be the deployment model for MVP; Kubernetes compatibility shall be ensured by design |

### 2.3 Security

| ID | Requirement |
|----|-------------|
| NF-SEC-01 | All API communication shall use TLS 1.2 or higher |
| NF-SEC-02 | Secrets (DB credentials, API keys) shall never be stored in source code or container images |
| NF-SEC-03 | All user input shall be validated and sanitized at the API boundary (OWASP Top 10 compliance) |
| NF-SEC-04 | SQL and NoSQL injection shall be prevented through parameterized queries and ORM usage |
| NF-SEC-05 | The system shall produce a complete, tamper-evident audit trail for all data modifications |
| NF-SEC-06 | Role and permission checks shall be enforced server-side; the frontend shall never be the sole guard |

### 2.4 Reliability & Availability

| ID | Requirement |
|----|-------------|
| NF-RA-01 | Target availability for production: 99.5% uptime |
| NF-RA-02 | Database backups shall be performed daily with a 30-day retention window |
| NF-RA-03 | Application startup and shutdown shall be graceful; in-flight requests shall complete |
| NF-RA-04 | Health check endpoints (`/health/live`, `/health/ready`) shall be exposed by all services |

### 2.5 Maintainability

| ID | Requirement |
|----|-------------|
| NF-M-01 | Backend codebase shall achieve ≥ 80% unit test coverage |
| NF-M-02 | All public API endpoints shall be documented via OpenAPI 3.1 |
| NF-M-03 | Database schema migrations shall be version-controlled using Alembic |
| NF-M-04 | The system shall use structured logging (JSON format) compatible with Loki/ELK |

### 2.6 Compliance

| ID | Requirement |
|----|-------------|
| NF-CO-01 | System shall be compliant with GDPR (EU 2016/679) regarding personally identifiable information |
| NF-CO-02 | DPP data model shall align with EU Battery Regulation (EU 2023/1542) requirements for battery passports as a reference implementation |
| NF-CO-03 | AAS API endpoints shall conform to the IDTA AAS REST API specification |
| NF-CO-04 | The system shall support data retention policies configurable per tenant |

### 2.7 Interoperability

| ID | Requirement |
|----|-------------|
| NF-IO-01 | AAS objects shall be serializable to JSON compliant with AAS Part 2 / IEC 63278-2 |
| NF-IO-02 | The system shall accept and produce AASX packages |
| NF-IO-03 | All external-facing identifiers (product IDs, asset IDs) shall use globally resolvable URIs |

---

## 3. Constraints

| Constraint | Description |
|------------|-------------|
| **AAS Standard** | AAS Part 1 v3.0 and AAS Part 2 serialization are the normative base |
| **BaSyx SDK** | Backend AAS handling must use the BaSyx Python SDK as the primary library |
| **Docker** | All deployable components must be containerized with Docker |
| **Open Source** | Core dependencies must be open-source with compatible licenses (Apache 2.0, MIT, LGPL) |
| **Language** | Backend: Python 3.11+. Frontend: TypeScript / React |
