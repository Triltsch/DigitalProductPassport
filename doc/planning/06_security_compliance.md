# 06 — Security & Compliance

## 1. Authentication

### 1.1 Identity Provider: Keycloak

All user authentication is delegated to **Keycloak** as the central Identity Provider (IdP):

- Protocol: **OpenID Connect (OIDC)** on top of OAuth 2.0
- Flow for frontend: **Authorization Code Flow with PKCE** (no client secrets in browser)
- Flow for server-to-server: **Client Credentials Grant**
- Token format: JWT (RS256 signed)
- Token lifetime:
  - Access token: 5 minutes
  - Refresh token: 8 hours
  - Session lifetime: 24 hours

### 1.2 Token Validation (Backend)

Every protected API request requires a valid `Authorization: Bearer <token>` header.

The backend middleware:
1. Fetches Keycloak's JWKS endpoint on startup and caches signing keys.
2. Validates JWT signature, expiry (`exp`), audience (`aud`), and issuer (`iss`).
3. Extracts the user's roles and tenant from token claims.
4. Populates the request context with a `CurrentUser` object.

```python
# Middleware pseudocode
async def verify_token(token: str) -> CurrentUser:
    claims = jwt.decode(token, jwks=keycloak_jwks, algorithms=["RS256"],
                        audience=settings.JWT_AUDIENCE,
                        issuer=settings.KEYCLOAK_ISSUER_URL)
    return CurrentUser(
        id=claims["sub"],
        roles=claims.get("realm_access", {}).get("roles", []),
        tenant_id=claims.get("tenant_id"),
    )
```

### 1.3 Multi-Factor Authentication (MFA)

- MFA is **required** for `MANUFACTURER` and `AUDITOR` roles (enforced via Keycloak realm policy).
- Supported second factors: TOTP (Google Authenticator, Authy), WebAuthn/Passkey.
- `CUSTOMER` accounts may optionally enable MFA.

---

## 2. Authorization (RBAC)

### 2.1 Enforcement Points

Authorization is enforced at **two independent layers**:

1. **FastAPI endpoint dependencies:** Each router uses `Depends(require_role([...]))` to gate access at the HTTP handler level.
2. **Service layer checks:** Critical operations (e.g., publishing a DPP, issuing a certificate) perform an additional check in the service using domain-level policy functions.

The frontend performs role-based UI rendering as a **UX optimization only**; it is never the security boundary.

### 2.2 Access Grant Enforcement

For resource-level access (e.g., reading a specific DPP), the `AccessGrant` model is checked in the service layer:

```python
async def get_aas(aas_id: str, current_user: CurrentUser) -> AASShell:
    aas = await aas_repository.get(aas_id)
    if not access_policy.can_read(current_user, aas):
        raise PermissionDeniedError()
    return aas
```

`access_policy.can_read` checks:
- The user is the tenant owner (MANUFACTURER), OR
- The user has an explicit `AccessGrant` for this AAS with `READ` permission, OR
- The AAS is in `ACTIVE` state and the requested data is publicly disclosed

### 2.3 Scoped Write Permissions for Suppliers

Suppliers may be granted `WRITE` or `WRITE_PENDING_APPROVAL` access to specific submodels. This scope is stored in the `AccessGrant.scope` field and enforced at both the API and service layers before allowing write operations.

---

## 3. Input Validation & Injection Prevention

### 3.1 API Boundary Validation

All request payloads are validated using **Pydantic v2** models at the API layer:
- Type coercion with strict mode where applicable
- String length limits enforced at model level
- No raw user strings are passed directly to database queries

### 3.2 SQL Injection Prevention

- All PostgreSQL queries use **SQLAlchemy ORM** or parameterized raw queries.
- No string concatenation in query construction.
- MongoDB queries use the Motor/Motor driver's query builder; user input mapped to typed query parameters.

### 3.3 XSS / Injection in Frontend

- React's JSX escapes all dynamic content by default; `dangerouslySetInnerHTML` is prohibited.
- Content Security Policy (CSP) headers are enforced by the nginx container and configured in Traefik.

### 3.4 File Upload Security

- All uploaded files (certificates, AASX packages) are:
  - Size-limited (configurable, default 50 MB max)
  - MIME type validated against an allowlist
  - Scanned via ClamAV (optional, configurable) before storage
  - Stored in MinIO with randomized, non-guessable object keys
  - Served with `Content-Disposition: attachment` to prevent browser execution

---

## 4. Data Protection & GDPR

### 4.1 Personal Data Classification

| Data Category | Classification | Storage | Retention |
|---------------|---------------|---------|-----------|
| User email, name | Personal Data | PostgreSQL | Until account deletion + 30 days |
| Authentication logs | Personal Data | PostgreSQL / Loki | 90 days |
| DPP product data | Non-personal (product-level) | MongoDB | Configurable per tenant |
| Audit trail | Personal Data (user attribution) | PostgreSQL | 7 years (compliance) |
| Certificate documents | May contain personal data | MinIO | Certificate validity + 5 years |

### 4.2 GDPR Controls

- **Right to erasure (Art. 17):** User accounts can be deleted; personal attributes are anonymized in audit trails (user ID replaced with `[DELETED]` marker).
- **Data minimization:** Product data does not require personal data. User-facing events only store `userId` references, not name/email inline.
- **Data portability (Art. 20):** Users can request an export of their account data via the admin API.
- **Data processing agreements:** Template DPA available for tenant onboarding.
- **GDPR-compliant logging:** Log entries must never contain passwords, tokens, or personally identifiable information beyond `userId`.

---

## 5. Transport Security

- All external-facing endpoints are served over **TLS 1.2+** (enforced by Traefik).
- TLS certificates: Let's Encrypt via Traefik ACME in production; self-signed for local dev.
- HTTP → HTTPS redirect is enforced by Traefik.
- HSTS header (`Strict-Transport-Security`) is set with a minimum `max-age` of 1 year.
- Traefik serves as the sole TLS termination point; backend services communicate over plain HTTP within the Docker network.

---

## 6. Secrets Management

- No secrets (DB passwords, API keys, JWT signing keys) are stored in source code, Dockerfiles, or committed environment files.
- **Development:** Secrets are loaded from a `.env` file (gitignored). A `.env.example` file without real values is committed.
- **Production:** Secrets are injected via **Docker Secrets** or an external vault (HashiCorp Vault / cloud secret manager). The application reads secrets from environment variables or mounted files.
- Keycloak's client secrets and DB credentials follow the same policy.
- Secret rotation is supported without downtime (rolling application restart after secret update).

---

## 7. Audit Trail

All data modifications are recorded in a tamper-evident audit log in PostgreSQL:

| Field | Description |
|-------|-------------|
| `id` | UUID |
| `timestamp` | UTC timestamp |
| `userId` | Acting user (UUID) |
| `tenantId` | Tenant context |
| `action` | `CREATE`, `UPDATE`, `DELETE`, `PUBLISH`, `ACCESS_GRANT`, `CERTIFICATE_ISSUED`, etc. |
| `resourceType` | e.g., `AAS`, `SUBMODEL`, `USER` |
| `resourceId` | ID of the affected resource |
| `previousValue` | JSON snapshot of previous state (for updates) |
| `newValue` | JSON snapshot of new state |
| `ipAddress` | Client IP (anonymized after 90 days) |

Audit log entries are **write-only** via the application. No application-level `DELETE` or `UPDATE` is permitted on audit records. Direct database-level deletion requires administrative access and is logged.

---

## 8. EU DPP Regulatory Alignment

### 8.1 Applicable Regulations

| Regulation | Status | DPP System Response |
|------------|--------|---------------------|
| **EU Battery Regulation** (EU 2023/1542) | In force (phased) | Battery DPP submodel templates based on Annex XIII requirements |
| **ESPR** (Ecodesign for Sustainable Products Regulation) | Transitioning | System architecture supports multiple product categories; submodels are extensible |
| **GDPR** (EU 2016/679) | In force | Controls described in Section 4 above |
| **NIS2 Directive** | In force | Security controls in Sections 1–6 |

### 8.2 Battery Regulation Compliance Checklist (Reference)

The Battery Regulation (Art. 77, Annex XIII) requires the following DPP data attributes to be accessible:

- [ ] General information (manufacturer, model, date of manufacture)
- [ ] Carbon footprint (per lifecycle phase)
- [ ] Recycled content declaration
- [ ] Material composition (cobalt, lithium, nickel, lead share)
- [ ] Hazardous substances
- [ ] Performance and durability certifications
- [ ] Supply chain due diligence policy
- [ ] Extended producer responsibility information

These map directly to the **Technical Data**, **Sustainability**, and **Provenance** submodels in this system.

### 8.3 Data Residency

- For EU compliance: product and personal data must be stored in EU data centers.
- Docker Compose does not enforce data residency — this constraint applies to cloud deployment configurations.
- Tenant-level data residency configuration is a planned feature for v1.1.

---

## 9. Security Testing

- OWASP Top 10 checklist is reviewed for each release.
- SAST (static analysis): `bandit` for Python, `eslint-plugin-security` for TypeScript.
- Dependency vulnerability scanning: `pip-audit` for Python, `npm audit` for Node.
- API fuzz testing: `schemathesis` (property-based testing against the OpenAPI spec) is part of the CI pipeline.
- Penetration testing: manual assessment before first production deployment; annual thereafter.
