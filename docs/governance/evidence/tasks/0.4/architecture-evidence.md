# Task 0.4 — Architecture Contract Evidence

| Field | Value |
|---|---|
| Task ID | 0.4 |
| UTC Timestamp | 2026-08-06T16:30:00Z |
| Proposed Status | REVIEW |

## Required Commands

| Command | Exit Code |
|---|---|
| uv sync --locked | 0 |
| uv run ruff format --check . | 0 |
| uv run ruff check . | 0 |
| uv run pyright | 0 |
| uv run pytest | 0 |
| uv run python scripts/validate_contracts.py | 0 |

## Tests added

- tests/architecture/test_import_boundaries.py: 4 tests (expanded from 1)
- tests/contract/test_event_envelope.py: 7 tests (new)
- Total new/expanded tests: +10

## Import contracts added to .importlinter

- app-no-adapter: Application layer must not import adapters
- domain-no-application: Domain layer must not import application or adapter layers

## Files created/modified

- tasks/active/0.4-architecture-contract.yaml (created)
- .importlinter (modified — 2 contracts appended: app-no-adapter, domain-no-application)
- tests/architecture/test_import_boundaries.py (expanded — 4 tests total, was 1)
- contracts/fixtures/integration-event-envelope.v1.valid.json (updated with received_at/processed_at nullable fields)
- tests/contract/__init__.py (created)
- tests/contract/test_event_envelope.py (created — 7 tests)
- migrations/versions/0002_platform_idempotency_keys.py (created)
- docs/governance/evidence/tasks/0.4/architecture-evidence.md (this file)

## pytest summary

14 passed, 1 skipped (integration test — requires live DB)

## Proposed status: REVIEW
