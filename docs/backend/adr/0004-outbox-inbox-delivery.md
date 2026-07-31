# ADR-0004 — Outbox/inbox at-least-once delivery and compatibility

| Thuộc tính | Giá trị |
|---|---|
| Status | DRAFT — required for Phase 0.0; chưa mở gate |
| Date | 2026-07-31 |
| Owner | Technical Operator |
| Approver | Account Owner |
| Related | FR-EXEC-001, FR-REC-001, NFR-AUD-001, NFR-SAFE-001; [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §5.7–§5.8, §7.1–§7.3, §7.13; DATA-003, DATA-005 |
| Supersedes / superseded by | None / None |

## Context and decision drivers

An order/fill/risk/ledger change must not be committed while its downstream event is silently lost. Conversely, crashes and network faults make exactly-once delivery impossible in this topology. Consumers must tolerate duplicate/out-of-order input while preserving aggregate ordering and evidence.

## Proposed decision

If approved, delivery is at least once:

1. Producer persists its aggregate state, immutable event and immutable `platform.outbox` message in one PostgreSQL transaction.
2. Publisher claims delivery state after commit, publishes outside the transaction and records result/retry/DLQ evidence with short lease/CAS transaction.
3. Consumer validates schema/version and atomically writes its local state/outbox plus immutable `platform.inbox` receipt unique on `(consumer_id,event_id)`.
4. Events are versioned envelopes with schema/fixture/compatibility test. Ordering is guaranteed only by documented aggregate/partition key; order lifecycle uses `order_id`.
5. Failure uses bounded retry/backoff and redacted DLQ evidence. Financial/audit event is never dropped to reduce backlog.

In-process bus dispatches only committed events and never replaces outbox across process boundaries.

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| Exactly-once promise | unverifiable across crash/network/consumer boundaries; would hide recovery responsibility |
| Publish before DB commit | can produce events for facts that never committed |
| Direct synchronous handler chain only | crash loses downstream work and couples process availability |
| External broker first | extra infrastructure before PostgreSQL baseline proves insufficient |
| Global total ordering | unnecessary/expensive; aggregate partition ordering is the relevant contract |

## Consequences

Consumers and projections must be idempotent; duplicate/out-of-order events are normal tested paths. Outbox payload is immutable; mutable lease/retry state is separate technical state. Event compatibility has public contracts at `contracts/events/`, registered fixture and consumer impact evidence. Unknown event version routes to safe DLQ/alert, not consumer crash/reinterpretation.

## Migration, rollout and rollback/forward-fix

Task 0.3 may create only approved `platform` delivery tables and tests. Schema/event changes require additive compatible form first; breaking meaning needs v2, migration/upcaster/retirement plan. On delivery failure, preserve event/evidence and forward-fix/replay; do not delete messages to clear a metric.

## Approval criteria

- [ ] Account Owner accepts at-least-once semantics and explicit duplicate handling.
- [ ] DATA-003/DATA-005 exact table/transaction proposal is approved.
- [ ] Contract registry names event schema, partition key, producer/consumer and compatibility test before an event is used.

