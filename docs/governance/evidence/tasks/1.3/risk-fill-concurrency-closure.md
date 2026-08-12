# Task 1.3 — Risk, Fill và concurrency closure draft

| Trường | Giá trị |
|---|---|
| Document ID | GOV-TASK-1.3-CLOSURE-RFC-001 |
| Phiên bản | 0.2.0 |
| Trạng thái | APPROVED FOR TASK 1.3 DESIGN; runtime evidence pending |
| Parent | [Task 1.3 preflight](task-1.3-preflight.md) |
| Decision register | [OD-1.3 decisions](owner-decision-register.md) |
| Ngày lập | 2026-08-12 |

> Approval record `2026-08-12T09:19:16Z` chốt các giá trị trong packet cho local simulator. Tài liệu này vẫn không thay thế risk policy, canonical Fill hoặc migration authority.

## 1. Authority hiện có

| Chủ đề | Nguồn hiện tại | Đánh giá |
|---|---|---|
| OMS transition | `docs/backend/domain/oms-state-machine.md` | APPROVED baseline; Task 1.2 đã DONE |
| Transaction/concurrency | `docs/backend/data/transaction-and-concurrency.md` | APPROVED baseline cho local simulator/Phase 1 |
| Risk structure | `docs/backend/domain/risk-policy.md` + approved local fixture | Task-scoped approval recorded; authority sync pending |
| Canonical Fill | `docs/backend/domain/canonical-domain-model.md` §7.5 | Semantics approved; authority sync pending |
| ADR isolation | `docs/backend/adr/0012-transaction-concurrency.md` | APPROVED v0.3.0; wording blocker closed |

## 2. Risk closure checklist

| Hạng mục | Cần chốt | Không được suy đoán |
|---|---|---|
| Scope | account/venue/instrument/environment áp dụng | Không mặc định venue/account thật |
| Exposure/notional | limit, unit, Decimal scale, inclusive/exclusive boundary | Không dùng cap tùy ý để làm test pass |
| Rate | window, counter key, clock source, behavior khi clock lùi | Không dùng wall-clock global trong domain |
| Loss/drawdown | calculation source, reset timezone, unavailable-data behavior | Không tự chọn reset timezone |
| Freshness | threshold, timestamp, market-data source, fail-closed behavior | Không coi fake price luôn fresh nếu policy chưa nói |
| Fee/slippage | buffer formula, asset/quote convention, rounding | Không đoán fee = 0 trừ khi fixture nói rõ |
| Reservation | create/release/consume/expire, uniqueness, amount semantics | Không mở reservation pre-approval extension |
| Manual approval | required role, re-auth, expiry, full re-evaluation | Không dùng approval flag để bypass risk |
| Kill switch | hierarchy, default action, freeze/cancel capability | Không tự bật FLATTEN |
| Policy lifecycle | version, hash, activation/expiry, immutable snapshot | Không mutate policy snapshot đã dùng |

## 3. Fill closure checklist

Canonical Fill draft phải xác nhận tối thiểu:

- `fill_id` là UUIDv7 nội bộ.
- `order_id`, `client_order_id` và correlation ID tồn tại.
- `venue_fill_id` nullable khi venue không cung cấp.
- `price`, `quantity`, `fee_amount` là Decimal; API representation là string.
- `fee_asset` có semantics rõ ràng.
- `liquidity_flag` thuộc `MAKER | TAKER | UNKNOWN`.
- Có `occurred_at`, `received_at`, `processed_at`, `recorded_at` dạng UTC.
- `sequence` chỉ là ordering nội bộ, không thay thế dedupe identity.
- Dedupe theo venue/account + venue fill ID hoặc source fingerprint khi thiếu venue ID.
- Fill immutable; duplicate/conflict tạo evidence, không overwrite.
- Fee thiếu phải được biểu diễn bằng giá trị được policy cho phép và quality flag rõ ràng; không đoán ngầm.

Các điểm còn cần Owner decision: fee/rebate semantics, rounding mode, asset precision, source fingerprint format và conflict resolution.

## 4. Concurrency closure checklist

### 4.1. Pre-submit unit of work

Baseline hiện có yêu cầu:

1. `SERIALIZABLE` chỉ bao phủ risk decision/reservation, execution order/attempt và platform outbox.
2. Lock order cố định: risk limit/reservation → execution order → platform outbox.
3. Không gọi venue/network trong transaction.
4. Serialization/deadlock retry chỉ xảy ra trước external action và phải chạy lại full risk/CAS.
5. Commit thành công rồi execution leader mới được claim và gửi một venue request.

### 4.2. Unknown outcome

- Timeout, connection break hoặc ambiguous response phải persist `UNKNOWN`/reconciliation state.
- Không retry external submit theo cơ chế generic.
- Query/reconciliation phải dùng client identity và evidence, không tạo intent mới tự động.
- Lease loss dừng claim/submit mới; in-flight unknown chuyển recovery.

### 4.3. ADR-0012 amendment cần chuẩn bị

Đề xuất thay câu còn mâu thuẫn ở ADR-0012 §Decision bằng nội dung xác nhận rằng baseline `READ COMMITTED + constraint dedupe + CAS` cho fill/reconciliation đã được Account Owner approve trong DATA-TXN-001 v0.2.1, đồng thời giữ `SERIALIZABLE` cho `TradingSubmissionUnitOfWork`. Amendment phải có version, rationale, reviewer và UTC timestamp; AI không tự đổi status approval.

## 5. Acceptance evidence đề xuất

- Risk fixture có policy version/hash/expiry và Decimal context pin.
- Negative tests cho stale policy, stale market data, duplicate reservation, expired approval và kill-switch freeze.
- Fill tests cho partial fill, duplicate venue ID, missing venue ID, source fingerprint collision, fee quality flag và out-of-order sequence.
- Concurrency tests cho serialization retry trước venue, CAS conflict, lease expiry, fencing token và unknown outcome.
- Review record chứng minh không có external network call trong unit of work.

## 6. Approval status

| Artifact/decision | Status | Required action |
|---|---|---|
| Risk policy annex | APPROVED FOR LOCAL SIMULATOR | Sync task-scoped authority; no live policy |
| Fill contract | APPROVED FOR TASK 1.3 DESIGN | Sync canonical model before implementation |
| ADR-0012 amendment | APPLIED | ADR-0012 v0.3.0 is authority |
| Task 1.3 implementation | BLOCKED | PostgreSQL 17 no-skip, branch and authority sync are evidenced; canonical card still requires Account Owner `READY` transition |
