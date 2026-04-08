# 09 — Testing & Quality

## 1. Testing Strategy Overview

The DPP system follows a **test pyramid** approach, with a high volume of fast, isolated unit tests at the base, a smaller set of integration tests in the middle, and a targeted E2E test suite at the top.

```
              ┌──────────┐
              │   E2E    │   ← Few, critical user journey tests
              │  Tests   │     (Playwright / pytest + Docker)
              └────┬─────┘
           ┌───────┴────────┐
           │  Integration   │   ← Module boundary tests, DB tests
           │     Tests      │     (pytest + TestContainers)
           └───────┬────────┘
      ┌────────────┴────────────┐
      │       Unit Tests        │   ← All domain logic, services, utils
      │    (pytest / Vitest)    │     (no DB, no network, fast)
      └─────────────────────────┘
```

### Coverage Targets

| Layer | Tool | Target Coverage |
|-------|------|----------------|
| Backend unit tests | pytest + coverage.py | ≥ 80% line coverage |
| Backend integration tests | pytest + TestContainers | Key service boundaries |
| Frontend unit tests | Vitest + Testing Library | ≥ 70% component coverage |
| E2E tests | Playwright | All MVP user journeys |

---

## 2. Backend Testing

### 2.1 Unit Tests

**Location:** `backend/tests/unit/`

**Scope:** Domain model logic, service layer methods, utility functions, validation rules — isolated with mocked repositories and external clients.

**Tools:**
- `pytest` — test runner
- `pytest-asyncio` — async test support
- `unittest.mock` / `pytest-mock` — mocking
- `coverage` — coverage reporting

**Naming Convention:**
```
tests/unit/domain/test_aas_shell.py
tests/unit/services/test_aas_service.py
tests/unit/domain/test_certification_workflow.py
```

**Example structure:**
```python
# tests/unit/domain/test_certification_workflow.py
"""
Unit tests for the CertificationWorkflow state machine.

Tests that the workflow correctly transitions between states,
rejects invalid transitions, and records findings.
"""

class TestCertificationWorkflowTransitions:
    """Tests for workflow state machine transitions."""

    def test_approve_from_pending_transitions_to_approved(self):
        # Given: a workflow in PENDING_REVIEW state
        # When: approve() is called
        # Then: state becomes APPROVED
        ...

    def test_approve_from_rejected_raises_invalid_transition(self):
        # Given: a workflow in REJECTED state
        # When: approve() is called
        # Then: InvalidStateTransitionError is raised
        ...
```

### 2.2 Integration Tests

**Location:** `backend/tests/integration/`

**Scope:** Repository implementations (PostgreSQL + MongoDB), full service flows through the DB, Keycloak JWT validation.

**Tools:**
- `pytest` + `pytest-asyncio`
- `testcontainers-python` — starts ephemeral Docker containers for PostgreSQL, MongoDB, MinIO during testing
- No mocking of infrastructure layer (tests against real DB instances)

**Example:**
```python
# tests/integration/test_aas_repository.py
"""
Integration tests for the AAS MongoDB repository.

Uses TestContainers to spin up an ephemeral MongoDB instance.
Tests CRUD operations, pagination, and filter queries.
"""

@pytest.fixture(scope="session")
def mongo_container():
    with MongoDbContainer("mongo:7") as container:
        yield container

class TestAASRepository:
    async def test_create_and_retrieve_shell(self, aas_repo):
        # Given: a valid AAS domain object
        # When: saved to MongoDB
        # Then: retrieved object matches original
        ...
```

### 2.3 API / Contract Tests

**Location:** `backend/tests/api/`

**Scope:** FastAPI endpoint behavior, request/response contracts, authentication enforcement, HTTP error codes.

**Tools:**
- `httpx` + FastAPI `TestClient` (async mode)
- `pytest-mock` for mocking service layer

**Key test areas:**
- Each endpoint returns the correct HTTP status for each role (200, 403, 404, 422)
- Request validation errors return 422 with structured messages
- Auth-protected endpoints return 401 without a token

### 2.4 Security Testing (Automated)

| Tool | What it Checks | When |
|------|---------------|------|
| `bandit` | Python SAST (common security issues) | CI on every PR |
| `pip-audit` | Known CVEs in dependencies | CI on every PR |
| `schemathesis` | Fuzz testing against OpenAPI spec | CI nightly |
| `safety` | Additional Python dependency scan | CI on every PR |

---

## 3. Frontend Testing

### 3.1 Unit / Component Tests

**Location:** `frontend/src/**/*.test.tsx`

**Tools:**
- `Vitest` — fast test runner (Vite-compatible)
- `@testing-library/react` — component rendering and interaction
- `@testing-library/user-event` — user interaction simulation
- `msw` (Mock Service Worker) — API mocking in browser environment

**Key areas:**
- Rendering of all submodel viewer components with sample data
- Role guard renders/hides components based on role
- DPP form validation (client-side Zod schemas)
- API query hooks return correct loading/error/success states

### 3.2 Frontend Security Testing

| Tool | Purpose |
|------|---------|
| `eslint-plugin-security` | Detect XSS-prone patterns |
| `npm audit` | Dependency CVE scan |

---

## 4. End-to-End (E2E) Tests

**Location:** `e2e/`

**Tool:** Playwright (TypeScript)

**Strategy:** E2E tests run against the full Docker Compose stack (limited, stable containers) to validate critical user journeys.

### MVP E2E Test Scenarios

| Test ID | Journey | Roles Involved |
|---------|---------|---------------|
| E2E-01 | Create and publish a DPP with TechnicalData and Sustainability submodels | Manufacturer |
| E2E-02 | Share DPP with Auditor; Auditor reads but cannot edit | Manufacturer, Auditor |
| E2E-03 | Submit DPP for certification → Auditor approves → Certificate attached | Manufacturer, Auditor |
| E2E-04 | Record lifecycle event → visible in timeline | Manufacturer |
| E2E-05 | Export DPP as AASX → re-import → data intact | Manufacturer |
| E2E-06 | Customer accesses public DPP view without authentication | Customer (unauthenticated) |
| E2E-07 | Unauthorized access attempt returns 403 | Supplier (no grant) |

---

## 5. CI/CD Pipeline

### Pipeline Stages

```
Push / PR
    │
    ├── Lint (backend: ruff + mypy; frontend: eslint + tsc)
    │
    ├── Unit Tests (backend: pytest; frontend: vitest)
    │
    ├── Security Scans (bandit, pip-audit, npm audit)
    │
    ├── Build (backend: Docker build; frontend: vite build + Docker)
    │
    ├── Integration Tests (backend: pytest + TestContainers)
    │
    └── [main branch only]
         ├── E2E Tests (Playwright vs. Docker Compose stack)
         └── Publish Docker images (registry)
```

### Quality Gates (PR must pass)

- All unit tests pass
- Backend coverage ≥ 80%
- No `bandit` HIGH severity findings
- No `pip-audit` or `npm audit` critical CVEs unresolved
- TypeScript compiles with zero errors
- ESLint with zero errors

---

## 6. Test Data Management

- **Unit tests:** Use factory functions / builders to create domain objects (`AASFactory.build()`, `SubmodelFactory.build()`).
- **Integration tests:** Each test cleans up its own data; `testcontainers` starts fresh containers per test session.
- **E2E tests:** A dedicated seed script (`e2e/seed.ts`) populates the Docker Compose stack with a defined set of organizations, users, and DPPs before the E2E suite runs.
- **No production data** is ever used in any test environment.

---

## 7. Code Quality Standards

| Standard | Tool | Rule |
|----------|------|------|
| Python code style | `ruff` | PEP 8 + additional rules |
| Python type checking | `mypy` | Strict mode on domain and service layers |
| Python formatting | `black` | Enforced in CI |
| TypeScript linting | ESLint + typescript-eslint | Recommended ruleset + security rules |
| TypeScript formatting | Prettier | Enforced in CI |
| Import sorting | `isort` (Python) / ESLint (TS) | Enforced in CI |
| Commit messages | Conventional Commits | Enforced by `commitlint` |
| Branch name | `feat/`, `fix/`, `chore/` prefix | Enforced by PR rules |

---

## 8. Documentation Quality

- All public API endpoints must have an OpenAPI summary and description string.
- All domain service methods must have a docstring explaining inputs, outputs, and side effects.
- Any non-obvious algorithm or business rule must be explained with an inline comment.
- Each test file must have a module-level docstring explaining its scope and purpose.
- ADRs for architectural decisions are maintained in [11_risks_decisions.md](./11_risks_decisions.md).
