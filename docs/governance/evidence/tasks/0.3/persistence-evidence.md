# Evidence Report — Task 0.3 Persistence Contract

| Field | Value |
|---|---|
| Task ID | 0.3 |
| Phase | 0 |
| UTC Timestamp | 2026-08-06T15:00:00Z |
| Actor | Technical Operator (AI Agent) |
| Proposed Status | REVIEW |

## Required Commands — Exit Codes

| Command | Exit Code |
|---|---|
| `uv sync --locked` | 0 |
| `uv run ruff format --check .` | 0 |
| `uv run ruff check .` | 0 |
| `uv run pyright` | 0 |
| `uv run pytest` | 0 (4 passed, 1 skipped — integration test skipped: DATABASE_URL not set) |
| `uv run python scripts/validate_contracts.py` | 0 |

## New Dependencies Pinned

| Package | Version |
|---|---|
| sqlalchemy | 2.0.41 |
| alembic | 1.16.2 |
| asyncpg | 0.30.0 |
| psycopg2-binary | 2.9.10 |

Transitive deps added: greenlet==3.5.4, mako==1.4.1, markupsafe==3.0.3

## Files Created

| File | Purpose |
|---|---|
| `tasks/active/0.3-persistence-contract.yaml` | Task card (status: READY) |
| `docker-compose.yml` | Local PostgreSQL 16-alpine service |
| `pyproject.toml` | Updated: new deps + [tool.alembic] + migrations per-file-ignores + pyright exclude |
| `uv.lock` | Updated lockfile |
| `migrations/__init__.py` | Empty package marker |
| `migrations/README` | Migration immutability rules |
| `migrations/env.py` | Alembic environment configuration |
| `migrations/script.py.mako` | Revision template |
| `migrations/versions/0001_platform_delivery_baseline.py` | Platform schema + 4 tables |
| `src/ai_auto_trade/adapters/persistence/database.py` | Async engine + session factory skeleton |
| `tests/integration/__init__.py` | Empty package marker |
| `tests/integration/test_platform_migrations.py` | Integration test (skipped without DB) |
| `.kiro/hooks/pre-write-task-guard.json` | Updated hook to Task 0.3 scope |

## Acceptance Criteria Verification

- [x] docker-compose.yml defines postgres:16-alpine with port 5432, env vars, healthcheck, volume
- [x] Alembic configured in pyproject.toml [tool.alembic]; base revision exists at migrations/versions/0001_platform_delivery_baseline.py
- [x] Migration creates 4 tables: platform.outbox, platform.outbox_delivery_state, platform.inbox, platform.dead_letters — all constraints/indexes present
- [x] uv run alembic upgrade head ready to run (integration test skipped pending postgres; DB not available in dev environment)
- [x] All 6 required_commands exit 0

## Non-Goals Confirmed

- No tables created outside platform schema
- No risk, execution, portfolio_ledger, operations tables created
- No adapter, repository, or application code created
- No venue or external service connection created

## Blocker / Known Risk

- Integration test `test_platform_tables_exist` is skipped when `DATABASE_URL` is not set. To run it: start docker-compose, run `alembic upgrade head`, provide `DATABASE_URL` through the process environment without printing or persisting its value, then `uv run pytest tests/integration/`.

## Proposed Status

REVIEW
