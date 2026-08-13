# Task 1.3 — Automated one-time approval self-check

| Field | Value |
|---|---|
| Document ID | GOV-TASK-1.3-SELF-CHECK-20260813 |
| Version | 0.1.0 |
| Run UTC | 2026-08-13T13:31:21Z |
| Branch | `task/1.3-durable-submit-fake-venue` |
| Script | [`task-1.3-self-check.ps1`](task-1.3-self-check.ps1) |
| Result | **BLOCKED/FAIL — review required** |

## Scope

This is a governance/preflight check only. It does not implement Task 1.3,
approve an ADR, change a gate, or authorize external venue/ledger/AI runtime.
The database URL was used only in the test process and was not written to the
repository or evidence.

Run command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\docs\governance\evidence\tasks\1.3\task-1.3-self-check.ps1 -StartSupabase
```

## Result summary

| Result | Count |
|---|---:|
| PASS | 18 |
| INFO | 4 |
| BLOCKED | 1 |
| FAIL | 2 |

## Checks passed

- Branch matches `task/1.3-*`.
- Task card has all 22 required structural fields.
- Quality and integration checks pass; the current Task 1.3 allowlist check
  deliberately flags the separately approved cleanup card as out-of-scope for
  this branch.
- All 18 required authority/evidence paths checked by the script exist.
- Fake-venue scenario fixture validates against its Draft 2020-12 schema.
- All 14 repository JSON Schemas validate.
- Approved risk fixture metadata is valid; file SHA-256:
  `234e93ab1e06a9c0240cbde89a20b78aada70597b5a72d015c6b03bad0d8e113`.
- `uv sync --locked` passed.
- Ruff format, Ruff check and Pyright passed.
- Full pytest passed without a database URL.
- Docker daemon and Supabase Local start passed.
- PostgreSQL integration suite passed with a process-only local `DATABASE_URL`.
- Full pytest with the process-only database URL passed: `104 passed`.
- `git diff --check` passed.
- Changed files contain no trailing whitespace.

Evidence hashes:

- `task-1.3-self-check.ps1`: `c900e179fe80ade4195a1a35a4c7e40dc8a8e075fafa1a6429b9cd8ba2e4dcb2`

## Remaining blockers and follow-ups

1. The canonical card remains `BLOCKED`. Only the Account Owner/reviewer may
   transition it to `READY`; the self-check deliberately exits non-zero for
   this condition.
2. The current Task 1.3 allowlist check flags
   `tasks/active/1.3.1-evidence-secret-redaction.yaml`. This is a separate
   governance card, not Task 1.3 implementation; cleanup execution requires
   its own `task/1.3.1-*` branch and clean working tree.
3. The task-specific file
   `tests/integration/test_task_1_3_postgres.py` and migration
   `migrations/versions/0003_task_1_3_execution_risk.py` do not exist yet.
   This is expected before implementation and must be produced only after the
   card is `READY`.
4. The secret scan found a credential-like PostgreSQL DSN in the historical
   file `docs/governance/evidence/tasks/0.3/persistence-evidence.md`. That file
   is outside Task 1.3's allowlist, so it was not modified. A separate
   authorized redaction/cleanup task is required before claiming a repository-wide
   clean secret boundary.
5. `pyproject.toml` contains a local placeholder database credential. The
   self-check reports it as informational only; it is outside the current card's
   allowed scope and must not be used for any external service.

## Approval boundary

The package is ready for human review of the local-simulator scope and
preconditions. It is not evidence that Task 1.3 runtime acceptance criteria
have passed, and it does not authorize implementation until the canonical card
is explicitly changed to `READY`.
