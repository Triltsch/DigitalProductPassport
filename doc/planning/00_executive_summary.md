# 00 — Executive Summary

## 1. Product Vision

The **Digital Product Passport (DPP)** system is a lifecycle-spanning platform that creates, manages, and distributes structured digital representations of physical products. It enables manufacturers, suppliers, auditors, regulators, and consumers to access relevant product information in a standardized, secure, and role-appropriate manner throughout the entire product lifecycle — from design and manufacturing through distribution and use to end-of-life and recycling.

The system is built on the **Asset Administration Shell (AAS)** standard as specified by the Industrial Digital Twin Association (IDTA), making it natively compliant with the DPP4.0 initiative and aligned with upcoming EU regulatory requirements for digital product passports (ESPR, Battery Regulation EU 2023/1542).

---

## 2. Strategic Value Proposition

### For Manufacturers
- Centralized management of product data, certifications, and compliance documentation
- Automated generation of regulatory reports and audit trails
- Foundation for circular economy business models (product-as-a-service, refurbishment)

### For Supply Chain Partners
- Verified traceability of components and materials
- Structured handover of product data between supply chain stages
- Reduced compliance overhead through standardized data exchange

### For Regulators & Auditors
- Tamper-evident, timestamped product history
- Structured access to compliance data without full product data disclosure
- Alignment with EU DPP and ESPR regulatory frameworks

### For End Customers
- Transparent access to sustainability, repair, and end-of-life information
- Independent verification of product claims (carbon footprint, material origin, certifications)

---

## 3. Scope

### In Scope
- Full lifecycle DPP creation and management based on the AAS metamodel
- Role-based web frontend with tailored views per user type
- AAS-compliant REST API backend using the BaSyx Python SDK
- Submodels for: product data, sustainability, traceability/provenance, certifications, lifecycle events
- Structured persistence layer (relational + document database)
- Authentication, authorization, and role-based access control
- Docker-based deployment for both local development and production
- CI/CD pipeline and automated testing

### Out of Scope (initial version)
- Native mobile applications
- Real-time IoT sensor integration (planned for later phase)
- Blockchain-based tamper proofing (ADR-documented decision)
- Full ERP/MES integration (planned extension)

---

## 4. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Web Frontend (React)                         │
│             Role-adaptive views: Manufacturer, Supplier,            │
│                     Auditor, Customer, Admin                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTPS (REST / OpenAPI)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    API Gateway / Reverse Proxy (Traefik)            │
│               TLS termination · routing · rate limiting             │
└──────────┬──────────────────────────┬──────────────────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────────┐   ┌──────────────────────────────────────────┐
│   Auth Service       │   │         DPP Backend Service              │
│   (Keycloak OIDC)    │   │   FastAPI · BaSyx Python SDK             │
│                      │   │   AAS Registry · Submodel Handling       │
└──────────────────────┘   │   Business Logic · Validation            │
                           └───────────┬──────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
           ┌──────────────┐  ┌────────────────┐  ┌──────────────┐
           │  PostgreSQL  │  │    MongoDB     │  │  File Store  │
           │  (metadata,  │  │  (AAS objects, │  │  (S3/MinIO)  │
           │   users,     │  │  submodels,    │  │  documents,  │
           │   audit log) │  │  AASX files)   │  │  certs, …)   │
           └──────────────┘  └────────────────┘  └──────────────┘
```

**Container overview:**

| Container | Image | Role |
|-----------|-------|------|
| `frontend` | Node/nginx | React SPA served via nginx |
| `backend` | Python / FastAPI | DPP business logic, AAS API |
| `keycloak` | Keycloak 24 | OIDC identity provider |
| `postgres` | PostgreSQL 16 | Relational data (users, metadata, audit) |
| `mongo` | MongoDB 7 | AAS object store |
| `minio` | MinIO | Object storage for documents/certificates |
| `traefik` | Traefik v3 | Reverse proxy, TLS, routing |
| `prometheus` | Prometheus | Metrics collection |
| `grafana` | Grafana | Metrics dashboards |
| `loki` | Grafana Loki | Log aggregation |

---

## 5. Key Assumptions

1. The AAS metamodel version used is **AAS Part 1 v3.0** (IEC 63278-1).
2. The BaSyx Python SDK is the primary library for AAS object construction, serialization, and deserialization.
3. Product identity is established via **Global Asset ID** (URI-based, aligned with GS1/EPCIS where applicable).
4. The first release targets **industrial manufacturing** use cases; the pattern is generalizable to other sectors.
5. Deployment targets Linux-based environments; Windows support is via Docker Desktop.
6. Initial user base is **small-to-medium enterprises** (< 10,000 products, < 500 concurrent users); horizontal scaling is designed for but not required at v1.
7. The frontend is a **Single-Page Application (SPA)**; server-side rendering is not required initially.

---

## 6. Guiding Principles

- **Standards-first:** AAS and IDTA standards take precedence over custom solutions wherever possible.
- **Separation of concerns:** Domain model, persistence model, and API model are deliberately kept separate.
- **Security by design:** Authentication and authorization are not afterthoughts; they are central to the architecture.
- **Observability by default:** Every service emits structured logs and metrics from day one.
- **Incremental extensibility:** The Submodel pattern allows new data domains to be added without changing core architecture.
- **Reproducibility:** Any developer should be able to run the full system locally with a single `docker compose up` command.
