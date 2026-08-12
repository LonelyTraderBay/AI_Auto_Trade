# Task 1.3 — Supabase Local PostgreSQL 17 installation evidence

| Field | Value |
|---|---|
| Date | 2026-08-12 |
| Branch | `task/1.3-durable-submit-fake-venue` |
| CLI | Supabase `2.113.0` via `npx --yes supabase@2.113.0` |
| Project | `AI_Auto_Trade` |
| Database | `postgres` on `127.0.0.1:54322` |
| Proposed state | PostgreSQL environment `PASS`; Task 1.3 card remains `BLOCKED` pending explicit `READY` transition |

## Installation and verification

| Check | Result | Evidence |
|---|---|---|
| Docker daemon | PASS | Docker Server `29.7.2` |
| Supabase project initialization | PASS | `supabase init --yes` generated `supabase/config.toml` and `.gitignore` |
| PostgreSQL major version | PASS | `supabase/config.toml` sets `db.major_version = 17`; SQL query reports server `17.6` |
| Supabase Local startup | PASS | `supabase start` created the `AI_Auto_Trade` project containers; database is healthy |
| Test query | PASS | `select current_database(), current_setting('server_version')` → `postgres`, `17.6` |
| Schema query | PASS with advisory | `platform.outbox` and `platform.inbox` exist; Supabase advisor reports RLS disabled on `public.alembic_version` |
| Alembic baseline | PASS | Existing migrations applied with `alembic upgrade head` using an ephemeral local URL |
| Migration integration test | PASS | `uv run pytest tests/integration/test_platform_migrations.py -q` → `1 passed` |
| Full test suite with DB URL | PASS | `uv run pytest` → `104 passed` |
| Quality commands | PASS | `uv sync --locked`, Ruff format/check, Pyright, contract validation all exit `0` |

## Service note

The core services (database, PostgREST, Auth, Storage, Realtime, Kong,
Mailpit, Studio and edge runtime) are running for `AI_Auto_Trade`. The optional
Vector analytics container restarts on this Windows Docker Desktop host because
its Docker-log source cannot connect to the host Docker API; database/API
verification is unaffected. No production or venue credential is configured.

## Safety and authority

- `DATABASE_URL` was supplied only to the migration/test process and was not
  written to the repository, config, shell profile or evidence.
- Alembic under `migrations/` remains the application schema authority; the
  Supabase Local migration/reset workflow is not used for application DDL.
- Supabase Local is development-only and is not an approval for external venue,
  live trading, ledger activation or production deployment.
- Security follow-up is open: Supabase reports `public.alembic_version` with RLS
  disabled. No remediation was auto-applied. Before any API exposure, the owner
  must choose a reviewed policy or move the Alembic version table to a private
  schema. Enabling RLS without policies would block all client-role access.
- Task 1.3 must remain `BLOCKED` until the Account Owner explicitly transitions
  the canonical card to `READY`; this evidence does not self-approve that gate.
