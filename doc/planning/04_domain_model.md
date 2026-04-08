# 04 — Domain Model

## 1. Core Entities

### 1.1 Asset (Product)

Represents the physical or digital product that the DPP describes.

| Attribute | Type | Description |
|-----------|------|-------------|
| `globalAssetId` | URI | Globally unique, externally resolvable product identifier |
| `assetKind` | Enum | `INSTANCE` (specific physical item) or `TYPE` (product model) |
| `assetCategory` | String | Product category (e.g., "Battery", "Electric Motor") |
| `assetStatus` | Enum | `DRAFT`, `ACTIVE`, `ARCHIVED`, `RECALLED` |
| `tenantId` | UUID | Owning organization (tenant) |
| `createdAt` | DateTime | Creation timestamp |
| `updatedAt` | DateTime | Last modification timestamp |

### 1.2 AssetAdministrationShell (AAS)

The digital representation of an Asset. One Asset can have one or more AAS versions (via versioning). In AAS Part 1 v3.0 terms, this is the `AssetAdministrationShell` element.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | URI | AAS identifier (IRI) |
| `idShort` | String | Human-readable short identifier |
| `assetId` | URI (→ Asset) | Reference to the described asset |
| `description` | LangStringSet | Multi-language description |
| `version` | String | AAS version string (e.g., "1.0") |
| `revision` | String | Revision within a version |
| `derivedFrom` | URI (→ AAS) | Reference to parent type AAS (for instances) |
| `submodels` | List\<SubmodelRef\> | References to associated submodels |

### 1.3 Submodel

A structured data container attached to an AAS. Each submodel addresses a specific domain (technical data, sustainability, etc.).

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | URI | Submodel identifier (IRI) |
| `idShort` | String | Human-readable name |
| `semanticId` | URI | Reference to IDTA Submodel Template definition |
| `kind` | Enum | `TEMPLATE` or `INSTANCE` |
| `elements` | List\<SubmodelElement\> | Hierarchical data elements |
| `version` | String | Submodel version |

### 1.4 SubmodelElement

Atomic or composite data element within a submodel. Follows the AAS Part 1 type hierarchy.

**Concrete types:** `Property`, `MultiLanguageProperty`, `File`, `Blob`, `ReferenceElement`, `SubmodelElementCollection`, `SubmodelElementList`, `RelationshipElement`, `Operation`

### 1.5 LifecycleEvent

An append-only event record representing something that happened to or with the product.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Unique event identifier |
| `aasId` | URI (→ AAS) | Associated AAS |
| `eventType` | Enum | `MANUFACTURED`, `SHIPPED`, `INSPECTED`, `SOLD`, `REPAIRED`, `END_OF_LIFE`, `RECALLED`, `CUSTOM` |
| `timestamp` | DateTime | When the event occurred |
| `recordedBy` | UUID (→ User) | User who recorded the event |
| `organizationId` | UUID (→ Tenant) | Organization that recorded the event |
| `payload` | JSON | Event-specific structured data |
| `submodelRef` | URI (optional) | Reference to a submodel updated by this event |

### 1.6 Certificate

Represents a certification or conformity declaration attached to an AAS.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Certificate identifier |
| `aasId` | URI (→ AAS) | Associated AAS |
| `certificationType` | String | Certificate type (e.g., "ISO 14001", "CE", "RoHS") |
| `issuedBy` | UUID (→ User/Org) | Issuing auditor / certification body |
| `issuedAt` | DateTime | Certificate issuance date |
| `validUntil` | DateTime | Expiry date |
| `documentRef` | URI | Reference to stored certificate document (MinIO) |
| `status` | Enum | `ACTIVE`, `REVOKED`, `EXPIRED` |
| `signatureRef` | String | Digital signature reference |

### 1.7 AccessGrant

Expresses what a user or organization is permitted to access on a specific DPP.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Grant identifier |
| `aasId` | URI (→ AAS) | Target AAS |
| `granteeId` | UUID (→ User or Org) | Who receives access |
| `granteeType` | Enum | `USER`, `ORGANIZATION` |
| `scope` | List\<SubmodelId\> | Accessible submodels (empty = all) |
| `permissions` | List\<Enum\> | `READ`, `WRITE`, `WRITE_PENDING_APPROVAL` |
| `grantedBy` | UUID (→ User) | Who issued the grant |
| `expiresAt` | DateTime (optional) | Optional expiry |

### 1.8 CertificationWorkflow

Tracks the formal review process for a DPP certification request.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Workflow identifier |
| `aasId` | URI (→ AAS) | Target AAS |
| `requestedBy` | UUID (→ User) | Initiating manufacturer user |
| `assignedTo` | UUID (→ User/Org) | Responsible auditor |
| `status` | Enum | `PENDING_REVIEW`, `CHANGES_REQUESTED`, `APPROVED`, `REJECTED` |
| `certificationType` | String | What is being certified |
| `findings` | List\<AuditFinding\> | Structured audit findings |
| `createdAt` | DateTime | Workflow creation timestamp |
| `resolvedAt` | DateTime | Closure timestamp |

### 1.9 AuditFinding

Structured finding within a certification workflow.

| Attribute | Type | Description |
|-----------|------|-------------|
| `criterionId` | String | Reference to audit criterion |
| `result` | Enum | `PASS`, `FAIL`, `NOT_APPLICABLE` |
| `comment` | String | Free-text finding description |
| `submodelRef` | URI (optional) | Relevant submodel/element |

### 1.10 User

Platform user entity (mirrored from Keycloak, enriched with DPP-specific attributes).

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Internal user identifier (matches Keycloak sub) |
| `organizationId` | UUID (→ Tenant) | Owning organization |
| `email` | String | Primary email |
| `roles` | List\<Enum\> | Assigned roles per tenant |
| `createdAt` | DateTime | Account creation |

### 1.11 Organization (Tenant)

A company or entity that owns and manages DPPs.

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Tenant identifier |
| `name` | String | Organization display name |
| `legalEntityId` | String | Optional: GLN, VAT number, or other identifier |
| `createdAt` | DateTime | Tenant creation date |

---

## 2. Entity Relationship Diagram

```
Organization (Tenant)
│ 1
│ ├── n → User
│ └── n → Asset
│           │ 1
│           └── n → AssetAdministrationShell
│                        │ 1
│                        ├── n → Submodel
│                        │         └── n → SubmodelElement (tree)
│                        ├── n → LifecycleEvent
│                        ├── n → Certificate
│                        ├── n → AccessGrant
│                        └── n → CertificationWorkflow
│                                     └── n → AuditFinding
```

---

## 3. Mapping to AAS Metamodel (AAS Part 1 v3.0)

| DPP Entity | AAS Concept | Notes |
|------------|-------------|-------|
| `Asset` | `AssetInformation.globalAssetId` + `AssetAdministrationShell.assetInformation` | Asset is embedded in AAS |
| `AssetAdministrationShell` | `AssetAdministrationShell` | Direct mapping |
| `Submodel` | `Submodel` | Direct mapping |
| `SubmodelElement` | `SubmodelElement` subtypes | Direct mapping |
| `LifecycleEvent` | `Submodel` (Lifecycle Events SMT) | Modeled as a dedicated Submodel with `SubmodelElementCollection` per event |
| `Certificate` | `Submodel` (Certifications SMT) + `File` element | Certificate doc stored in MinIO; reference stored in AAS |
| `AccessGrant` | **Application-layer only** | Not part of AAS standard; DPP system extension |
| `CertificationWorkflow` | **Application-layer only** | Workflow state machine; not part of AAS schema |

---

## 4. Standard Submodel Templates

The following IDTA Submodel Templates are used or adapted as the basis for DPP submodels:

| Submodel | IDTA Template ID | Description |
|----------|-----------------|-------------|
| Technical Data | `https://admin-shell.io/IDTA/Submodel/TechnicalData/1/2` | Dimensions, materials, components, specifications |
| Sustainability | `https://admin-shell.io/IDTA/Submodel/CarbonFootprint/0/9` | Carbon footprint, recyclability, hazardous content |
| Provenance / Traceability | Custom (based on `https://admin-shell.io/IDTA/Submodel/SupplyChainTraceability`) | Supply chain hops, material origin, certifications of origin |
| Certifications | `https://admin-shell.io/IDTA/Submodel/SoftwareNameplate/1/0` (adapted) | Certificate records, expiry, issuer references |
| Lifecycle Events | `https://admin-shell.io/IDTA/Submodel/AssetLifeCycleDocumentation/1/0` | Event log entries |
| Nameplate | `https://admin-shell.io/IDTA/Submodel/Nameplate/2/0` | Standard product nameplate |

---

## 5. Global Identifier Convention

All asset identifiers follow the convention:
```
urn:{authority}:{product-category}:{manufacturer-id}:{product-model}:{serial-number}
```
Example:
```
urn:acme-corp:battery:ACM-001:BT47-PRO:SN-2025-09812
```
For type-level AAS (no serial number):
```
urn:acme-corp:battery:ACM-001:BT47-PRO
```

This convention aligns with [IEC 61406](https://www.iec.ch/news/iec-61406-resolving-digital-identities) and can be extended to support GS1 URIs where required by trading partners.
