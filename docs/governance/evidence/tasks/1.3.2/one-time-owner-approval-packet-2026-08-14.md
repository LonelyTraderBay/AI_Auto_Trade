# Task 1.3.2 — One-time owner approval packet

| Field | Value |
|---|---|
| Document ID | GOV-TASK-1.3.2-APPROVAL-PACKET-20260814 |
| Prepared UTC | 2026-08-14 |
| Proposed task | `1.3.2` — durable-submit hardening |
| Current card status | `BLOCKED` |
| Proposed transition | `BLOCKED → READY` |
| Reviewer | Account Owner — pending decision |

## Scope prepared for one approval

This bounded card closes the remaining local-only durability/recovery gaps after
Task 1.3: transactional persistence before venue I/O, risk approval expiry and
reservation matching, idempotent replay, UNKNOWN reconciliation, fencing/lease
loss, duplicate/out-of-order delivery and deterministic crash/restart tests.

It explicitly excludes external venue access, credentials, testnet/live trading,
ledger activation, public API changes, AI execution, new dependencies and schema
changes. The canonical scope is the YAML card:

`tasks/active/1.3.2-durable-submit-hardening.yaml`

## Preflight already verified

- Task 1.3 is `DONE` in `tasks/completed/`.
- Current repository quality is green: full local self-check
  `PASS=23 INFO=2 BLOCKED=0 FAIL=0`.
- PostgreSQL/Supabase Local integration runs without skip: `113 passed`.
- Ruff, Pyright, all 14 JSON Schemas, allowlist, diff and secret checks pass.
- No current active card is `READY`; Task 1.3.1 remains `REVIEW`.

## Account Owner decision to record

Before implementation, record one separate owner action containing:

```text
Task 1.3.1: REVIEW -> DONE, if the redaction evidence is accepted.
Task 1.3.2: BLOCKED -> READY, with the YAML scope unchanged.
Actor/role: Account Owner
UTC timestamp: <record at decision time>
Branch precondition: task/1.3.2-*
Evidence: this packet plus the card-specific preflight artifacts.
```

The coding agent must not fill the timestamp, self-approve either transition,
or begin implementation before the owner decision is recorded.
