# Learnings

## Architecture and Planning

- Keep planning in `doc/planning` as modular files so implementation tickets and scaffolding can be derived directly.
- Separate domain model, persistence model, and API model to avoid framework-driven coupling.
- Use MUST/SHOULD/MAY prioritization in requirements to keep sprint slicing unambiguous.
- Use canonical repository paths (for example `doc/planning/...`) in prompt and agent files to prevent automation drift.

## Repository and Source Control

- Keep empty scaffold directories with `.gitkeep` so intended architecture remains visible in Git.
- Do not auto-approve state-changing terminal actions (`git add`, `git push`, installs, broad `gh` commands) in shared settings.
- Remove or ignore generated `backend/dpp_backend.egg-info` before committing.
- Ensure all text and Compose files end with a trailing newline to avoid noisy diffs.

## CLI and Automation

- Do not hard-code repository names in scripts; derive with `gh repo view --json nameWithOwner --jq .nameWithOwner` and keep a safe fallback.
- With `gh api --paginate`, merge pages before JSON parsing (`--slurp`) or force single page (`per_page=100`), otherwise `ConvertFrom-Json` can fail.

## Docker and Infrastructure

- For scaffold phases, placeholder service commands on stock images are acceptable if they provide reproducible startup.
- Pin Docker image tags; do not use `:latest`.
- Keep cross-service credentials/defaults consistent so stack startup does not require hidden bootstrap steps.
- When one PostgreSQL container serves multiple consumers, provision extra DBs/roles via init scripts in `/docker-entrypoint-initdb.d/`.
- Include observability and reproducibility concerns in Docker-first decisions from the start.

## Backend and Python

- Avoid import-time logging side effects; initialize logging during app startup.
- Add explicit `__init__.py` files in new Python package paths to keep pytest/mypy/ruff discovery predictable.

## Database and Migrations

- Use hybrid persistence intentionally: PostgreSQL for relational workflow/auth/audit data and MongoDB for AAS/Submodel documents.
- Read Alembic database configuration from application settings to keep one source of truth.
- For async-first apps, convert migration URLs to a sync SQLAlchemy driver for Alembic execution.
- If default `DATABASE_URL` uses `postgresql+asyncpg://`, include `asyncpg` explicitly in project dependencies.
- Add passthrough tests for URL conversion helpers to cover non-conversion branches.

## Frontend and TypeScript

- Keep Vite, Vitest, and React plugin versions mutually compatible.
- In project-reference setups, mark referenced configs as `composite` and run `tsc -b` for typecheck coverage.

## CI and Quality

- Prefer module-invoked tooling in CI (for example `python -m ruff`) to avoid PATH-dependent failures.
- Run lightweight markdown lint checks before PR creation to catch table and terminology issues.

## PR Review Workflow

- If MCP active PR lookup fails, fall back to `gh pr view <N> --json reviews,comments` plus `gh api repos/<owner>/<repo>/pulls/<N>/comments`.
- For true unresolved-review detection, query GraphQL `reviewThreads`; pull-review comments alone do not include thread resolution state.
