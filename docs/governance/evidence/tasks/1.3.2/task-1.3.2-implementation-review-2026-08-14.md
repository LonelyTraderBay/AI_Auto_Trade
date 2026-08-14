# Task 1.3.2 — implementation and verification evidence

| Field | Value |
|---|---|
| Document ID | `EV-TASK-1.3.2-IMPLEMENTATION-20260814` |
| Task | `1.3.2` — durable-submit hardening |
| Card status | `REVIEW` — Account Owner `DONE` decision required |
| Branch | `task/1.3.2-durable-submit-hardening` |
| Scope decision | Account Owner transition `BLOCKED → READY` at `2026-08-14T04:48:21Z`; scope, allowlist, ADRs, contracts and non-goals unchanged |
| Runtime boundary | Supabase Local/PostgreSQL only; no external venue, credential, ledger, public API or AI execution |

## Delivered

- Added a framework-independent submission safety contract for explicit UTC lease, fencing and kill-switch context, risk freshness, reservation binding and request identity.
- Added `PostgresTradingSubmissionUnitOfWork` with a `SERIALIZABLE` pre-submit transaction that persists risk reservation/decision, queued order, first conservative `UNKNOWN` attempt, reconciliation case, immutable lifecycle event and platform outbox/delivery state before the fake venue call.
- Added a claim phase before the venue call and a fenced response phase with lifecycle CAS, immutable event/outbox append, reconciliation resolution, fill fingerprint dedupe and canonical replay.
- Added outbox claim/publish CAS and inbox receipt dedupe for duplicate publish/consume recovery.
- Added negative and fault-boundary tests for expiry, quantity mismatch, kill switch, hash conflict, lease loss, crash-before-call, crash-after-apply-before-ack, UNKNOWN recovery, fill dedupe and duplicate delivery.

## Acceptance trace

| Acceptance area | Evidence |
|---|---|
| Atomic pre-submit persistence | `tests/integration/test_task_1_3_2_postgres.py::test_atomic_submit_replay_and_delivery_dedupe`; verifies 1 decision, 1 reservation, 1 order, 1 attempt, 3 lifecycle events, 3 outbox rows and 1 reconciliation case |
| Expiry/reservation/kill-switch/fencing | `test_expired_quantity_and_kill_switch_fail_closed`; `test_unknown_restart_and_lease_loss_never_resubmit` |
| Replay and hash conflict | Atomic integration test replays without a second venue effect and rejects changed request data with `SubmissionConflictError` |
| UNKNOWN and reconciliation | Unknown integration test verifies replay remains `UNKNOWN`, case remains `OPEN`, and blind retry is blocked |
| Duplicate/out-of-order/fill safety | Lifecycle sequences are exactly `[1, 2, 3]`; duplicate response leaves one fill; outbox publish/consume returns `True` then `False` for the duplicate receipt |
| Crash/restart boundaries | `test_crash_boundaries_and_duplicate_response_are_recoverable` |
| Contract and architecture boundary | Domain/application imports remain vendor/framework independent; no migration, dependency or contract file changed |

## Commands and results

All commands were run on 2026-08-14. The PostgreSQL commands used a process-only local connection environment; the connection URL and credentials were not written to this evidence.

| Command | Result |
|---|---|
| `uv sync --locked` | PASS — 45 packages resolved/checked |
| `uv run ruff format --check .` | PASS — 241 files already formatted |
| `uv run ruff check .` | PASS |
| `uv run pyright` | PASS — 0 errors, 0 warnings, 0 informations |
| `uv run pytest` | PASS — `117 passed` |
| `uv run pytest tests/integration/test_task_1_3_2_postgres.py -q` | PASS — `4 passed`, PostgreSQL no-skip |
| `uv run pytest tests/integration -q` | PASS — `8 passed`, PostgreSQL no-skip |
| `uv run python scripts/validate_contracts.py` | PASS — all 14 JSON schemas valid |
| `git diff --check` | PASS at verification run; rerun after evidence staging before commit |
| staged high-confidence secret scan | PASS — 0 hits |

## Artifact hashes

SHA-256 hashes were captured before writing this evidence file:

```text
288566891d0d3acf44d4312da21d8d3eff2843bf19bc323d5a174bb20c9c7d0e  src/ai_auto_trade/adapters/persistence/durable_submission.py
9f5033be540518c210020dba6d8578878460ced296fd98a62be8c687dfc0157c  src/ai_auto_trade/contexts/execution/application/durable_submit.py
fdf82574ed92df3c914713cb8170818699d995398b89f88658348ae9a9dca9f6  src/ai_auto_trade/contexts/execution/domain/submit_contract.py
6a469eefe28619fcd0cca6bdbaa46d5b584b8a08407cd3789adcd000901ebf2c  tests/integration/test_task_1_3_2_postgres.py
1accce8add5b990f95fe822a98002c27e8351c8ea3e702fb5870ffdf74c1f02e  tasks/active/1.3.2-durable-submit-hardening.yaml
```

## Review boundary

The implementation is proposed for `REVIEW` only. Account Owner must inspect the diff/evidence and explicitly decide `REVIEW → DONE`; no human gate, waiver, ADR or phase gate was self-approved. External venue, ledger activation and AI-to-execution remain blocked.
