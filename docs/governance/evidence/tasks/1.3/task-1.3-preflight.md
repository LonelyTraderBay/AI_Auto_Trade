# Task 1.3 — Preflight package cho durable submit và local fake venue

| Trường | Giá trị |
|---|---|
| Document ID | GOV-TASK-1.3-PREFLIGHT-001 |
| Phiên bản | 0.2.1 |
| Trạng thái | IN_REVIEW — approval đã ghi nhận; canonical task card vẫn BLOCKED |
| Owner | Technical Operator |
| Reviewer/Approver | Account Owner; Risk Approver và Security/Backup Owner theo control |
| Ngày chuẩn bị | 2026-08-12 |
| Master authority | `AI_AUTO_TRADE_MASTER_SPEC.md` v2.3.9 |
| Instruction authority | `AGENTS.md`, ENG-AI-001 v1.2.0 |
| Phạm vi dự kiến | Phase 1 — local simulator/no external venue |
| Ledger | Chưa mở; vẫn gated bởi accounting annex |

> Tài liệu này là gói chuẩn bị để Account Owner review. Nó không phê duyệt risk policy, ADR, contract, migration, gate hoặc task card; không được dùng làm căn cứ để sửa `src/`, `migrations/`, `configs/`, `contracts/` hay dependency.

## 1. Kết luận preflight

Task 1.3 hiện **BLOCKED, chưa READY**. Approval đã được ghi nhận, nhưng AI chưa được triển khai durable submit, fake venue adapter, persistence, risk reservation, reconciliation hoặc ledger runtime cho đến khi authority sync, PostgreSQL no-skip và branch precondition đạt.

Nền tảng đã hoàn thành:

- Task 1.1 deterministic primitives — `DONE`.
- Task 1.2 OMS state machine — `DONE`.
- OMS baseline `DOM-OMS-001` — approved cho local simulator/Phase 1.
- Transaction baseline `DATA-TXN-001` — approved cho local simulator/Phase 1.
- Accounting baseline `DOM-ACC-001` — approved nhưng ledger runtime còn gated.

## 2. Mục tiêu sau khi được mở task

Mục tiêu cuối của nhóm công việc này là tạo một execution boundary có thể kiểm chứng trong local simulator:

1. Nhận internal submit command đã qua risk approval và reservation.
2. Ghi nhận intent/attempt theo idempotency key trước khi gửi venue.
3. Gọi một fake venue deterministic, không network, không credential và không external SDK.
4. Xử lý `ACCEPTED`, `REJECTED`, `PARTIAL_FILL`, `FILLED`, `CANCELLED`, `TIMEOUT` và `UNKNOWN` theo contract đã được phê duyệt.
5. Không retry mù khi kết quả submit là `UNKNOWN`; chỉ được chuyển sang query/reconciliation path đã chốt.
6. Phát hành event/outbox theo contract versioned và giữ audit history bất biến.

Mục tiêu này **chưa cho phép** kết nối sàn thật, ghi ledger tài chính hoàn chỉnh, mở withdrawal hoặc đưa LLM vào execution path.

## 3. Đề xuất tách phạm vi

### 3.1. Gói A — chốt tài liệu và contract trước khi code

| Mã | Nội dung bắt buộc | Đầu ra cần được review |
|---|---|---|
| A-01 | Chốt risk policy annex cho local simulator | Tham số, đơn vị, precision, expiry, fixture và policy hash |
| A-02 | Chốt canonical Fill contract | Field, Decimal scale, fee/rebate, partial-fill và terminal mapping |
| A-03 | Hoàn thiện execution/risk data dictionary | Column, type, constraint, CAS/version, lease, retention và role |
| A-04 | Hoàn thiện ERD logical-to-physical mapping | Quan hệ, key, uniqueness, index và cross-context boundary |
| A-05 | Tạo fake-venue contract/harness design | Scenario format, deterministic clock/sequence, fault injection và evidence |
| A-06 | Sửa mâu thuẫn ADR-0012 | Isolation/concurrency rule không còn `If approved` hoặc `DRAFT` |
| A-07 | Chốt contract registry status | Các command/event được phép implement, không chỉ validate schema |

### 3.2. Gói B — implementation sau khi Gói A được approve

Gói B phải có task card code riêng, `status: READY`, branch riêng, allowlist riêng và reviewer xác định. Không chuyển thẳng từ tài liệu này sang code.

- Durable submit state machine orchestration.
- Persistence/migration cho các bảng đã có dictionary và ERD được phê duyệt.
- Local fake venue adapter và conformance tests.
- Crash/restart, duplicate, timeout, out-of-order và unknown-outcome tests.
- Recovery/reconciliation boundary; không retry submit unknown.

## 4. Blocker hiện tại

| Blocker | Bằng chứng | Điều kiện gỡ |
|---|---|---|
| Task card chưa `READY` | Canonical `tasks/active/1.3-durable-submit-fake-venue.yaml` đang `BLOCKED` | Cấp PostgreSQL no-skip, hoàn tất authority sync, đổi branch và human review chuyển `READY` |
| Task-directory hygiene | Card `0.0.7` đã chuyển sang `tasks/completed/` | Đã xử lý; duy trì không duplicate active authority |
| Risk policy còn `DRAFT` | `docs/backend/domain/risk-policy.md` | Risk Approver + Account Owner phê duyệt annex và fixture |
| Canonical model/Fill còn `DRAFT` | `docs/backend/domain/canonical-domain-model.md` | Phê duyệt field semantics và terminal mapping |
| Data dictionary/ERD còn `DRAFT` | `docs/backend/data/data-dictionary.md`, `erd.md` | Hoàn thiện cột, constraint, index, role, retention và migration plan |
| Chưa có fake venue contract/harness | `docs/backend/engineering/test-strategy.md` § venue conformance | Phê duyệt protocol deterministic và fault matrix |
| Contract registry `IN_REVIEW` | `docs/backend/contracts/contract-registry.md` | Registry review cho command/event dùng trong Task 1.3 |
| ADR-0012 còn nội dung mâu thuẫn | `docs/backend/adr/0012-transaction-concurrency.md` | Amendment/clarification có reviewer và timestamp |
| Chưa có Postgres integration evidence | `tests/integration/test_platform_migrations.py` bị skip khi thiếu `DATABASE_URL` | Cấp database test và lưu migration/concurrency evidence |

## 5. Các quyết định Account Owner cần xác nhận

Các mục dưới đây là **open decisions**, không được AI tự suy đoán:

| ID | Quyết định | Giá trị cần chốt |
|---|---|---|
| OD-1.3-01 | Fake venue protocol | Request/response envelope, correlation, idempotency và version |
| OD-1.3-02 | Scenario script | Sequence event, delay, duplicate, out-of-order, timeout, crash và retryable/non-retryable fault |
| OD-1.3-03 | UNKNOWN handling | Trạng thái lưu, query/reconcile path, operator action và tuyệt đối không blind retry |
| OD-1.3-04 | Idempotency boundary | Khóa logic, uniqueness scope, replay result và conflict behavior |
| OD-1.3-05 | Order/attempt/event identity | UUIDv7 nội bộ, external reference opaque và quan hệ audit |
| OD-1.3-06 | Concurrency/lease | Isolation, CAS/version, fencing token, lease expiry và crash recovery |
| OD-1.3-07 | Fill/fee/rebate precision | Decimal scale, rounding mode, quantity/price/fee semantics |
| OD-1.3-08 | Risk reservation boundary | Reservation lifecycle, release/consume, expiration và kill-switch interaction |
| OD-1.3-09 | Retention/immutability | Audit/event retention, append-only rule và forward-fix policy |
| OD-1.3-10 | Database test authority | PostgreSQL version/profile, `DATABASE_URL`, seed, UTC và Decimal context |
| OD-1.3-11 | Contract approval | Contract registry status và approver cho command/event/fake venue |
| OD-1.3-12 | Ledger boundary | Xác nhận Task 1.3 không activate portfolio ledger khi accounting annex chưa đủ |

## 6. Invariants bắt buộc cho task implementation tương lai

- Không có đường trực tiếp từ LLM/AI tới exchange hoặc fake venue write path.
- Risk engine là deterministic; fake venue không được quyết định risk approval.
- Không dùng float cho tiền, giá, quantity hoặc fee; API dùng string và DB dùng `NUMERIC(38,18)` khi được phê duyệt.
- Không retry submit khi outcome là `UNKNOWN`.
- Không hard-delete order, attempt, event hoặc audit history.
- Domain không import FastAPI, SQLAlchemy, Pydantic, CCXT, Nautilus hoặc vendor SDK.
- Clock, UUID và random source phải được inject/deterministic trong test.
- Mọi duplicate, replay, out-of-order và terminal transition phải có kết quả deterministic.
- Public command/event schema không được thay đổi âm thầm; breaking change cần version/ADR.

## 7. Acceptance criteria đề xuất cho task code sau này

Task implementation chỉ được mở khi task card riêng ghi rõ và reviewer chấp thuận toàn bộ:

1. Submit cùng idempotency key không tạo thêm attempt hoặc venue side effect.
2. Database failure trước/sau submit không làm mất audit intent và được phân loại rõ.
3. `UNKNOWN` không tự động retry; recovery path tạo evidence riêng.
4. Fake venue chạy cùng seed/clock/script cho cùng một sequence kết quả.
5. Partial fill, duplicate fill, out-of-order event và terminal event đều được kiểm tra invariant.
6. Restart/crash test chứng minh không tạo duplicate order side effect.
7. Migration chỉ chứa object đã có approved dictionary/ERD/task card.
8. Contract validator, type checker, linter, unit test và Postgres integration đều có exit code/evidence.
9. Diff khớp allowlist; không có secret, dependency ngoài card hoặc file runtime ngoài scope.
10. Báo cáo kết thúc đề xuất tối đa `REVIEW`, không tự chuyển `DONE`.

## 8. Checklist để chuyển sang READY

- [x] Account Owner xác nhận phạm vi local simulator/no external venue trong approval record.
- [x] Risk Approver và Account Owner chốt risk annex/fixture/hash/expiry trong approval record.
- [x] Canonical domain model và Fill contract có task-scoped approval; global document promotion vẫn deferred.
- [x] Execution/risk dictionary và ERD addendum có đủ design column/constraint/index/role/retention; physical DDL vẫn gated.
- [x] Fake venue protocol và conformance harness design được phê duyệt; runtime harness chưa chạy.
- [x] ADR-0012 đã amend/clarify, không còn nội dung `If approved` gây mâu thuẫn.
- [x] Contract registry ghi rõ task-scoped artifacts được phép implement sau `READY`.
- [x] Task card code có `allowed_globs`, `forbidden_globs`, expiry, reviewer, commands và evidence path.
- [x] Không còn card `DONE` trong `tasks/active/`; card cũ đã reconcile sang `tasks/completed/`.
- [x] Branch pattern đúng (`task/1.3-durable-submit-fake-venue`) và working tree đã clean sau docs commit.
- [ ] Có PostgreSQL test environment để không bỏ qua migration/concurrency tests.
- [x] Ledger runtime vẫn bị khóa nếu accounting annex chưa được phê duyệt.

## 9. Evidence dự kiến

Khi Gói A được review, evidence nên được lưu dưới `docs/governance/evidence/tasks/1.3/` và tối thiểu gồm:

- Quyết định/approval record cho từng OD-1.3-xx.
- Snapshot/hash của risk policy fixture và fake venue scenario script.
- Contract validation output và registry review record.
- Data dictionary/ERD review record.
- ADR-0012 amendment record.
- PostgreSQL migration/concurrency test output nếu task implementation được mở.
- Task report ghi rõ instruction provenance, branch, allowlist, command exit code và blocker còn lại.

## 10. Quyết định đề xuất

**Đề xuất hiện tại:** giữ Task 1.3 ở `BLOCKED`; hoàn thiện và review Gói A; sau khi mọi checklist bắt buộc đạt, tạo một task card implementation mới ở trạng thái `READY`. Không dùng tài liệu này để suy ra quyền code.

| Vai trò | Quyết định | Thời điểm |
|---|---|---|
| Technical Operator | Chuẩn bị hồ sơ và không code khi chưa READY | 2026-08-12 |
| Account Owner | Review scope, open decisions và approval checklist | Chờ xác nhận |
| Risk Approver | Review risk annex/fixtures | Chờ xác nhận |
