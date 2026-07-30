# DOM-002 — Canonical OMS state machine

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 0.1.0 |
| Trạng thái | DRAFT — chờ Account Owner phê duyệt |
| Owner | Technical Operator |
| Approver | Account Owner |
| Ngày soạn | 2026-07-31 |
| Liên quan | FR-EXEC-001, FR-REC-001, NFR-AUD-001, NFR-SAFE-001; ADR-0004, ADR-0005, ADR-0007, ADR-0012 |
| Nguồn policy | [Master specification](../../AI_AUTO_TRADE_MASTER_SPEC.md), §5.4–§5.8, §7.2–§7.7, §8.6–§8.9 |

## 1. Authority và phạm vi

Đây là state contract canonical cho một `execution.Order`. Nó chỉ áp dụng cho MVP spot/order lifecycle; venue adapter phải map evidence venue vào contract này, không được dùng state vendor thay thế. Direct venue replace không thuộc MVP. DRAFT này không cho phép implementation/gate cho đến khi ADR-0005 và ADR-0012 được phê duyệt.

`EXTERNAL` là classification reconciliation của evidence/order chỉ tồn tại ở venue, không phải một state trong bảng dưới.

## 2. State và tính terminal

| State | Loại | Ý nghĩa |
|---|---|---|
| `CREATED` | non-terminal | OrderIntent đã canonicalize, chưa có verdict risk |
| `PENDING_MANUAL_APPROVAL` | non-terminal | Risk yêu cầu approval; không có submission queue |
| `RISK_APPROVED` | non-terminal | Risk/reservation hợp lệ, chưa queue durable submission |
| `SUBMISSION_QUEUED` | non-terminal | order, attempt đầu và outbox đã commit |
| `SUBMITTING` | non-terminal | execution leader đã claim; request evidence được persist trước venue call |
| `OPEN` | non-terminal | venue acknowledged order còn mở |
| `PARTIALLY_FILLED` | non-terminal | có fill nhưng quantity chưa đủ |
| `CANCEL_REQUESTED` | non-terminal | cancel request đã durable, chờ evidence |
| `UNKNOWN` | non-terminal/safe block | outcome submit/cancel không xác định; cấm blind retry |
| `RECONCILING` | non-terminal/safe block | đang thu thập/đánh giá evidence venue |
| `RISK_REJECTED`, `REJECTED`, `CANCELLED`, `EXPIRED`, `FILLED`, `LOST` | terminal | không được quay lại non-terminal |

## 3. Transition contract

| Từ | Guard / evidence | Sang | Persist/audit bắt buộc |
|---|---|---|---|
| `CREATED` | risk rejects | `RISK_REJECTED` | immutable reason + risk decision |
| `CREATED` | risk requires manual approval | `PENDING_MANUAL_APPROVAL` | pending approval, required role, expiry, hashes; không queue |
| `PENDING_MANUAL_APPROVAL` | valid authorized approval + fresh risk approve | `RISK_APPROVED` | approval/audit, new risk decision, reservation |
| `PENDING_MANUAL_APPROVAL` | approval expiry | `EXPIRED` | audit reason; không submission |
| `PENDING_MANUAL_APPROVAL` | fresh re-review rejects/fails | `RISK_REJECTED` | audit reason; không submission |
| `CREATED` | risk approves + reservation commits | `RISK_APPROVED` | risk decision + reservation |
| `RISK_APPROVED` | same DB transaction commits | `SUBMISSION_QUEUED` | order, first submission attempt, outbox |
| `SUBMISSION_QUEUED` | execution leader lease claims | `SUBMITTING` | claim/attempt request hash before external call |
| `SUBMITTING` | venue acknowledgement | `OPEN` | venue order ID, immutable event |
| `SUBMITTING` | fill arrives before ack | `PARTIALLY_FILLED` or `FILLED` | deduped fill + ledger booking first; late ack enriches only |
| `SUBMITTING` | business rejection | `REJECTED` | evidence/reason; reservation release policy |
| `SUBMITTING` | timeout, disconnect or unknown outcome | `UNKNOWN` | no retry; reconciliation trigger |
| `OPEN` | valid partial fill | `PARTIALLY_FILLED` | immutable fill + ledger event |
| `OPEN` / `PARTIALLY_FILLED` | cumulative fill reaches target | `FILLED` | final fill/ledger/projection |
| `OPEN` / `PARTIALLY_FILLED` | cancel intent accepted internally | `CANCEL_REQUESTED` | cancel attempt/audit |
| `CANCEL_REQUESTED` | venue confirms cancellation | `CANCELLED` | evidence + release remaining reservation |
| `OPEN` / `PARTIALLY_FILLED` / `CANCEL_REQUESTED` | venue expiry evidence | `EXPIRED` | evidence + release remaining reservation |
| `OPEN` / `PARTIALLY_FILLED` / `CANCEL_REQUESTED` | cancel timeout/outcome unknown | `UNKNOWN` | `pending_operation=CANCEL`; reconcile |
| `UNKNOWN` | reconciliation begins | `RECONCILING` | case/evidence correlation |
| `RECONCILING` | sufficient venue evidence | canonical proven state | preserve evidence + state event |
| `RECONCILING` | SLA expires without sufficient evidence | `LOST` | critical incident + manual handling |
| `CANCELLED` / `EXPIRED` | late proven fill | same terminal or `FILLED` | terminal correction; only full cumulative quantity becomes `FILLED` |
| `LOST` | late proven terminal result | proven terminal state | approved terminal correction; retain LOST incident history |
| `LOST` | late evidence says open/partial | `LOST` | open EXTERNAL case; block exposure; never reopen aggregate |

Any event not shown is invalid and must be rejected/audited rather than guessed.

## 4. Submission and cancellation protocol

1. Execution canonicalizes proposal, generates `OrderIntentId` and exactly one `ClientOrderId`.
2. Risk evaluate/reserve and `RISK_APPROVED -> SUBMISSION_QUEUED` persist in the pre-submit transaction.
3. A valid execution leader claims the queue; an attempt number, request hash and timestamp are durable before the venue request.
4. A venue request is made once for that attempt. Loss of response is not permission to submit again.
5. Recovery queries client order ID, history, open orders and recent fills under the venue capability contract. It records evidence, never fabricates an acknowledgement.
6. Cancellation is a distinct operation. Replace is modelled as terminal cancellation followed by a new OrderIntent/new ClientOrderId only after evidence/policy permit it.

## 5. Idempotency, ordering and deduplication

| Case | Required handling |
|---|---|
| Same internal command retried | route/actor idempotency contract returns original command outcome |
| Same `ClientOrderId` | unique by `(venue_id, account_id, client_order_id)`; reject payload mismatch |
| Same venue order ID | unique when non-null in venue/account scope |
| Same venue fill ID | one canonical fill only; fallback source fingerprint where venue lacks fill ID |
| Duplicate lifecycle event | unique `(order_id, sequence)` and transition guard prevent effect twice |
| Out-of-order ack/fill | fill is accepted only if dedupe/invariants pass; ack enriches metadata and does not undo booked fill |
| Terminal-to-non-terminal transition | forbidden; investigate through reconciliation/EXTERNAL procedure |

`canonical_request_hash` is audit evidence, not a global idempotency key; two legitimate orders can share a payload.

## 6. Manual approval contract

`REQUIRE_MANUAL_APPROVAL` persists a risk-owned pending approval with required role, reason, expiry, input snapshot hash and policy version. The approval record is immutable operations evidence; it does not mutate risk state by itself. A valid approval invokes a fresh risk evaluation. Changed/stale policy, snapshot, health, reference, exposure or expiry causes reject/expiry and requires a new intent.

## 7. Reconciliation and terminal correction

Reconciliation starts at startup, periodically, after private-stream gap/disconnect, for unknown state and on operator request. It compares balances, positions, open orders, recent fills, fee and order state. A mismatch opens a case with internal/external snapshots, window, tolerance, adapter version and actor.

No procedure may overwrite order/fill history to make it look like venue state. `APPROVED_ADJUSTMENT` is only for irrecoverable original evidence and requires approval; terminal corrections retain earlier terminal reason/incident/evidence history.

## 8. Required invariants and verification

- Exactly one execution leader claims a venue/account queue; lease loss stops new claims.
- The database transaction is committed before venue I/O. External I/O is never inside a long PostgreSQL transaction.
- `executed_quantity` is derived solely from immutable fills.
- Reservation release follows proven terminal state/fill/reconciliation, never timer-only silent cleanup.
- A `LOST` order blocks conflicting exposure until reconciliation resolves its external impact.
- Tests must enumerate all allowed/forbidden transitions, duplicate/out-of-order evidence, crash points before/after request, restart, stale approval and terminal correction.

## 9. Change control

Changing a state, transition, terminal meaning, submission retry or cancel/replace behavior is a breaking domain/data change. It requires ADR, updated event/schema compatibility plan, migration/forward-fix plan, property/contract tests and Account Owner approval.

