# 07 — Modules

## 1. Module Overview

The DPP system is structured as a **modular monolith** on the backend and a **feature-sliced** architecture on the frontend. Each module has a clearly defined responsibility, public interface, and dependency set.

```
┌────────────────────────────────────────────────────────────────────┐
│                          DPP Backend                               │
│                                                                    │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────────┐   │
│  │  AAS Module  │  │  Submodel     │  │  Lifecycle Events    │   │
│  │              │  │  Module       │  │  Module              │   │
│  └──────┬───────┘  └──────┬────────┘  └──────────┬───────────┘   │
│         │                 │                       │               │
│  ┌──────┴─────────────────┴───────────────────────┴───────────┐   │
│  │                    Access Control Module                    │   │
│  └──────────────────────────┬──────────────────────────────────┘   │
│                             │                                      │
│  ┌──────────────┐  ┌────────┴──────┐  ┌──────────────────────┐   │
│  │  Cert &      │  │  Import /     │  │   Notification       │   │
│  │  Workflow    │  │  Export       │  │   Module             │   │
│  │  Module      │  │  Module       │  │                      │   │
│  └──────────────┘  └───────────────┘  └──────────────────────┘   │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │           Infrastructure Layer (DB, Storage, Auth)         │   │
│  └────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

---

## 2. Backend Modules

### 2.1 AAS Module

**Responsibility:** Creation, retrieval, update, deletion, versioning, and publication of AAS shell objects.

**Public Interface:**
- `AASService.create_shell(dto, owner) → AASShell`
- `AASService.get_shell(aas_id, requester) → AASShell`
- `AASService.list_shells(filters, requester) → Page[AASShell]`
- `AASService.update_shell(aas_id, dto, requester) → AASShell`
- `AASService.publish_shell(aas_id, requester) → AASShell`
- `AASService.archive_shell(aas_id, requester)`
- `AASService.delete_shell(aas_id, requester)`

**Internal Components:**
- `AASRepository` (MongoDB): CRUD for AAS JSON documents
- `AASRegistryRepository` (PostgreSQL): AAS-to-assetId lookup index
- `AASValidator`: validates AAS structure against AAS Part 1 schema using BaSyx SDK
- `AASVersioningService`: manages version/revision transitions, archived version chaining

**Dependencies:** Access Control Module, Infrastructure/MongoDB, Infrastructure/PostgreSQL

---

### 2.2 Submodel Module

**Responsibility:** Management of Submodel objects, SubmodelElements, and validation against IDTA Submodel Templates.

**Public Interface:**
- `SubmodelService.create(aas_id, dto, requester) → Submodel`
- `SubmodelService.get(submodel_id, requester) → Submodel`
- `SubmodelService.update(submodel_id, dto, requester) → Submodel`
- `SubmodelService.delete(submodel_id, requester)`
- `SubmodelService.get_element(submodel_id, id_short_path, requester) → SubmodelElement`
- `SubmodelService.update_element(submodel_id, id_short_path, dto, requester) → SubmodelElement`
- `SubmodelService.validate(submodel_id) → ValidationResult`

**Internal Components:**
- `SubmodelRepository` (MongoDB): stores submodel JSON documents
- `SubmodelTemplateRegistry`: stores and retrieves IDTA Submodel Template definitions
- `SubmodelValidator`: validates a submodel instance against its `semanticId` template

**Supported Submodel Types:** TechnicalData, Sustainability, Provenance, Certifications, LifecycleEvents, Nameplate (extensible)

**Dependencies:** Access Control Module, AAS Module (for shell ↔ submodel linkage), Infrastructure/MongoDB

---

### 2.3 Lifecycle Events Module

**Responsibility:** Recording, retrieval, and querying of append-only lifecycle events associated with AAS instances.

**Public Interface:**
- `LifecycleService.record_event(aas_id, event_dto, requester) → LifecycleEvent`
- `LifecycleService.get_events(aas_id, filters, requester) → Page[LifecycleEvent]`
- `LifecycleService.get_event(event_id, requester) → LifecycleEvent`

**Note:** Events are immutable after recording. No update or delete operations are exposed.

**Internal Components:**
- `EventRepository` (PostgreSQL): append-only event table with indexing on `aasId` and `timestamp`

**Dependencies:** Access Control Module, AAS Module, Infrastructure/PostgreSQL

---

### 2.4 Certification & Workflow Module

**Responsibility:** Managing certification requests, the review workflow state machine, and certificate records.

**Public Interface:**
- `CertificationService.request_review(aas_id, dto, requester) → CertificationWorkflow`
- `CertificationService.get_workflow(workflow_id, requester) → CertificationWorkflow`
- `CertificationService.submit_findings(workflow_id, findings, requester) → CertificationWorkflow`
- `CertificationService.approve(workflow_id, requester) → CertificationWorkflow`
- `CertificationService.reject(workflow_id, reason, requester) → CertificationWorkflow`
- `CertificationService.request_changes(workflow_id, comments, requester) → CertificationWorkflow`
- `CertificationService.issue_certificate(aas_id, dto, requester) → Certificate`
- `CertificationService.revoke_certificate(cert_id, reason, requester)`
- `CertificationService.get_certificates(aas_id, requester) → List[Certificate]`

**Workflow State Machine:**
```
PENDING_REVIEW ──approve──▶ APPROVED
PENDING_REVIEW ──reject──▶ REJECTED
PENDING_REVIEW ──request_changes──▶ CHANGES_REQUESTED
CHANGES_REQUESTED ──resubmit──▶ PENDING_REVIEW
```

**Internal Components:**
- `WorkflowRepository` (PostgreSQL)
- `CertificateRepository` (PostgreSQL + MinIO for documents)
- `CertificateSignatureService`: generates a SHA-256 hash reference for certificate integrity

**Dependencies:** Access Control Module, AAS Module, Notification Module, Infrastructure

---

### 2.5 Access Control Module

**Responsibility:** Centralized enforcement of role-based and resource-level permissions across all modules.

**Public Interface:**
- `AccessPolicy.can_read(user, resource) → bool`
- `AccessPolicy.can_write(user, resource) → bool`
- `AccessPolicy.can_delete(user, resource) → bool`
- `AccessGrantService.grant(aas_id, grantee, permissions, requester) → AccessGrant`
- `AccessGrantService.revoke(grant_id, requester)`
- `AccessGrantService.list_grants(aas_id, requester) → List[AccessGrant]`

**Internal Components:**
- `AccessGrantRepository` (PostgreSQL)
- `RolePolicy`: static role-level permission definitions
- `GrantPolicy`: runtime access grant lookups

**Dependencies:** Infrastructure/PostgreSQL only (no circular dependencies; all other modules depend on this one)

---

### 2.6 Import / Export Module

**Responsibility:** Serialization and deserialization of AAS data to/from external formats (AASX, JSON-LD).

**Public Interface:**
- `ExportService.export_aasx(aas_id, requester) → bytes`
- `ExportService.export_json(aas_id, requester) → dict`
- `ImportService.import_aasx(file_bytes, owner) → ImportResult`
- `ImportService.import_json(data, owner) → ImportResult`

**Internal Components:**
- `AASXPackager`: uses BaSyx SDK to build AASX ZIP packages
- `AASXParser`: validates and parses uploaded AASX files using BaSyx SDK
- `JSONLDSerializer`: produces JSON-LD output from AAS domain objects

**Dependencies:** AAS Module, Submodel Module, Infrastructure/MinIO (for document attachments in AASX)

---

### 2.7 Notification Module

**Responsibility:** Sending in-app and external (email/webhook) notifications triggered by system events.

**Public Interface (internal event bus):**
- `NotificationService.send(event: DomainEvent)`

Events handled:
- `CertificationWorkflowUpdated` → notify manufacturer/auditor
- `AccessGrantCreated` → notify grantee
- `DPPPublished` → webhook trigger for subscribers
- `CertificateIssued` → notify manufacturer

**Internal Components:**
- `EmailNotifier`: sends transactional email via SMTP (configurable)
- `WebhookNotifier`: HTTP POST to registered endpoints
- `InAppNotificationRepository` (PostgreSQL): stores in-app notification records
- Celery background tasks for async delivery

**Dependencies:** Infrastructure/PostgreSQL, Infrastructure/Celery + Redis

---

### 2.8 User & Organization Module

**Responsibility:** Management of internal user profiles and organization (tenant) records, synchronized with Keycloak.

**Public Interface:**
- `UserService.sync_from_token(token_claims) → User`
- `UserService.get(user_id) → User`
- `OrganizationService.create(dto) → Organization`
- `OrganizationService.update(org_id, dto) → Organization`

**Internal Components:**
- `UserRepository` (PostgreSQL)
- `OrganizationRepository` (PostgreSQL)
- `KeycloakAdminClient`: creates users/roles in Keycloak (admin API)

**Dependencies:** Infrastructure/PostgreSQL, Infrastructure/Keycloak

---

## 3. Frontend Modules (Features)

| Feature Module | Components | Primary Role | Notes |
|----------------|------------|-------------|-------|
| `dashboard` | DashboardPage, StatsSummary, TaskList | All | Role-adaptive entry point |
| `dpp` | DPPListPage, DPPDetailPage, DPPCreateWizard | Manufacturer, Supplier | Core DPP CRUD |
| `submodels` | SubmodelViewer, SubmodelEditor (per type) | Manufacturer, Supplier | Per-submodel UI forms |
| `lifecycle` | LifecycleTimeline, EventRecordForm | All (role-filtered) | Append-only event display |
| `certifications` | CertList, CertDetail, CertIssueForm | Auditor, Manufacturer | Certificate viewer and issuer |
| `workflows` | WorkflowList, WorkflowReviewPanel | Manufacturer, Auditor | Certification workflow UI |
| `access-management` | GrantTable, GrantModal, RevokeButton | Manufacturer | Access grant management |
| `import-export` | ImportUpload, ExportButtons | Manufacturer, Admin | AASX/JSON file ops |
| `admin` | UserTable, OrgTable, UserCreateForm | Admin | Platform admin panel |
| `public-dpp` | PublicDPPView, QRCodeDisplay | Customer | Unauthenticated public view |

---

## 4. Module Dependency Graph

```
Access Control ◀───── AAS ──────▶ Submodel
       ▲                │               │
       │           Lifecycle        Certification/
       │           Events           Workflow
       │                │               │
       └────────────────┴───────────────┘
                        │
                 Notifications
                        │
                  Import/Export ──▶ AAS + Submodel
                        │
               User & Organization
```

**Rule:** No module may import from a module it does not have a declared dependency on. Circular dependencies are prohibited. The `Access Control` module has **zero** application-layer dependencies (it only depends on infrastructure).
