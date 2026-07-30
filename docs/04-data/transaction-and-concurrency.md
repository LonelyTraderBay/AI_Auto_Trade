# DATA-005 — Transaction, concurrency and idempotency policy

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 0.1.0 |
| Trạng thái | DRAFT — chờ Account Owner phê duyệt |
| Owner | Technical Operator |
| Approver | Account Owner |
| Ngày soạn | 2026-07-31 |
| Liên quan | FR-EXEC-001, FR-LED-001, FR-REC-001, FR-RSK-001, NFR-SAFE-001, NFR-AUD-001; ADR-0004, ADR-0005, ADR-0007, ADR-0011, ADR-0012 |
| Nguồn policy | [Master specification](../../AI_AUTO_TRADE_MASTER_SPEC.md), §6.3, §7.2–§7.8, §8.4–§8.9 |

## 1. Objective and non-negotiable rules

PostgreSQL transaction boundaries must ensure durable internal facts before external effect, detect contention and make recovery explicit. The system provides at-least-once delivery, not exactly-once. No distributed transaction, 2PC, in-memory mutex, UI state or “retry until success” is a capital-safety boundary.

External venue HTTP/WebSocket calls are always after commit. Unknown external outcome means `UNKNOWN`/reconciliation, never blind resubmission.

## 2. Authorized cross-context units of work

Only the following application workflows may atomically coordinate owner repositories across contexts. They do not grant direct SQL/ORM access to another context.

| Unit of Work | Atomic owner tables | Isolation / purpose |
|---|---|---|
| `TradingSubmissionUnitOfWork` | risk decisions/reservations, execution order/submission attempt, platform outbox | `SERIALIZABLE`; approve, reserve, queue exactly once before external submit |
| `FillLedgerUnitOfWork` | execution fill/order event, ledger journal/postings/projections, platform outbox | isolation selected/approved with ADR-0012; dedupe and book verified fill once |
| `ReconciliationResolutionUnitOfWork` | execution case/evidence, risk reservation, ledger adjustment through owner command, platform outbox | evidence-led resolution; no history overwrite |
| `OutboxPublishUnitOfWork` | platform delivery-state/attempt/DLQ only | short transaction/lease claim; not business transaction |
| `InboxConsumeUnitOfWork` | consumer-owned local state/outbox plus platform inbox marker | atomic idempotent local effect + receipt |

Any new cross-context transaction requires ADR/task amendment and a table-by-table ownership map.

## 3. Lock order and optimistic concurrency

The mandatory lock order is:

```text
risk limit/reservation -> execution order -> platform outbox
```

Mutable aggregates include a non-negative version (`aggregate_version` or delivery equivalent). Updates use compare-and-swap against the version read. Lock acquisition is bounded; deadlock/serialization errors follow retry policy below. Do not acquire locks in a reverse/conditional order and do not hold a transaction while waiting on network, user approval, UI or long compute.

Queue/outbox work claims due rows with `SELECT ... FOR UPDATE SKIP LOCKED` under an explicit lease/claim owner, expiry, fencing token and CAS version. Lease/fencing protects internal claim/write only; it does not prove that a venue did not receive an already-sent request.

## 4. Exact transaction maps

### 4.1 Pre-submit / durable queue

1. Begin `SERIALIZABLE` transaction.
2. Read/lock risk limit and reservation scope in fixed order; validate policy/input/market/reference/portfolio/lease snapshot.
3. Persist immutable RiskDecision and reservation if approved; persist execution order state `SUBMISSION_QUEUED`, first `SubmissionAttempt`, lifecycle event and immutable outbox event/delivery state.
4. Compare aggregate/snapshot versions and commit.
5. Only after a successful commit may execution leader claim and make one venue request.

Any failed commit or serialization retry performs full risk re-evaluation. A failed/unknown venue response cannot reopen the pre-submit transaction or cause a new submit attempt without reconciliation evidence.

### 4.2 Outbox publish

1. Start short transaction; claim one or bounded batch of due `PENDING` rows using `SKIP LOCKED`, lease/expiry/fencing and delivery-version CAS.
2. Commit claim.
3. Publish the immutable outbox payload outside the transaction.
4. Start short transaction; CAS state to `PUBLISHED`, schedule bounded retry, or append DLQ evidence and set terminal delivery state according to approved policy.

A crash after publish before final state yields duplicate delivery, which is expected; consumer dedupe handles it. Never modify outbox payload/history.

### 4.3 Inbox consume

1. Validate event schema/version and consumer compatibility before any side effect.
2. Begin the consumer owner transaction; insert an immutable inbox receipt guarded by unique `(consumer_id,event_id)` together with the local effect and any new outbox message.
3. If uniqueness reports existing receipt, treat it as duplicate and do not repeat effect.
4. Commit. Failed transaction leaves no success receipt/effect; retry remains safe.

The exact ordering of insert versus effect may vary only if the same atomic transaction and duplicate semantics remain proven; external effect cannot be put inside this transaction.

### 4.4 Verified fill -> ledger

1. Validate/deduplicate venue fill evidence and lock/update execution order in canonical sequence.
2. Persist immutable fill/order event; derive cumulative executed quantity from fills.
3. Build and validate balancing journal/postings under approved accounting policy; persist ledger and projection updates with an outbox event atomically.
4. Commit before any external follow-up. Duplicate evidence must hit a unique constraint/idempotency path before additional postings occur.

### 4.5 Reconciliation resolution

1. Persist immutable external/internal evidence and case transition.
2. If evidence proves an order state, apply allowed OMS transition. If not reconstructable, require explicit approved adjustment command.
3. Change reservation/projection only through their owner operations and append audit/outbox in the same allowed Unit of Work.
4. Never mutate original fill/journal/posting/order-event history.

## 5. Retry, timeout and failure matrix

| Failure class | Allowed retry | Required action |
|---|---|---|
| Serialization/deadlock before external call | bounded retry with jitter/backoff | re-run complete validation/risk and CAS checks |
| Constraint/idempotency duplicate | no blind retry of effect | load canonical prior result/evidence and return deterministic outcome |
| Lock timeout/lease lost | bounded retry only if no external action | relinquish/alert when bounded limit exceeded |
| Outbox publish failure | bounded delivery retry | preserve message; DLQ redacted evidence at policy threshold |
| Consumer handler failure | bounded retry | no inbox success receipt until atomic completion; DLQ/alert by policy |
| Venue request response missing | **never retry submit blindly** | order `UNKNOWN`, reconcile by client order ID/history/open orders/fills |
| DB unavailable | no in-memory safety fallback | fail closed; do not submit/approve new exposure |

Retry limit, backoff, jitter, claim TTL, batch size, reconciliation SLA and DLQ thresholds are controlled operational configuration. They must be schema-validated, versioned and owner-approved, not hard-coded here.

## 6. Idempotency scopes

| Scope | Key / enforcement |
|---|---|
| HTTP/control command | `(actor_id, route_scope, idempotency_key)`; same payload returns prior outcome, changed payload returns contract conflict |
| Venue order | `(venue_id, account_id, client_order_id)`; client ID generated once, never reused |
| Venue order metadata | `(venue_id, account_id, venue_order_id)` when non-null |
| Fill | venue fill ID or source event/fingerprint in venue/account |
| Order lifecycle | `(order_id, sequence)` |
| Event consumer | `(consumer_id, event_id)` |
| Journal posting | `(journal_entry_id, line_no)` plus source event dedupe in approved ledger write path |

Canonical request hash is audit/change-detection evidence; it is not a global uniqueness constraint.

## 7. Leader, lease and shutdown

Exactly one execution leader can claim submit work for a venue/account scope. Lease uses TTL, heartbeat and monotonically increasing fencing token. Lease loss stops new claims/submits; in-flight request with unknown outcome is recorded/reconciled. Startup runs state/config/venue/reconciliation/market-health sequence before enabling strategy. Shutdown stops new intent, drains under bounded timeout, flushes outbox/checkpoint and audits; it does not default to cancel all orders.

## 8. Verification and evidence

Before Phase 1, tests/evidence must prove: competing reservation contention, version conflict, fixed lock order, publisher duplicate after crash, consumer duplicate, fill dedupe/ledger single-booking, unknown submit no blind retry, lease-loss behavior, reconciliation correction and all allowed OMS transitions. Fault injection/restart evidence must record input hash/config/version and command exit results.

