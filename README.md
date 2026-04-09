# Digital Product Passport

This repository contains the planning artifacts and implementation scaffold for the Digital Product Passport project.

The current state reflects Sprint 0 structure enablement only. No application features are implemented yet. The repository now provides the directory layout and onboarding entry points required for follow-up issues to add backend, frontend, infrastructure, and CI functionality incrementally.

## Repository Layout

```text
.
|-- backend/        Python/FastAPI service scaffold and test layout
|-- doc/            Planning, seed material, and project documentation
|-- frontend/       React/TypeScript application scaffold layout
|-- infra/          Docker, auth, observability, and operations scaffold
|-- LEARNINGS.md    Repository learnings captured during implementation
`-- ensure-milestones.ps1
```

## Developer Onboarding

1. Read the planning overview in `doc/planning/README.md`.
2. Use the folder READMEs in `backend/`, `frontend/`, and `infra/` to understand the intended implementation boundaries.
3. Copy `.env.example` to `.env` when runtime configuration is introduced by later Sprint 0 issues.
4. Implement application code only in the follow-up setup issues for backend, frontend, Docker Compose, and CI.

## Current Boundaries

- This scaffold intentionally contains no runnable backend or frontend code yet.
- The directory structure mirrors the architecture described in `doc/planning/05_system_architecture.md` and `doc/planning/07_modules.md`.
- Infrastructure directories are placeholders for later issues such as Docker Compose, Keycloak realm setup, observability, and recovery runbooks.

## Related Planning Documents

- `doc/planning/05_system_architecture.md`
- `doc/planning/07_modules.md`
- `doc/planning/08_backlog_roadmap.md`
- `doc/planning/10_operations_observability.md`