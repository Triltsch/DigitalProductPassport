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
- In solution-style TypeScript setups that use project references, referenced configs should be `composite`, and repository `typecheck` scripts should use `tsc -b` so the referenced projects are actually validated.
- CI lint steps should prefer module invocation (for example `python -m ruff`) over bare executables to avoid PATH-specific failures across different runner and shell environments.
- In MCP-first PR review workflows, `github-pull-request_activePullRequest` can return "There is no active pull request" even when the checked-out branch matches the PR head; in that case, use the explicit fallback `gh pr view <N> --json reviews,comments` plus `gh api repos/<owner>/<repo>/pulls/<N>/comments` to ensure review coverage.
- PR review thread resolution state is not available from `gh api repos/<owner>/<repo>/pulls/<N>/comments` alone; use the GraphQL `reviewThreads` query to filter truly unresolved and non-outdated feedback.
- Alembic migration environments should read database URLs from application settings (via Pydantic config) to maintain a single source of truth; this is especially important for async-first backends where the application URL uses `+asyncpg` but migrations require a sync driver like `+psycopg`.
- When adding a new async driver alias (e.g. `postgresql+asyncpg://`) as the default `DATABASE_URL`, `asyncpg` must be listed as an explicit dependency in `pyproject.toml`; omitting it causes `ModuleNotFoundError` at runtime even though the application configuration itself loads fine without it.
- All new Python packages (`app/infrastructure/`, `app/infrastructure/db/`, migrations directories) should carry explicit `__init__.py` files to prevent namespace-package ambiguity and keep tool discovery (pytest, mypy, ruff) predictable.
- Branch-coverage gaps in `alembic_database_url`-style property helpers should be caught by a dedicated passthrough test that sets a non-asyncpg URL and asserts the value is returned unchanged.
