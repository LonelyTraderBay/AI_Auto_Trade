# ADR-0012 — PostgreSQL transaction, isolation, locking and execution-leader fencing

| Thuộc tính | Giá trị |
|---|---|
| ADR ID | ADR-0012 |
| Phiên bản | 0.3.0 |
| Status | APPROVED — baseline 2026-08-06; Task 1.3 amendment approved 2026-08-12T09:19:16Z |
| Date | 2026-07-31 |
| Owner | Technical Operator |
| Approver | Account Owner |
| Effective date | 2026-08-06 |
| Decision deadline | Phase 0.0 gate |
| Rà soát gần nhất | 2026-08-12 |
| Related | FR-EXEC-001, FR-RSK-001, FR-LED-001, FR-REC-001, NFR-SAFE-001; [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §7.2, §7.7, §8.5–§8.9; DATA-005 |
| Supersedes / superseded by | None / None |
| Change summary | 0.3.0 (2026-08-12): resolve `If approved`/DRAFT contradiction for Task 1.3; approve fill/reconciliation `READ COMMITTED` + unique dedupe + CAS boundary and local-simulator lease values under approval record GOV-TASK-1.3-APPROVAL-20260812-091916. |

## Context and decision drivers

Concurrent strategy decisions, retries, process restarts, publisher leases and venue uncertainty can create duplicate exposure or double booking without a transaction/locking policy. PostgreSQL can protect internal facts, but cannot atomically include an external venue API call. The policy must state exactly what is protected and what becomes reconciliation work.

## Decision

- Pre-submit `TradingSubmissionUnitOfWork` is `SERIALIZABLE` and spans risk decision/reservation, execution order/attempt and platform outbox only; no venue/network call occurs inside it.
- Lock order is `risk limit/reservation -> execution order -> platform outbox`.
- Mutable aggregates use non-negative version and compare-and-swap. Queue/outbox claims use short `SELECT FOR UPDATE SKIP LOCKED`, bounded lease, monotonic fencing token and CAS delivery version.
- Serialization/deadlock retry is bounded, occurs only before external action and reruns all validation/risk. External submit is never blind-retried.
- Verified fill/ledger and reconciliation workflows use the whitelisted unit-of-work maps in DATA-005, dedupe facts and persist outbox atomically. `FillLedgerUnitOfWork` and `ReconciliationResolutionUnitOfWork` use `READ COMMITTED` + unique-constraint dedupe (`venue_fill_id` in venue/account scope, or source-event fingerprint when absent; journal by `source_event_id`) + compare-and-swap on aggregate version. This is sufficient because facts are append-only immutable and dedupe is enforced by constraint; `TradingSubmissionUnitOfWork` remains `SERIALIZABLE`.
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

- [x] Account Owner accepts serializable pre-submit/no-external-call/no-blind-retry rules.
- [x] DATA-005 transaction maps and platform dictionary are reviewed.
- [x] Tests/evidence cover competing reservations, duplicate publish/consume/fill, crash boundaries, lease loss and unknown outcome.

## Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.3.0 | 2026-08-12 | Resolve `If approved`/DRAFT contradiction; approve fill/reconciliation isolation, dedupe and CAS wording for Task 1.3 local simulator. | Technical Operator | Approval record `2026-08-12T09:19:16Z` |
| 0.2.0 | 2026-08-06 | Status → APPROVED; Account Owner decision 2026-08-06T00:00:00Z. | Account Owner | Account Owner |

