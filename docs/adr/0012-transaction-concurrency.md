# ADR-0012 — PostgreSQL transaction, isolation, locking and execution-leader fencing

| Thuộc tính | Giá trị |
|---|---|
| Status | DRAFT — required for Phase 0.0; chưa mở gate |
| Date | 2026-07-31 |
| Owner | Technical Operator |
| Approver | Account Owner |
| Related | FR-EXEC-001, FR-RSK-001, FR-LED-001, FR-REC-001, NFR-SAFE-001; [Master](../../AI_AUTO_TRADE_MASTER_SPEC.md) §7.2, §7.7, §8.5–§8.9; DATA-005 |
| Supersedes / superseded by | None / None |

## Context and decision drivers

Concurrent strategy decisions, retries, process restarts, publisher leases and venue uncertainty can create duplicate exposure or double booking without a transaction/locking policy. PostgreSQL can protect internal facts, but cannot atomically include an external venue API call. The policy must state exactly what is protected and what becomes reconciliation work.

## Proposed decision

If approved:

- Pre-submit `TradingSubmissionUnitOfWork` is `SERIALIZABLE` and spans risk decision/reservation, execution order/attempt and platform outbox only; no venue/network call occurs inside it.
- Lock order is `risk limit/reservation -> execution order -> platform outbox`.
- Mutable aggregates use non-negative version and compare-and-swap. Queue/outbox claims use short `SELECT FOR UPDATE SKIP LOCKED`, bounded lease, monotonic fencing token and CAS delivery version.
- Serialization/deadlock retry is bounded, occurs only before external action and reruns all validation/risk. External submit is never blind-retried.
- Verified fill/ledger and reconciliation workflows use the whitelisted unit-of-work maps in DATA-005, dedupe facts and persist outbox atomically.
- Only one execution leader claims a venue/account scope. Lease loss stops new claims; in-flight unknown request transitions to recovery/reconciliation.

No 2PC, distributed transaction, in-memory mutex or global request hash uniqueness is used as safety boundary.

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| Read committed only with application checks | insufficient for concurrent reservation/limit race without stricter proven design |
| Hold DB transaction during venue call | creates lock exhaustion and still cannot guarantee external atomicity |
| Retry submit after timeout | can duplicate venue order |
| Exactly one process by deployment convention | crash/split-brain cannot be safely assumed away |
| Distributed lock/broker first | new availability/consistency dependency before PostgreSQL-based proof |

## Consequences

Transaction retry, lease/claim, state version, idempotency scopes, lock/latency telemetry and crash/chaos tests are mandatory. `UNKNOWN`/`RECONCILING` become normal observable operational states. Any new cross-context transaction needs an owner-table map and ADR/task amendment. Fencing does not protect venue API; client order identity plus reconciliation remain required.

## Migration, rollout and rollback/forward-fix

Task 0.3 only prepares delivery baseline under this policy. Phase 1 proves fake-venue racing/restart cases before external integration. Changing isolation/lock order/idempotency scope is a safety/domain/data change requiring new ADR, migration/contract/test evidence and staged rollout. Recovery favors freeze/reconcile/forward-fix, not re-submit.

## Approval criteria

- [ ] Account Owner accepts serializable pre-submit/no-external-call/no-blind-retry rules.
- [ ] DATA-005 transaction maps and platform dictionary are reviewed.
- [ ] Tests/evidence cover competing reservations, duplicate publish/consume/fill, crash boundaries, lease loss and unknown outcome.

