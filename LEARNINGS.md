# Learnings

## 2026-04-08

- A multi-file planning structure in `doc/planning` improves maintainability and allows direct derivation of implementation tickets, ADRs, and module scaffolding.
- For AAS-based DPP systems, separating domain model, persistence model, and API model is essential to avoid coupling framework concerns to business semantics.
- A hybrid persistence strategy (PostgreSQL for relational workflow/auth/audit data and MongoDB for AAS/Submodel documents) aligns well with DPP data characteristics.
- Docker-first architecture decisions should include not only runtime services (frontend, backend, databases, auth) but also observability and local reproducibility from the start.
- Explicit MUST/SHOULD/MAY requirement prioritization reduces ambiguity and makes roadmap slicing significantly easier.
- Prompt and agent files should reference canonical repository paths (`doc/planning/...`) to avoid drift between generated documentation and automation prompts.
- Shared repository settings should avoid auto-approving state-changing terminal commands (`git push`, `git add`, package installs, broad `gh` commands) to reduce accidental destructive operations.
- Documentation quality checks should include a lightweight markdown lint pass for table integrity and terminology consistency before opening PRs.
