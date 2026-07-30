# Runtime Sequences — luồng bắt buộc và failure semantics

| Thuộc tính | Giá trị |
|---|---|
| Document ID | ARC-SEQ-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §5, §6, §7.2–§7.7, §8 và §11 |
| Related requirements | FR-MKT-001, FR-EXEC-001, FR-LED-001, FR-REC-001, FR-RSK-001, FR-OPS-001; NFR-DET-001, NFR-AUD-001, NFR-SAFE-001 |
| Related ADR | ADR-0004, ADR-0005, ADR-0007, ADR-0011, ADR-0012 |

> Diagram thể hiện normative flow ở mức architecture. Message/event field phải do schema versioned xác định. Không có sequence nào cho phép giữ DB transaction mở trong external call, blind retry hoặc bypass risk.

## 1. Quy ước chung

- Mọi event public mang schema_version, correlation_id, causation_id, trace_id và occurred_at theo master.
- Decimal/financial value không dùng float; timestamp UTC.
- Atomic transaction chỉ bao gồm persistent internal state được nêu; network call nằm ngoài transaction.
- Unknown external outcome luôn là reconciliation path, không là retry path.
- Actor/controller action dangerous đi qua authorization, audit và re-auth khi policy yêu cầu.

## 2. Market event đến strategy proposal

~~~mermaid
sequenceDiagram
    participant Feed as Market data source
    participant Adapter as Market adapter
    participant MD as market_data application
    participant Ref as reference snapshot
    participant Strat as strategy runtime
    participant Exec as execution application

    Feed->>Adapter: raw market/reference message
    Adapter->>MD: normalized candidate + received_at
    MD->>MD: validate schema, ordering, quality, timestamps
    MD->>Ref: resolve effective instrument/reference version
    alt data/reference is valid and fresh
        MD->>Strat: canonical market event + state/context
        Strat->>Strat: deterministic evaluation with injected Clock/RandomSource
        Strat->>Exec: ProposeOrderIntent action or NoAction
    else invalid, gap, stale or unsupported
        MD->>MD: persist quality evidence / alert according to policy
        MD-->>Strat: no unsafe input
    end
~~~

**Guards:** strategy has no network/DB/file/env access; it cannot create ClientOrderId. Reference/quality freshness is re-checked by risk, not trusted solely because a strategy saw an event.

## 3. Intent, risk, durable submission và venue outcome

~~~mermaid
sequenceDiagram
    participant Strat as strategy
    participant Exec as execution application
    participant Risk as risk application
    participant DB as PostgreSQL
    participant Leader as execution leader
    participant Venue as venue adapter / venue
    participant Ledger as portfolio_ledger

    Strat->>Exec: ProposedOrderIntent
    Exec->>Exec: validate/canonicalize; assign OrderIntentId + one ClientOrderId
    Exec->>Risk: immutable intent + policy/snapshot/reservation/runtime health
    alt Risk REJECT
        Risk-->>Exec: RiskDecision(REJECT)
        Exec->>DB: persist RISK_REJECTED + audit reason
    else Risk REQUIRE_MANUAL_APPROVAL
        Risk-->>Exec: RiskDecision(REQUIRE_MANUAL_APPROVAL)
        Exec->>DB: persist PENDING_MANUAL_APPROVAL; no submission queue
    else Risk APPROVE
        Risk-->>Exec: RiskDecision(APPROVE) + reservation
        Exec->>DB: one transaction: decision, reservation, order RISK_APPROVED -> SUBMISSION_QUEUED, SubmissionAttempt, outbox
        Leader->>DB: atomically claim queue only with valid lease/fencing
        Leader->>DB: persist attempt/request hash/client_order_id before network call
        Leader->>Venue: exactly one submit attempt
        alt venue acknowledgment
            Venue-->>Leader: accepted + venue order ID
            Leader->>DB: persist OPEN / immutable event
        else business rejection
            Venue-->>Leader: rejected
            Leader->>DB: persist REJECTED; release reservation per policy
        else fill arrives before acknowledgment
            Venue-->>Leader: fill evidence
            Leader->>Ledger: immutable fill/fee booking
            Ledger->>DB: balanced journal/postings + projection
            Leader->>DB: PARTIALLY_FILLED or FILLED; late ack only enriches metadata
        else timeout or disconnect
            Leader->>DB: persist UNKNOWN; do not resubmit
        end
    end
~~~

**Manual approval continuation:** valid approver action triggers fresh full risk evaluation. If expiry, policy/input/snapshot state is stale or new risk rejects, intent becomes EXPIRED or RISK_REJECTED and no submission is queued.

## 4. Unknown submit outcome và reconciliation

~~~mermaid
sequenceDiagram
    participant Node as trading node
    participant DB as PostgreSQL
    participant Venue as venue adapter / venue
    participant Rec as reconciliation
    participant Ops as control/operations

    Node->>DB: order state UNKNOWN; audit correlation/evidence
    Node->>Rec: request recovery workflow
    Rec->>Venue: query by ClientOrderId if supported
    Rec->>Venue: query history, open orders and recent fills
    alt evidence resolves canonical order
        Venue-->>Rec: order/fill/cancel/reject evidence
        Rec->>DB: persist evidence; derive canonical state and fill/ledger effects
        Rec-->>Ops: reconciliation case RESOLVED or clean result
    else evidence remains insufficient before SLA
        Rec->>DB: state RECONCILING; block conflicting intent/exposure scope
        Rec-->>Ops: alert with case/evidence
    else SLA elapsed
        Rec->>DB: state LOST + immutable incident/evidence history
        Rec-->>Ops: critical alert; manual handling required
    end
~~~

Late evidence after terminal state only follows terminal-correction/EXTERNAL procedure defined by the OMS policy. An aggregate never reopens to a non-terminal state.

## 5. Startup, lease và shutdown

~~~mermaid
sequenceDiagram
    participant Node as trading node
    participant DB as PostgreSQL
    participant Venue as venue adapter
    participant Ops as operations

    Node->>Ops: BOOTING
    Node->>DB: acquire execution lease + fencing token
    alt lease acquired
        Node->>Ops: CONFIG_VALIDATED
        Node->>DB: load local state, checkpoints, pending work
        Node->>Venue: connect / capability and account checks allowed by mode
        Node->>Ops: RECONCILING
        Node->>Venue: obtain external reconciliation evidence
        Node->>Ops: MARKET_HEALTH_CHECK
        alt reconciliation and health clean
            Node->>Ops: READY -> STRATEGIES_ENABLED
        else mismatch or unsafe condition
            Node->>Ops: BLOCKED / safe state; do not enable strategy
        end
    else lease not acquired
        Node->>Ops: remain non-executing; alert/observe only
    end
~~~

On lost lease, the node stops claiming/sending new orders. In-flight request with unknown outcome is marked/reconciled. Shutdown blocks new intent, drains within configured timeout, flushes outbox/checkpoint, persists audit and does not cancel all open orders unless a separate policy requires it.

## 6. Dangerous control command

~~~mermaid
sequenceDiagram
    participant Actor as authenticated actor
    participant API as Control API
    participant Auth as authorization policy
    participant Audit as audit store
    participant Runtime as operations/trading runtime
    participant Rec as reconciliation/health check

    Actor->>API: command + Idempotency-Key + reason + correlation ID
    API->>Auth: authenticate, authorize, validate route scope
    alt action requires re-auth
        API->>Auth: re-authenticate actor
    end
    API->>Audit: append command intent/before hash
    API-->>Actor: 202 ACCEPTED + command ID/location
    API->>Runtime: authorized asynchronous command
    Runtime->>Runtime: apply safe-state policy
    opt release kill switch
        Runtime->>Rec: require clean reconciliation + health
        Rec-->>Runtime: evidence result
    end
    Runtime->>Audit: append outcome/after hash/actor role
    API-->>Actor: command status resource
~~~

Same actor/route/idempotency key with a different canonical payload returns conflict; dangerous action cannot rely on UI confirmation alone.

## 7. Event delivery and projection rebuild

Outbox/inbox delivery is at-least-once. Consumer deduplicates via event identity/consumer record and treats unsupported event version as DLQ/alert per compatibility policy. Projection rebuild consumes canonical append-only event/ledger source rather than mutating history to recover a display.

## 8. Sequence invariants to test

- Persist attempt/client_order_id/request hash before external submit.
- No DB transaction remains open while HTTP/WebSocket venue call is in progress.
- Unknown outcome never schedules automatic resubmit of the same order.
- Duplicate fill/event has no second ledger/exposure effect.
- Terminal OMS state never returns to non-terminal state.
- Lost lease stops new claim/submission.
- Manual approval runs fresh risk; kill-switch release requires re-auth/reconciliation/health.
- UI/AI/strategy has no message path that directly reaches venue execution.

## 9. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | Tạo normative runtime sequence baseline cho core safety flows. | Technical Operator | Pending |
