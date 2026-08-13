# Task 1.3.1 — Evidence redaction report

| Field | Value |
|---|---|
| Document ID | GOV-TASK-1.3.1-REDACTION-20260813 |
| Decision UTC | 2026-08-13T14:03:02Z |
| Task branch | `task/1.3.1-evidence-redaction` |
| Target | `docs/governance/evidence/tasks/0.3/persistence-evidence.md` |
| Affected line | 68 |
| SHA-256 before | `320f73a9a027424c50b4f9ff85fe4c84e38fc133c0fe3ce019590a2798a43e1c` |
| SHA-256 after | `3ee0faf53e5d380309441a24c9e4cd0f47c030901b2deec86b4ae5730ce6babe` |
| Operator | Technical Operator |
| Account Owner action | Approved at `2026-08-13T13:27:48Z` |
| Security/Backup Owner action | Approved at `2026-08-13T14:01:57Z` |
| Proposed status | REVIEW |

## Change

The credential-like PostgreSQL DSN was removed from the historical procedure.
The procedure now instructs the operator to provide `DATABASE_URL` through the
process environment without printing or persisting its value, then run the
integration test.

The removed value is not reproduced in this report or any new artifact. No
runtime code, migration, configuration, database, Docker or Supabase state was
changed.

## Verification

- Target scan: no credential-like PostgreSQL DSN remains.
- Repository scan: only pre-existing local/template placeholders remain in
  `.env.example` and `pyproject.toml`; neither was modified or expanded.
- Diff scope is limited to the Task 1.3.1 allowlist.

## Final post-redaction command evidence

Run UTC: `2026-08-13T14:05:02Z`

| Command | Result |
|---|---|
| `uv sync --locked` | PASS |
| `uv run ruff format --check .` | PASS — 223 files already formatted |
| `uv run ruff check .` | PASS |
| `uv run pyright` | PASS — 0 errors, 0 warnings, 0 informations |
| `uv run pytest` | PASS — 103 passed, 1 skipped |
| `uv run python scripts/validate_contracts.py` | PASS — all 14 schemas valid |
| `git diff --check` | PASS |
