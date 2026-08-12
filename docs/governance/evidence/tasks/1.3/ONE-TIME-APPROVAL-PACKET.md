# Task 1.3 — Gói phê duyệt một lần

| Trường | Giá trị |
|---|---|
| Document ID | GOV-TASK-1.3-ONE-TIME-APPROVAL-001 |
| Phiên bản | 0.3.0 |
| Trạng thái | APPROVED WITH SAFETY BOUNDARIES; implementation BLOCKED bởi external evidence/branch/authority sync |
| Phạm vi | Phase 1, local simulator/no external venue |
| Parent | [Task 1.3 preflight](task-1.3-preflight.md) |
| Decision register | [Owner decision register](owner-decision-register.md) |
| Ngày lập | 2026-08-12 |

> v0.3.0 ghi nhận approval record [2026-08-12](approval-record-2026-08-12.md) lúc `2026-08-12T09:19:16Z`. Approval record cũ `2026-08-12T08:56:11Z` chỉ bao phủ packet v0.1.0/P-01 đến P-48; approval mới bao phủ P-01..P-68 và ghi riêng ba role actions theo Master §1.6.

> Đây là tài liệu duy nhất cần đọc để review toàn bộ scope Task 1.3. Các phụ lục chỉ giải thích chi tiết kỹ thuật. Việc phê duyệt gói này không tự chuyển artifact sang `APPROVED`, không tạo migration và không mở quyền code cho đến khi approval record hợp lệ được ghi nhận.

## 1. Cách phê duyệt một lần

Account Owner, Risk Approver và Security/Backup Owner đọc toàn bộ bảng dưới đây, sau đó trả lời bằng mẫu ở §6. Có thể phê duyệt toàn bộ bundle hoặc ghi rõ `REJECT`/`DEFERRED` cho từng ID. Không cần gửi lại từng file. Security/Backup Owner phải ký riêng các control liên quan access, logging/redaction, runbook, DB role/migration/backup và threat mapping (P-50..P-56, P-60); Technical Operator chỉ cung cấp evidence, không thay thế approver.

Một approval hợp lệ phải có actor, role, UTC timestamp, rationale, scope và expiry/supersession nếu có. Nếu Account Owner đồng thời giữ vai Risk Approver, phải ghi hai role riêng biệt trong approval record.

## 2. Bundle quyết định đề xuất

### 2.1. Scope và safety — đề xuất phê duyệt

| ID | Quyết định đề xuất | Tác động |
|---|---|---|
| P-01 | Task 1.3 chỉ chạy `LOCAL_ONLY` trong fake venue; không external venue/testnet/live | Không network, credential, exchange SDK hoặc venue secret |
| P-02 | Không có đường LLM/AI → risk write hoặc venue write | AI vẫn ngoài execution hot path |
| P-03 | Portfolio ledger runtime `DEFERRED` | Không tạo journal/posting/valuation runtime trong task này |
| P-04 | Không withdrawal, transfer, leverage, multi-account hoặc multi-venue | Giữ đúng Phase 1 scope |
| P-05 | Audit/order/event/fill history append-only; không hard-delete | Forward-fix/reconciliation thay cho overwrite |

### 2.2. Fake venue contract — đề xuất phê duyệt

| ID | Quyết định đề xuất | Giá trị đề xuất |
|---|---|---|
| P-06 | Protocol | `FVENUE-1` versioned internal protocol; request/response envelope có `protocol_version`, `scenario_id`, `scenario_revision`, `order_id`, `attempt_id`, `client_order_id`, `request_hash`, UTC timestamp |
| P-07 | Outcome enum | `ACCEPTED`, `REJECTED`, `PARTIAL_FILL`, `FILLED`, `CANCELLED`, `TIMEOUT`, `UNKNOWN` |
| P-08 | Scenario determinism | Scenario revision + seed `0` mặc định + injected UTC clock + ordered response sequence; không global random/wall clock |
| P-09 | Fault matrix | Immediate accept/reject, partial-fill, duplicate, out-of-order, timeout, ambiguous response, crash-after-apply, lease-loss, invalid request |
| P-10 | Conformance | Replay cùng scenario phải cho cùng outcome; không network, credential hoặc vendor SDK |

### 2.3. UNKNOWN, idempotency và identity — đề xuất phê duyệt

| ID | Quyết định đề xuất | Giá trị đề xuất |
|---|---|---|
| P-11 | UNKNOWN | Persist `UNKNOWN`/reconciliation; không blind retry; query/reconcile dùng cùng client identity và evidence |
| P-12 | Idempotency | Unique `(venue_id, account_id, client_order_id)`; request hash conflict fail-closed; replay trả kết quả đã ghi |
| P-13 | Duplicate/conflict | Không overwrite; append conflict evidence và mở reconciliation case |
| P-14 | Internal identity | UUIDv7 cho order/attempt/event/fill/reservation; external venue IDs opaque và nullable trước acknowledgement |
| P-15 | Client ID | Tạo một lần trong execution boundary; không reuse kể cả order terminal |

### 2.4. Fill và Decimal — đề xuất phê duyệt

| ID | Quyết định đề xuất | Giá trị đề xuất |
|---|---|---|
| P-16 | Fill fields | `fill_id`, `order_id`, `client_order_id`, nullable `venue_fill_id`, `price`, `quantity`, `fee_amount`, `fee_asset`, `liquidity_flag`, bốn UTC timestamps, `sequence`, `correlation_id` |
| P-17 | Numeric representation | Domain Decimal; API string; PostgreSQL `NUMERIC(38,18)` khi migration được mở |
| P-18 | Rounding | `ROUND_HALF_EVEN` cho các phép lượng hóa được policy cho phép; không dùng float |
| P-19 | Fill dedupe | Venue fill ID trong venue/account; nếu thiếu thì source event fingerprint; `sequence` chỉ ordering |
| P-20 | Missing fee | Không đoán; chỉ chấp nhận fee zero khi fixture/policy ghi rõ và có quality flag |

### 2.5. Risk profile local simulator — bắt buộc Risk Approver xác nhận

Các giá trị dưới đây là **candidate test-only profile**, không áp dụng live/testnet. Nếu không chấp nhận, ghi giá trị thay thế trong approval response.

| ID | Candidate value | Điều kiện an toàn |
|---|---|---|
| P-21 | Scope `LOCAL_SIMULATOR_TEST` | Chỉ synthetic account/venue/instrument; reject mọi scope khác |
| P-22 | Max order quantity `1000.000000000000000000` synthetic units | Inclusive cap; Decimal(38,18) |
| P-23 | Max order notional `1000.000000000000000000` synthetic quote units | Inclusive cap; không có giá trị tiền thật |
| P-24 | Rate limit `10` submit intents / `60` seconds / synthetic account | Clock do test inject; fail closed khi thiếu clock |
| P-25 | Market-data freshness `5` seconds | Stale/missing data => reject; không suy diễn giá |
| P-26 | Loss/drawdown | `NOT_APPLICABLE_BY_SCOPE`; mọi flow cần portfolio valuation bị reject và deferred sang accounting annex |
| P-27 | Reservation expiry `30` seconds | Expired reservation không được submit; cần intent mới |
| P-28 | Manual approval | Không mở UI/manual approval runtime trong Task 1.3; chỉ nhận RiskDecision đã signed/versioned |
| P-29 | Kill switch | Hierarchy `GLOBAL → VENUE → ACCOUNT → STRATEGY → INSTRUMENT`; default `FREEZE`; không tự động `FLATTEN` |
| P-30 | Policy lifecycle | Immutable version/hash/expiry; stale/expired policy fail closed |

> P-21 đến P-30 chỉ có hiệu lực nếu Risk Approver và Account Owner phê duyệt rõ. Nếu không, Task 1.3 vẫn BLOCKED ở risk boundary.

### 2.6. Transaction, concurrency và lease — đề xuất phê duyệt

| ID | Quyết định đề xuất | Giá trị đề xuất |
|---|---|---|
| P-31 | Pre-submit UoW | `SERIALIZABLE`; risk limit/reservation → execution order/attempt → platform outbox |
| P-32 | External call boundary | Commit thành công trước; không gọi fake/external venue trong DB transaction |
| P-33 | Fill/reconciliation UoW | `READ COMMITTED` + unique dedupe + CAS; append-only immutable facts |
| P-34 | Lease | TTL `30s`, heartbeat `10s`, monotonic fencing token; lease loss dừng claim/submit mới |
| P-35 | Retry | Chỉ bounded serialization/deadlock retry trước external action và rerun full risk; không retry UNKNOWN submit |
| P-36 | ADR-0012 | Amend câu `If approved`/`DRAFT` để đồng bộ DATA-TXN-001 v0.2.1 approved baseline |

### 2.7. Persistence boundary — đề xuất phê duyệt

| ID | Entity | Phạm vi đề xuất |
|---|---|---|
| P-37 | `execution.orders` | Order aggregate, state/version, client identity, intent/risk refs, terminal reason |
| P-38 | `execution.submission_attempts` | Attempt request hash, ordinal, outcome, timestamps, lease/fencing, UNKNOWN evidence |
| P-39 | `execution.order_events` | Append-only lifecycle event, partition/sequence, schema version, dedupe |
| P-40 | `execution.fills` | Immutable fill/fee evidence, dedupe identity, source fingerprint |
| P-41 | `execution.reconciliation_cases` | UNKNOWN/mismatch evidence và owner resolution command |
| P-42 | `risk.policies`/`decisions`/`reservations`/`limit_state` | Chỉ mở sau khi risk annex và dictionary/ERD được approve |
| P-43 | DDL/migration | Chưa tạo trong approval packet; chỉ mở bằng task card implementation riêng sau dictionary/ERD review |

### 2.8. Contract, evidence và task scope — đề xuất phê duyệt

| ID | Quyết định đề xuất | Giá trị đề xuất |
|---|---|---|
| P-44 | Existing command/event | Cho phép chuẩn bị implementation cho `submit-order.v1` và `order-event.v1` sau registry review |
| P-45 | Fake venue contract | Tạo `FVENUE-1` draft ở evidence; chỉ chuyển runtime contract sau approval |
| P-46 | Required evidence | Contract validation, unit/integration/concurrency/fault/replay/negative/security evidence |
| P-47 | Database evidence | PostgreSQL thật với `DATABASE_URL`; không chấp nhận skip cho migration/concurrency gate |
| P-48 | Task card | Tạo card implementation `1.3` riêng, status ban đầu `BLOCKED`, chỉ chuyển `READY` sau khi mọi prerequisite đạt |

### 2.9. Enterprise cross-cutting controls — bổ sung bắt buộc

| ID | Quyết định đề xuất | Giá trị/điều kiện |
|---|---|---|
| P-49 | Audit/correlation | Mọi command/event/attempt có actor, role, trace/correlation/causation ID và immutable audit |
| P-50 | Access control | Deny-by-default; runtime role không DDL/delete; không direct venue/AI write; cross-scope denial test |
| P-51 | Logging/redaction | Structured JSON-lines; UTC/event/context/correlation fields; secret/PII/raw payload deny and scan |
| P-52 | Metrics/alerts | UNKNOWN, duplicate, lease loss, reconciliation age, outbox backlog, DB error and safe-state alert signals |
| P-53 | Runbooks | Unknown order, reconciliation mismatch, DB unavailable, trading-node restart; drill evidence required |
| P-54 | DB roles | `db_migrator` tách runtime; runtime least privilege; grant denial evidence; no history delete |
| P-55 | Migration safety | Schema snapshot, lock/timeout plan, expand/forward-fix, compatibility and rollback evidence |
| P-56 | Backup/restore | Task 1.3 phải có design/checklist; restore drill bắt buộc trước canary, không tự resume strategy |
| P-57 | Contract compatibility | Schema/fixture/registry version, additive/breaking rule and upcaster plan |
| P-58 | Architecture boundary | Import-linter/Pyright proves domain không import framework/DB/vendor/venue SDK |
| P-59 | Fault/replay evidence | Duplicate, partial, out-of-order, timeout, crash, lease loss, DB failure with pinned clock/seed/checksum |
| P-60 | Security/threat mapping | Map T-003/T-004/T-006/T-007/T-011/T-018 to controls and negative tests |
| P-61 | Rollback/forward-fix | Revert code safely; never rewrite financial/audit facts; schema changes use approved forward-fix |
| P-62 | Deferred controls | Retention/OPS numeric SLO/performance/external venue/AI runtime deferred to owning phase; no silent assumption |
| P-63 | Risk fixture | Approved [risk-profile.local-simulator.v1.approved.json](risk-profile.local-simulator.v1.approved.json); SHA-256/hash/effective/expiry are pinned |
| P-64 | Scenario contract | Review [fake-venue-scenario.v1.schema.json](fake-venue-scenario.v1.schema.json) and valid fixture; no runtime registry approval yet |
| P-65 | Column dictionary | Review [execution-risk-dictionary-addendum.md](execution-risk-dictionary-addendum.md) before any DDL |
| P-66 | Traceability | Review [task-1.3-traceability-matrix.md](task-1.3-traceability-matrix.md); no unlinked code accepted |
| P-67 | Recovery drills | Review [task-1.3-runbook-drill-plan.md](task-1.3-runbook-drill-plan.md); failed safety drill blocks review |
| P-68 | Task-directory hygiene | Move/record already-DONE `0.0.7` card consistently in `tasks/completed/` before creating canonical Task 1.3 active card; no duplicate active authority |

## 3. Các artifact được review cùng bundle

1. [Risk/Fill/concurrency closure](risk-fill-concurrency-closure.md)
2. [Data/persistence closure](data-persistence-closure.md)
3. [Fake venue closure](fake-venue-closure.md)
4. [ADR-0012 amendment proposal](adr-0012-amendment-proposal.md)
5. [Implementation task-card proposal](implementation-task-card-proposal.yaml)
6. [Owner decision register](owner-decision-register.md)
7. [Enterprise control closure matrix](enterprise-control-closure-matrix.md)
8. [Approved risk fixture](risk-profile.local-simulator.v1.approved.json) (candidate retained as draft evidence)
9. [Fake venue schema/fixture](fake-venue-scenario.v1.schema.json)
10. [Execution/risk dictionary addendum](execution-risk-dictionary-addendum.md)
11. [Traceability matrix](task-1.3-traceability-matrix.md)
12. [Runbook drill plan](task-1.3-runbook-drill-plan.md)
13. [One-time approval record](approval-record-2026-08-12.md)

## 4. Những gì bundle này không phê duyệt

- External venue, testnet, live trading, credential hoặc network.
- Portfolio ledger runtime, valuation, journal/posting hoặc accounting annex.
- Withdrawal, transfer, leverage, derivatives, multi-account, multi-venue.
- LLM/AI execution path hoặc OpenAI runtime.
- Migration thực tế trước khi dictionary/ERD/task card được approve.
- Bất kỳ artifact nào đang `DRAFT`/`IN_REVIEW` mà chưa có approval record.

## 5. Điều kiện chuyển sang READY sau approval

1. Account Owner ký P-01 đến P-20, P-31 đến P-68 và xác nhận các mục deferred trong phạm vi owner.
2. Risk Approver ký P-21 đến P-30 và mọi decision ảnh hưởng risk.
3. Security/Backup Owner ký P-50 đến P-56 và P-60 (hoặc ghi rõ phần nào `DEFERRED` ngoài scope), gồm access, redaction, runbook, DB role/migration/backup và threat mapping.
4. ADR-0012 được amend; registry, dictionary, ERD, Fill, logging/access/threat mapping được đồng bộ hoặc ghi rõ deferred.
5. PostgreSQL test environment chạy được, không skip integration gate.
6. Enterprise evidence manifest trong [control closure matrix](enterprise-control-closure-matrix.md) được chấp nhận.
7. `tasks/active/` được reconcile, không còn card `DONE` trong thư mục active và không có duplicate authority.
8. Task card implementation được tạo trong `tasks/active/` với status `READY`, allowlist/forbidden globs, expiry, commands và evidence path.
9. Chỉ sau bước 1–8 mới được chuyển sang `IN_PROGRESS` và viết code.

## 6. Mẫu xác nhận một lần

```text
ACCOUNT OWNER — ONE-TIME REVIEW
Identity:
Role: Account Owner
Decision: APPROVE / APPROVE WITH EXCEPTIONS / REJECT
Approved IDs:
Exceptions or replacements:
Deferred IDs and target phase/task:
Ledger: DEFERRED / APPROVE (chỉ nếu accounting annex đã đủ)
External venue: DEFERRED / REJECT
Rationale:
UTC timestamp:
Expiry/supersession:

RISK APPROVER — ONE-TIME REVIEW
Identity:
Role: Risk Approver
Decision: APPROVE / APPROVE WITH EXCEPTIONS / REJECT
Approved IDs: P-21..P-30 và các decision risk liên quan
Risk value replacements:
Rationale:
UTC timestamp:
Expiry/supersession:

SECURITY/BACKUP OWNER — ONE-TIME REVIEW (P-50..P-56, P-60)
Identity:
Role: Security/Backup Owner
Decision: APPROVE / APPROVE WITH EXCEPTIONS / DEFERRED / REJECT
Approved IDs:
Exceptions or replacements:
Rationale:
UTC timestamp:
Expiry/supersession:
```

## 7. Trạng thái hiện tại

Approval record mới đã ghi nhận Account Owner, Risk Approver và Security/Backup Owner role actions cho toàn bộ P-01..P-68. Task 1.3 implementation vẫn `BLOCKED` cho đến khi authority sync hoàn tất, PostgreSQL `DATABASE_URL` chạy no-skip và branch `task/1.3-*` được sử dụng.
