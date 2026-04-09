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

## 2026-04-09

- Repository scaffold commits should include `.gitkeep` placeholders in empty domain folders to preserve intended architecture in Git.
- `gh api --paginate` emits one JSON array per page rather than a single merged array; piping multi-page output into `ConvertFrom-Json` fails silently or throws. Use `per_page=100` (single request) or `--slurp` (merge pages) when the result must be parsed as a PowerShell object.
- Hard-coding a target repository in automation scripts creates risk when executing from forks or renamed repos. Prefer `gh repo view --json nameWithOwner --jq .nameWithOwner` to derive the repo dynamically, with a safe hard-coded fallback.
- For scaffold-phase Docker Compose setup, placeholder service commands using stock runtime images can provide a reproducible integration baseline without prematurely locking backend/frontend build conventions.
- When sharing a single PostgreSQL container between multiple services (e.g., the app DB and Keycloak), use a PostgreSQL init script mounted at `/docker-entrypoint-initdb.d/` to provision additional databases and roles on first start. Pass the required env vars into the postgres service so the script can read them.
- Docker Compose files and all text configuration files should always end with a trailing newline to conform to POSIX convention and avoid noisy diffs.
- Avoid `image: <name>:latest` in Docker Compose files; pin to a specific release tag so stack behaviour is reproducible and upgrades are explicit.
- Docker Compose scaffolds should keep cross-service defaults consistent (for example, Keycloak/Postgres DB credentials) so local startup succeeds without hidden bootstrap SQL steps.
- Running `pip install -e .` inside `backend/` creates `backend/dpp_backend.egg-info`; remove or ignore this generated artifact before committing to keep changesets source-only.
- Application modules should avoid import-time logging side effects; initialize logging during app startup to keep imports deterministic for tests and tooling.
- Vite, Vitest, and the React plugin should stay on compatible major versions; otherwise `vite.config.ts` can fail TypeScript builds even when runtime tooling appears correctly configured.
