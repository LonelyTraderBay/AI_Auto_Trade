# DOM-001 — Canonical domain model

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 0.2.0 |
| Trạng thái | DRAFT — chờ Account Owner phê duyệt |
| Owner | Technical Operator |
| Approver | Account Owner |
| Ngày soạn | 2026-07-31 |
| Rà soát tiếp theo | Trước khi Task 0.4 bắt đầu |
| Liên quan | FR-MKT-001, FR-STR-001, FR-EXEC-001, FR-RSK-001, FR-LED-001, FR-REC-001, FR-AI-001, NFR-DET-001, NFR-AUD-001, NFR-SAFE-001, NFR-AI-001; ADR-0002, ADR-0003, ADR-0005, ADR-0007, ADR-0011, ADR-0012, ADR-0016 |
| Nguồn policy | [Master specification](../../../AI_AUTO_TRADE_MASTER_SPEC.md), §4, §5, §7, §8, §10.6 |

## 1. Mục đích và phạm vi

Tài liệu này xác định ngôn ngữ domain và quyền sở hữu khái niệm chuẩn cho MVP. Nó không tạo database schema, API hay implementation. Mọi public contract phải dùng tên/ý nghĩa ở đây; chi tiết wire/DDL thuộc `contracts/` và `docs/backend/data/` sau khi được phê duyệt.

Phạm vi là một venue crypto spot, một account và các instrument do Account Owner duyệt sau này. Không suy diễn venue, asset, currency, account hoặc giới hạn giao dịch từ tài liệu này.

## 2. Ranh giới context và quyền sở hữu

| Context | Sở hữu canonical fact | Nhận vào | Phát ra | Không sở hữu |
|---|---|---|---|---|
| `reference` | venue, account reference, asset, instrument, rule/capability version | source snapshot đã kiểm chứng | reference/rule change | order hoặc risk verdict |
| `market_data` | normalized market event, feed health, quality issue | raw feed | market-data event/quality signal | strategy/risk decision |
| `strategy` | definition/version/instance state, signal, `ProposedOrderIntent` | market event, checkpoint | proposal | client order ID, network/DB access |
| `risk` | policy version, decision, reservation, pending approval, limit state | canonical `OrderIntent`, snapshots | `RiskDecision`, reservation/rejection | submit venue order |
| `execution` | OMS order, attempts, venue evidence, fills, reconciliation case | approved intent, venue/private event | order/fill lifecycle event | risk policy, accounting history |
| `portfolio_ledger` | journal/posting immutable và projection dẫn xuất | verified fill/fee/adjustment command | journal/projection event | overwrite venue/execution history |
| `operations` | command lifecycle, approval/audit, deployment/lease/kill switch, AI provider connection metadata | authorized command / owner-scoped connection lifecycle request | command/audit event | raw AI key or trading business decision |
| `platform` | outbox/inbox/DLQ/idempotency delivery metadata | committed event/command result | delivery outcome | domain/risk policy |
| `research` | dataset/backtest/evaluation | immutable catalog snapshot | report/candidate | live write model |
| `ai_memory` | proposal/memory/inference provenance Phase 6 | sanitized projection + active connection policy | proposal only | raw AI key, execution credential or write path |

Cross-context liên kết chỉ dùng immutable canonical ID, event hoặc read projection. Không có context nào đọc/ghi trực tiếp private ORM model/table của context khác.

## 3. Kiểu giá trị và quy ước bất biến

| Chủ đề | Quy tắc chuẩn |
|---|---|
| Internal ID | UUIDv7, lưu PostgreSQL `UUID`; không dùng venue ID làm khóa nội bộ |
| Money/price/quantity/fee/PnL | `Decimal` trong domain; `NUMERIC(38,18)` trong database; API/wire là string; cấm `float` |
| Timestamp | UTC, timezone-aware, ISO-8601 có `Z`; domain nhận `Clock` inject |
| Random | `RandomSource` inject; seed được lưu khi ảnh hưởng result replay/backtest |
| Immutability | public event, value object, RiskDecision, fill và journal/posting là immutable |
| Contract version | mọi public command/event/config có `schema_version` |
| Canonical hash | UTF-8 canonical JSON v1, key sort lexicographic, không whitespace/NaN/Infinity, SHA-256 |

Các timestamp chuẩn là `occurred_at`, `received_at`, `processed_at`, `recorded_at`, `effective_at`, `created_at`, `updated_at`. Không dùng `event_time` hay `received_time` cho cùng nghĩa khác tên.

## 4. Ubiquitous language

| Thuật ngữ | Nghĩa chuẩn | Không được hiểu là |
|---|---|---|
| Venue | nhà cung cấp/sàn có capability profile đã version | account hoặc environment |
| Account | phạm vi balance/order do venue quản lý | tenant chung hoặc credential raw |
| Instrument | cặp/tài sản giao dịch canonical cùng rule version theo thời gian | symbol string không version |
| Proposal | output chưa được phép giao dịch của strategy | order đã submit |
| `ProposedOrderIntent` | đề xuất strategy, chưa có `ClientOrderId` | aggregate execution |
| `OrderIntent` | yêu cầu chuẩn hóa của execution, có đúng một `ClientOrderId` | venue order/acknowledgement |
| Order | aggregate OMS nội bộ có lifecycle canonical | request HTTP đơn lẻ |
| Submission attempt | một lần gửi evidence-bound ra venue | quyền retry mù |
| Fill | bằng chứng khớp lệnh immutable, deduplicate được | projection balance |
| Reservation | phần balance/exposure được khóa logic trước submit | fill/exposure đã xảy ra |
| Risk decision | verdict synchronous, versioned và có expiry | approval UI có thể bypass |
| Reconciliation case | sai khác cần evidence/điều tra | thao tác overwrite local history |
| Ledger | accounting truth nội bộ append-only | số dư venue tức thời |
| Projection | state dẫn xuất có thể rebuild | source of truth tài chính |
| EXTERNAL | classification order/evidence chỉ thấy ở venue | một OMS state |
| AI provider connection | owner-scoped metadata chọn provider/model/policy/binding revision | raw API key, generic venue credential hoặc permission execution |
| Credential binding | opaque reference giữa connection và secret provider | giá trị key hoặc secret reference public |
| AI proposal | structured output đã validation/provenance, vẫn chưa là strategy/risk/order approval | lệnh, risk decision hoặc action có quyền runtime |

## 5. Aggregate và identity chuẩn

| Aggregate / record | Internal ID | Business identity/invariant |
|---|---|---|
| Instrument | `InstrumentId` | `(venue_id, canonical_symbol, valid_from)` xác định rule/version history |
| Strategy definition/version/instance | `StrategyDefinitionId`, `StrategyVersionId`, `StrategyInstanceId` | instance pin definition/version/config/deployment hash |
| Risk policy/decision/reservation | `RiskPolicyId`, `RiskDecisionId`, `ReservationId` | policy version immutable sau activation; reservation không âm |
| Order intent/order | `OrderIntentId`, `OrderId` | `ClientOrderId` duy nhất trong `(venue_id, account_id)` và không reuse |
| Submission attempt | `SubmissionAttemptId` | `(order_id, attempt_no)` duy nhất, `attempt_no > 0` |
| Fill | `FillId` | venue fill ID hoặc source fingerprint duy nhất trong venue/account |
| Journal entry/posting | `JournalEntryId`, `PostingId` | entry/posting append-only và cân bằng theo accounting policy |
| Dataset/deployment | `DatasetVersionId`, `DeploymentId` | có manifest/hash và lineage đủ để replay |
| Command/approval/audit | `CommandId`, `ApprovalId`, `AuditLogId` | actor, subject, reason, correlation và recorded time luôn có |
| AI provider connection | `AIProviderConnectionId` | owner scope + provider/model/catalog/policy-profile version + active/candidate opaque binding revision; raw key không thuộc aggregate |

`VenueOrderId` và venue fill/trade ID là external identifiers: có thể nullable trước acknowledgment, không được thay internal ID.

## 6. Luồng chuẩn từ strategy đến ledger

```text
NormalizedMarketEvent
  -> Strategy signal / ProposedOrderIntent
  -> execution canonicalization + OrderIntent + ClientOrderId
  -> RiskDecision + Reservation
  -> Order / SubmissionAttempt / Outbox
  -> venue evidence / Fill
  -> JournalEntry + Postings
  -> projections, reconciliation và audit evidence
```

Không bước nào được bỏ qua qua UI, CLI, AI worker hoặc adapter. Venue call chỉ xảy ra sau transaction persist durable order/attempt/outbox; outcome không chắc chắn đi vào `UNKNOWN` rồi reconciliation.

## 7. Contract dữ liệu tối thiểu

### 7.1 Instrument và market event

Instrument phải có `venue_id`, canonical symbol, base/quote asset, tick/lot size, min/max quantity, min notional, precision, trading status, `effective_at`, `valid_from`, `valid_to`, source checksum và adapter version. Market event phải có `event_id`, `schema_version`, venue, instrument, four operational timestamps, source sequence/trade ID nếu có, price/quantity/side phù hợp, quality flags và correlation metadata.

### 7.2 ProposedOrderIntent và OrderIntent

`ProposedOrderIntent` chứa strategy instance, side/type, quantity, giá/trigger khi có, time-in-force và input snapshot reference; nó không có `ClientOrderId` và không được submit.

`OrderIntent` phải thêm `order_intent_id`, `client_order_id`, account/venue/instrument, deployment/correlation, created/expiry time, strategy/config version, canonical request hash và capability-validated flags. Unsupported capability bị reject rõ trước submission; không fallback âm thầm.

### 7.3 RiskDecision

RiskDecision chỉ là `APPROVE`, `REJECT` hoặc `REQUIRE_MANUAL_APPROVAL`; phải mang quantity được duyệt, policy/version, portfolio/reference/market snapshot version, reservation ID khi có, lý do machine-readable, input hash, decision time và expiry. Approval của con người luôn chạy lại full risk trên snapshot mới.

### 7.4 Event envelope

Mọi integration event có `id`, `type`, `schema_version`, `source`, `occurred_at`, `correlation_id`, `causation_id`, `trace_id`, `subject_id` và `data`. Tên event là quá khứ; command là động từ; query bắt đầu bằng `Get`, `List` hoặc `Search`.

## 8. Invariant domain không được waiver

1. Strategy/AI/UI không tự tạo `ClientOrderId`, không gọi venue, database hoặc network trực tiếp.
2. Chỉ execution application gửi order sau risk approve/reservation hợp lệ.
3. Một `ClientOrderId` không reuse trong cùng venue/account, kể cả terminal order.
4. Fill, journal entry, posting, audit evidence và lifecycle event không bị sửa/xóa bởi runtime role.
5. Duplicate/out-of-order evidence không được tạo fill, reservation release hoặc posting lần hai.
6. Outcome submit không rõ không được retry blind; phải `UNKNOWN` và reconcile.
7. Projection không được là accounting truth, và reconciliation không overwrite history để “khớp” sàn.
8. Thiếu/stale reference, market, portfolio, lease hoặc policy state phải fail closed, trừ emergency reduce-only policy đã phê duyệt riêng.
9. AI provider connection chỉ được AI worker dùng khi ACTIVE, đúng owner scope/policy; không có field/domain event nào mang raw key hoặc tạo execution capability.

## 9. Phần hoãn và điều kiện thay đổi

NautilusTrader không sở hữu canonical domain; chỉ có thể được thêm sau ADR-0006 được APPROVED. Derivatives, leverage, transfer/withdrawal, multi-account, multi-venue, tax engine và AI memory là ngoài phạm vi hiện tại. Bất kỳ thay đổi meaning/state/public field nào phải có ADR, schema version và compatibility/migration evidence.

## 10. Acceptance trước implementation

- [ ] Các thuật ngữ và ownership không mâu thuẫn với Master/ADR liên quan.
- [ ] Mọi contract mới map được về aggregate/context/invariant ở tài liệu này.
- [ ] State/lifecycle chi tiết dùng [OMS state machine](oms-state-machine.md).
- [ ] Risk/ledger chi tiết dùng [risk policy](risk-policy.md) và [accounting policy](accounting-policy.md).
- [ ] Account Owner phê duyệt cùng ADR bắt buộc trước khi dùng làm input Task 0.4/Phase 1.
