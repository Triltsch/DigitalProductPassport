# 01 — Stakeholders & Roles

## 1. Stakeholder Analysis

### Primary Stakeholders (direct system users)

| Stakeholder | Interest | Pain Point Addressed | Engagement |
|-------------|----------|----------------------|------------|
| **Manufacturer** | Create & maintain product passports; prove compliance | Manual, fragmented compliance documentation | High — daily system use |
| **Supplier** | Provide component/material data; receive product specs | Inconsistent data formats from customers | High — regular data submission |
| **Auditor / Certification Body** | Inspect product data; issue and manage certificates | Incomplete, unverifiable product documentation | Medium — periodic access |
| **End Customer / Consumer** | Access product sustainability and repair information | No transparent access to meaningful product data | Low — read-only, self-service |
| **Regulator** | Monitor compliance with DPP/ESPR regulations | Manual regulatory submissions from multiple sources | Low — structured reporting access |
| **System Administrator** | Manage users, tenants, integrations | High operational overhead from custom solutions | High — continuous system operation |

### Secondary Stakeholders (indirectly affected)

| Stakeholder | Interest |
|-------------|----------|
| **ERP/MES System Operators** | Integration of DPP with existing enterprise systems |
| **IT Security Team** | Ensure data protection, GDPR compliance, audit trails |
| **Legal / Compliance Department** | Ensure adherence to EU DPP, ESPR, Battery Regulation |
| **Recycler / End-of-Life Handler** | Access material composition data for proper dismantling |

---

## 2. Role Model

The system defines the following built-in roles. Roles are assigned per product or per organizational scope (tenant-level RBAC).

### Role Definitions

#### `ADMIN`
- Platform-wide system administration
- User management, tenant provisioning, integration configuration
- Access to all audit logs and system configuration
- Can impersonate or delegate access for support purposes

#### `MANUFACTURER`
- Creates and manages DPPs for their own products
- Creates and edits all submodels
- Publishes DPPs to the registry (transitions DPP from draft to active)
- Manages access grants to other roles (e.g., shares DPP with supplier or auditor)
- Can initiate approval/certification workflows

#### `SUPPLIER`
- Submits component and material data as submodel contributions
- Can view the DPP of products they are supplying to
- Cannot edit data outside their designated submodel scope
- Receives and acknowledges data requests from manufacturers

#### `AUDITOR`
- Read-only access to the full DPP of assigned products
- Can annotate DPP with audit findings (structured audit submodel)
- Issues, signs, and attaches certificates to a DPP
- Cannot modify core product data

#### `CUSTOMER`
- Read-only access to the publicly disclosed subset of a DPP
- Access governed by manufacturer-defined disclosure rules
- No ability to submit or modify data

#### `REGULATOR`
- Read access to compliance-relevant submodels of reported products
- Receives structured data exports for regulatory submissions
- Can flag products for compliance review
- Cannot modify DPP data

---

## 3. Permission Matrix

Each symbol represents the scope of access per role and operation.

| Resource | ADMIN | MANUFACTURER | SUPPLIER | AUDITOR | CUSTOMER | REGULATOR |
|----------|:-----:|:------------:|:--------:|:-------:|:--------:|:---------:|
| **AAS / DPP — Create** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **AAS / DPP — Read (own)** | ✅ | ✅ | ✅ (granted) | ✅ (granted) | ✅ (public) | ✅ (granted) |
| **AAS / DPP — Edit** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **AAS / DPP — Delete** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **AAS / DPP — Publish** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Submodel — Create** | ✅ | ✅ | ✅ (scoped) | ❌ | ❌ | ❌ |
| **Submodel — Read** | ✅ | ✅ | ✅ (scoped) | ✅ (granted) | ✅ (public) | ✅ (compliance-only) |
| **Submodel — Edit** | ✅ | ✅ | ✅ (scoped) | ❌ | ❌ | ❌ |
| **Submodel — Delete** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Certificate — Issue** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Certificate — View** | ✅ | ✅ | ✅ | ✅ | ✅ (public) | ✅ |
| **Lifecycle Event — Create** | ✅ | ✅ | ✅ (scoped) | ✅ (audit event) | ❌ | ❌ |
| **Lifecycle Event — Read** | ✅ | ✅ | ✅ (scoped) | ✅ | ✅ (public) | ✅ |
| **User Management** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Audit Log — Read** | ✅ | ✅ (own) | ❌ | ✅ (own activity) | ❌ | ✅ (compliance events) |
| **Access Grant — Create** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Regulatory Export** | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |

**Legend:** ✅ = allowed, ❌ = not allowed, *(scoped)* = limited to own organizational scope, *(granted)* = requires explicit access grant from MANUFACTURER, *(public)* = restricted to publicly disclosed data only

---

## 4. Organizational Model (Multi-Tenancy)

- The system supports **multi-tenancy** at the organization level.
- Each organization (e.g., a manufacturer company) is a **tenant**.
- Users belong to one or more tenants and have roles within each.
- AAS/DPP records are owned by a tenant; access grants are issued at the tenant level.
- The `ADMIN` role spans all tenants (platform admin); tenant-scoped admins can only manage their own organization.

```
Platform
└── Tenant A (Manufacturer GmbH)
│   ├── User: alice [MANUFACTURER]
│   ├── User: bob [SUPPLIER]
│   └── DPP: product-001 → access grants → [auditor@CertCo, customer@public]
└── Tenant B (Certification Body AG)
    ├── User: carol [AUDITOR]
    └── Certificate store
```

---

## 5. Identity Provider Integration

- Users authenticate via **Keycloak** (OIDC / OAuth 2.0).
- Role assignments are managed in Keycloak and propagated as JWT claims.
- The backend validates JWTs and enforces RBAC via a policy middleware layer.
- Social login (e.g., for consumers accessing public DPPs) is a future extension.
