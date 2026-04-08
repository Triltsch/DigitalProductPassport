# Digital Product Passport — Project Planning

## Overview

This directory contains the complete, structured project planning for the **Digital Product Passport (DPP)** system based on the **Asset Administration Shell (AAS)** standard.

The DPP system provides a lifecycle-spanning digital representation of physical products, enabling traceability, sustainability reporting, compliance verification, and multi-stakeholder collaboration across the entire product value chain.

---

## Document Index

| File | Topic | Summary |
|------|-------|---------|
| [00_executive_summary.md](./00_executive_summary.md) | Executive Summary | Vision, value proposition, high-level architecture overview |
| [01_stakeholder_roles.md](./01_stakeholder_roles.md) | Stakeholders & Roles | Stakeholder analysis, role model, permission matrix |
| [02_requirements.md](./02_requirements.md) | Requirements | Functional and non-functional requirements, prioritization |
| [03_user_journeys.md](./03_user_journeys.md) | User Journeys | Use cases, user flows, key interactions per role |
| [04_domain_model.md](./04_domain_model.md) | Domain Model | Entities, relationships, AAS submodel mapping |
| [05_system_architecture.md](./05_system_architecture.md) | System Architecture | Architecture decisions, backend, frontend, persistence, Docker topology |
| [06_security_compliance.md](./06_security_compliance.md) | Security & Compliance | Authentication, authorization, data protection, EU DPP regulations |
| [07_modules.md](./07_modules.md) | Modules | Module structure, responsibilities, inter-module dependencies |
| [08_backlog_roadmap.md](./08_backlog_roadmap.md) | Backlog & Roadmap | MVP definition, sprint roadmap, milestones |
| [09_testing_quality.md](./09_testing_quality.md) | Testing & Quality | Test strategy, quality gates, CI/CD integration |
| [10_operations_observability.md](./10_operations_observability.md) | Operations | Docker deployment, local dev environment, monitoring, logging, secrets |
| [11_risks_decisions.md](./11_risks_decisions.md) | Risks & Decisions | Architecture decisions (ADRs), risks, trade-offs |

---

## Key Technology Choices

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Backend framework | Python / FastAPI | Performance, AAS SDK compatibility, async support |
| AAS SDK | [BaSyx Python SDK](https://github.com/eclipse-basyx/basyx-python-sdk) | Eclipse DPP4.0 compliant, active community |
| Database | PostgreSQL + MongoDB | Relational for metadata/auth; document store for AAS objects |
| Frontend | React (TypeScript) | Component-based UI, role-adaptive views, wide ecosystem |
| Auth | Keycloak (OIDC/OAuth2) | Industry-standard IAM, RBAC support |
| Container | Docker + Docker Compose | Reproducible environments, production-grade deployment |
| API gateway | Traefik | Dynamic routing, TLS termination, low configuration overhead |

---

## How to Use This Planning Document

1. **Start with [00_executive_summary.md](./00_executive_summary.md)** to understand the overall vision and scope.
2. **Read [02_requirements.md](./02_requirements.md)** to understand what must be built.
3. **Refer to [05_system_architecture.md](./05_system_architecture.md)** for implementation guidance.
4. **Use [07_modules.md](./07_modules.md) and [08_backlog_roadmap.md](./08_backlog_roadmap.md)** to plan implementation sprints.
5. **Consult [11_risks_decisions.md](./11_risks_decisions.md)** before making architectural changes.

---

## Standards & References

- [IDTA Digital Product Passport](https://industrialdigitaltwin.org/dpp4-0)
- [Eclipse BaSyx Python SDK](https://github.com/eclipse-basyx/basyx-python-sdk)
- [AAS Part 1 — Metamodel (IEC 63278-1)](https://www.plattform-i40.de/)
- [EU Battery Regulation 2023/1542](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R1542)
- [ESPR — Ecodesign for Sustainable Products Regulation](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52022PC0142)
