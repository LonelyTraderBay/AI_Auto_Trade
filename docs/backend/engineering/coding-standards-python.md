# ENG-PY-001 — Coding standards Python

| Trường | Giá trị |
|---|---|
| Version / Status | 1.1.0 / IN_REVIEW |
| Owner / Approver | Technical Operator / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | FR-EXEC-001, FR-RSK-001, NFR-SEC-001, NFR-OPS-001; ADR-0002, ADR-0011, ADR-0012, ADR-0014 |
| Change summary | 1.1.0 (2026-07-31, Technical Operator, Pending): đổi title ID ENG-002 -> ENG-PY-001; sửa Related FR-OMS-001 -> FR-EXEC-001 (dangling ID); thêm §4a Exception taxonomy và error mapping (DRAFT). 1.0.0: quy tắc Python áp dụng từ Task 0.1; chưa định nghĩa source implementation. |

## 1. Phạm vi và toolchain

Runtime chuẩn là Python 3.12.x. `uv`, Ruff, Pyright strict, Pytest, Hypothesis và Import Linter/architecture tests là toolchain đã đóng theo master §3 và §13. Không dùng mypy, Node.js/TypeScript, framework mới, message broker hoặc database khác nếu không có ADR `APPROVED`.

Version runtime/dependency phải pin trong `pyproject.toml`, `uv.lock`, image digest và CI image khi các file đó được Task 0.1 tạo. Không thêm package bằng `pip install` tự phát hoặc ghi version range mở cho production artifact.

## 2. Layer và import boundary

Mỗi bounded context có `domain`, `application`, `ports`, `adapters`, `tests`.

- `domain`: immutable value object/entity/policy; không import FastAPI, SQLAlchemy, Pydantic, CCXT, NautilusTrader, OpenAI SDK, HTTP client, filesystem, environment hoặc clock/random global.
- `application`: orchestration/use case, nhận port và Unit of Work qua constructor; không biết vendor SDK hoặc transport HTTP.
- `ports`: Protocol/ABC tối thiểu, type rõ ràng, không chứa vendor DTO.
- `adapters`: mapping/IO/vendor. Chỉ adapter được dùng framework/provider SDK.
- Composition root ở `bootstrap`/`apps`, không trong domain hoặc strategy.

Domain không truy cập DB/network/env/file trực tiếp. Strategy không tạo `ClientOrderId`, không place order và không tự retry external submission.

## 3. Type, dữ liệu và immutability

- Public function/method/port có annotation đầy đủ; Pyright strict phải pass.
- Cấm `Any`, `typing.cast` để che lỗi, `# type: ignore`, `# noqa`, broad/bare `except`, mutable default và dynamic attribute trong core. Ngoại lệ chỉ có waiver ID chưa hết hạn, approval và test chứng minh compensating control.
- Money, price, quantity, fee và PnL dùng `Decimal`; không dùng `float` hoặc `math` float. Persistence là `NUMERIC(38,18)`; wire/API serialize Decimal thành string.
- ID nội bộ là typed UUIDv7 value object, không truyền raw string tự do giữa contexts. Venue ID/vendor reference lưu riêng, không là primary key nội bộ.
- Timestamp timezone-aware UTC. Domain nhận `Clock`; random simulator/strategy nhận `RandomSource`; seed phải persist trong manifest/evidence.
- Event/domain object public immutable. Mutation projection phải explicit, versioned và có concurrency policy.

## 4. Error handling, retry và concurrency

- Exception domain phải explicit, machine-readable và map an toàn vào error catalog; không trả stack trace/vendor raw payload qua public API.
- Validation/domain conflict không retry. Transient external error chỉ retry theo operations policy, bounded backoff/jitter/circuit breaker.
- Submit order timeout, disconnect hoặc lease loss là `UNKNOWN`; không retry blind. Persist attempt/request hash trước HTTP, sau đó reconciliation.
- Chỉ các Unit of Work được master §7.7 whitelist mới được atomic xuyên contexts: `TradingSubmissionUnitOfWork`, `FillLedgerUnitOfWork`, `ReconciliationResolutionUnitOfWork`.
- Lock order cố định `risk -> execution -> outbox`; retry serialization chỉ trước external side effect. Không viết transaction tiện tay qua contexts.

## 4a. Exception taxonomy và error mapping (DRAFT)

> DRAFT — cần phê duyệt.

- Base hierarchy: mỗi context domain định nghĩa exception gốc riêng (ví dụ `RiskError`, `ExecutionError`, `LedgerError`) kế thừa từ `AiAutoTradeDomainError` trong `shared_kernel`.
- Application layer bọc domain exception thành application error có thuộc tính `code` bắt buộc, map 1-1 vào mã trong `contracts/errors/error-catalog.md`.
- Adapter boundary dịch vendor exception thành typed adapter error; vendor exception không được leak qua port.
- Control API layer là nơi duy nhất serialize error thành `ErrorEnvelope`.
- Mapping table (exception class -> catalog code) sống trong một module registry duy nhất, có contract test đối chiếu error-catalog để CI fail khi drift.

## 5. Naming, comments và API design

- Một function/use case có một intent rõ ràng. Tránh utility module chung che domain ownership.
- Enum wire dùng `SCREAMING_SNAKE_CASE`; Python enum không được đổi nghĩa wire value đã public.
- Comment giải thích invariant/quyết định, không diễn tả lại code. `TODO` trên safety path bị cấm nếu không có waiver ID/expiry.
- Public boundary lấy/ trả typed domain model hoặc versioned DTO; mapping vendor DTO tại adapter.
- Không log secret, token, raw authorization header, raw account PII hoặc raw vendor payload. Dùng redactor đã được review khi sau này tạo logging.

## 6. Testability bắt buộc

Code phải inject Clock, RandomSource, ports và policy. Không mock domain policy để giả pass; test invariant/state machine/failure path phải dùng real domain behavior. Unit test mặc định không network, real DB, current time, global RNG hay locale.

Với thay đổi OMS/risk/ledger/reconciliation phải thêm negative và recovery test: duplicate/out-of-order, timeout/unknown, stale data, lost lease, terminal-state rule và double-entry balance khi phù hợp.

## 7. Definition of Done cho code Python

Trước khi một source module được coi DONE: task allowlist pass, dependency/import boundary checked, type/lint/test theo task pass, contract/ADR link cập nhật, Decimal/time/idempotency/concurrency/security impact được review và evidence được lưu. Không có Phase 0.0 exception để tạo source module.

