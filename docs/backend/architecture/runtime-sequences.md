# Runtime Sequences — luồng bắt buộc và failure semantics

| Thuộc tính | Giá trị |
|---|---|
| Document ID | ARC-SEQ-001 |
| Phiên bản | 0.3.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §5, §6, §7.2–§7.7, §8, §10.6 và §11 |
| Related requirements | FR-MKT-001, FR-EXEC-001, FR-LED-001, FR-REC-001, FR-RSK-001, FR-OPS-001, FR-AI-001; NFR-DET-001, NFR-AUD-001, NFR-SAFE-001, NFR-AI-001 |
| Related ADR | ADR-0004, ADR-0005, ADR-0007, ADR-0011, ADR-0012, ADR-0016 |

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
    participant CMD as operations.commands (PostgreSQL)
    participant Runtime as operations/trading runtime handler
    participant Rec as reconciliation/health check

    Actor->>API: command + Idempotency-Key + reason + correlation ID
    API->>Auth: authenticate, authorize, validate route scope
    alt action requires re-auth
        API->>Auth: re-authenticate actor
    end
    API->>Audit: append command intent/before hash
    API->>CMD: persist durable command record ACCEPTED
    API-->>Actor: 202 ACCEPTED + command ID/location
    Runtime->>CMD: poll/claim command record (owner application handler)
    Runtime->>Runtime: apply safe-state policy / execute transition
    opt release kill switch
        Runtime->>Rec: require clean reconciliation + health
        Rec-->>Runtime: evidence result
    end
    Runtime->>CMD: append command_events transition (terminal/progress state)
    Runtime->>Audit: append outcome/after hash/actor role
    API->>CMD: read command status projection
    API-->>Actor: command status resource
~~~

`operations.commands` (PostgreSQL) là mutable source of truth duy nhất cho control command (master §7.6): Control API chỉ tạo durable command record; owner application handler poll/claim và thực thi transition, transition được append vào `command_events`. Không có direct API→Runtime network call — trading node không expose public HTTP management surface (master §4.7). Same actor/route/idempotency key with a different canonical payload returns conflict; dangerous action cannot rely on UI confirmation alone.

## 7. AI provider connection enrollment, validation and activation (Phase 6 only)

~~~mermaid
sequenceDiagram
    participant Owner as Account Owner
    participant API as Control API
    participant Policy as RBAC/catalog/egress policy
    participant Meta as operations metadata/audit
    participant Ingress as isolated secret_ingress
    participant Vault as approved secret provider
    participant Worker as ai_worker validation identity
    participant Provider as approved provider adapter

    Owner->>API: create connection metadata + provider/model/policy profile + reason
    API->>Policy: authenticate, owner-scope authorize, re-auth, validate ACTIVE catalog/profile compatibility
    API->>Meta: persist PENDING_SECRET connection; no raw key
    API-->>Owner: safe connection ID + isolated one-time enrollment session
    Owner->>Ingress: submit provider key; no Idempotency-Key/body hash
    Ingress->>Vault: direct write-only candidate enrollment
    Vault-->>Ingress: opaque binding receipt only
    Ingress->>Meta: record PENDING_VALIDATION safe lifecycle event; no body/fingerprint
    Owner->>API: validation/activation request + reason + re-auth
    API->>Policy: require Account Owner + Security/Backup Owner role records
    API->>Worker: scoped validation job
    Worker->>Policy: verify scope/catalog/egress/bounded probe budget
    Worker->>Vault: resolve one binding just-in-time
    Worker->>Provider: minimal synthetic/sanitized capability probe
    Provider-->>Worker: normalized capability result; no raw vendor payload
    alt valid and policy-approved
        Worker->>Meta: mark ACTIVE with revision/audit metadata
    else invalid, uncertain or policy denied
        Worker->>Meta: mark VALIDATION_FAILED or SUSPENDED; no activation
    end
    API-->>Owner: safe status only; never raw key, secret ref or provider response
~~~

**Guards:** Provider/model/endpoint/policy profile cannot be arbitrary. Enrollment body never enters Control API middleware, command, outbox, event, audit, proxy/WAF/APM or trace persistence; response is no-store and lost response is resolved by safe status query, not retry. No role can read back the provider key. The secret provider is external to PostgreSQL and a connection only stores internal opaque binding metadata.

## 8. AI inference, budget and controlled failure (Phase 6 only)

~~~mermaid
sequenceDiagram
    participant Worker as ai_worker
    participant Policy as scope/catalog/egress/budget policy
    participant Vault as approved secret provider
    participant Adapter as adapters/llm/<provider>
    participant Provider as approved AI provider
    participant Memory as ai_memory proposal/memory store

    Worker->>Policy: verify active binding state/revision + owner scope + model/profile + egress + quota reservation
    alt policy fails
        Policy-->>Worker: deny without provider call
    else policy passes
        Worker->>Vault: resolve short owner/connection/revision/job binding lease just-in-time
        Worker->>Policy: recheck revision immediately before egress
        Worker->>Adapter: canonical sanitized request + structured schema; tools disabled
        Adapter->>Provider: bounded request through approved host/SNI/TLS/DNS/redirect policy
        alt structured valid response
            Provider-->>Adapter: provider response
            Adapter-->>Worker: canonical result + safe usage/status metadata
            Worker->>Memory: validate schema/provenance then persist proposal/memory + usage reconciliation
        else timeout, revoked key, budget/circuit/rate limit, invalid or unknown outcome
            Provider-->>Adapter: normalized redacted failure
            Adapter-->>Worker: safe error metadata
            Worker->>Policy: reconcile reservation / open circuit or disable AI capability as policy requires
            Note over Worker,Memory: Do not retry/fallback blindly; trading is unchanged.
        end
    end
~~~

**Guards:** no execution/risk/config/deployment/database tool is exposed to the model. BYOK v1 automatic fallback is disabled. Suspend/revoke invalidates new binding leases; an in-flight result is discarded if revocation wins.

## 9. Event delivery and projection rebuild

Outbox/inbox delivery is at-least-once. Consumer deduplicates via event identity/consumer record and treats unsupported event version as DLQ/alert per compatibility policy. Projection rebuild consumes canonical append-only event/ledger source rather than mutating history to recover a display.

## 10. Sequence invariants to test

- Persist attempt/client_order_id/request hash before external submit.
- No DB transaction remains open while HTTP/WebSocket venue call is in progress.
- Unknown outcome never schedules automatic resubmit of the same order.
- Duplicate fill/event has no second ledger/exposure effect.
- Terminal OMS state never returns to non-terminal state.
- Lost lease stops new claim/submission.
- Manual approval runs fresh risk; kill-switch release requires re-auth/reconciliation/health.
- UI/AI/strategy has no message path that directly reaches venue execution.
- AI key enrollment is isolated/write-only/no-store and no raw field or key hash/fingerprint reaches command/event/outbox/audit/log/proxy/WAF/APM/trace/fixture/DB.
- AI initial/rotation lifecycle preserves old active binding until candidate validation/atomic cutover; dual-role validation/activation and emergency suspension/revocation are auditable.
- AI connection validation and inference require active owner-scoped catalog/policy-profile/budget/egress checks before secret resolution/provider call.
- Provider timeout/unknown outcome cannot cause a blind retry, silent cross-provider fallback or trading state change; DNS/redirect/private-route bypass is denied.

## 11. Cancel order sequence

~~~mermaid
sequenceDiagram
    participant Actor as operator/strategy
    participant Exec as execution application
    participant DB as PostgreSQL
    participant Venue as venue adapter / venue
    participant Ledger as portfolio_ledger

    Actor->>Exec: CancelIntent(order)
    Exec->>Exec: validate order đang OPEN hoặc PARTIALLY_FILLED
    alt order không ở trạng thái cancel được
        Exec->>DB: reject cancel + audit reason; state không đổi
    else order hợp lệ
        Exec->>DB: persist CANCEL_REQUESTED + cancel attempt trước HTTP
        Exec->>Venue: exactly one cancel call
        alt venue confirms cancel
            Venue-->>Exec: cancel confirmed
            Exec->>DB: persist CANCELLED; release remaining reservation
        else venue reports already filled
            Venue-->>Exec: fill evidence
            Exec->>Ledger: process fills first (immutable fill/fee booking)
            Exec->>DB: persist FILLED; cancel outcome ghi nhận là vô hiệu
        else timeout or disconnect
            Exec->>DB: persist UNKNOWN với pending_operation=CANCEL; không blind retry
            Note over Exec,DB: reconcile theo §4
        end
    end
~~~

**Guards:** cancel attempt/pending_operation được persist trước external call, giống submit path ở §3; unknown cancel outcome đi qua reconciliation (§4), không tự retry.

**DRAFT rule cần owner approval:** CancelIntent KHÔNG qua full risk evaluation vì là exposure-reducing action; nó vẫn phải qua authorization/audit path và bị chặn khi kill switch scope cấm cancel-path hoặc khi reconciliation đang block order đó. Quy tắc này chưa có trong master — cần amendment master §8.6 hoặc ADR. (DRAFT — đề xuất, cần Account Owner phê duyệt.)

## 12. Các flow chưa có diagram (chuẩn prose)

Các flow sau là deliberate prose-only ở phase này; diagram sẽ được bổ sung khi flow được implement lần đầu:

| Flow | Prose authority |
|---|---|
| Kill-switch activation / scope cascade | master §8.10 + runbook kill-switch.md |
| Manual-approval continuation | master §5.4 / §8.4 |
| Market-data gap recovery | master §9.4 + runbook stream-gap.md |
| Lease loss mid-flight | master §6.3.11 / §8.9 |
| Outbox relay failure | master §7.2–§7.3 |
| Config/deploy rollout-rollback | master §6.6 |

## 13. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | Tạo normative runtime sequence baseline cho core safety flows. | Technical Operator | Pending |
| 0.2.0 | 2026-07-31 | Thêm sequence BYOK enrollment/validation và inference failure isolation cho Phase 6. | Technical Operator | Pending |
| 0.3.0 | 2026-07-31 | Chèn durable command store `operations.commands` vào §6 (không direct API→Runtime call, master §7.6/§4.7); thêm §11 Cancel order sequence (kèm DRAFT risk-gate rule chờ owner approval); thêm §12 danh mục flow prose-only. | Technical Operator | Pending |
