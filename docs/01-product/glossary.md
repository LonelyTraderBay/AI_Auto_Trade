# Glossary — thuật ngữ chuẩn

| Thuộc tính | Giá trị |
|---|---|
| Document ID | PRD-GLOSSARY-001 |
| Phiên bản | 0.2.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §3–§12 và §16 |
| Related requirements | FR-MKT-001, FR-EXEC-001, FR-LED-001, FR-REC-001, FR-RSK-001, FR-AI-001, NFR-AUD-001, NFR-SAFE-001, NFR-AI-001 |
| Related ADR | ADR-0003, ADR-0004, ADR-0005, ADR-0007, ADR-0011, ADR-0012, ADR-0016 |

> Tên type/field/wire enum cuối cùng phải do contract schema quyết định. Glossary này dùng để tránh nhầm semantic khi viết requirement, ADR, task và test; không thay thế contract machine-readable.

## 1. Domain và identity

| Thuật ngữ | Định nghĩa chuẩn |
|---|---|
| Account | Phạm vi tài khoản/sub-account tại venue; một identity/business scope, không phải database user. |
| Venue | Sàn hoặc môi trường venue được adapter hỗ trợ. |
| Instrument | Công cụ giao dịch canonical, gồm venue/symbol/base/quote/filter/precision/version hiệu lực. |
| Asset | Đơn vị tài sản/currency được dùng trong instrument, balance hoặc ledger. |
| Internal ID | UUIDv7 dùng làm primary/canonical identifier nội bộ; không dùng venue ID làm primary key. |
| VenueOrderId | Identity do venue cấp; lưu riêng và có thể chưa tồn tại khi outcome unknown. |
| ClientOrderId | Identity do execution application sinh một lần trước submission, không reuse trong cùng venue/account. |
| Correlation ID | ID liên kết toàn bộ flow nghiệp vụ end-to-end. |
| Causation ID | ID của event/command trực tiếp gây ra event hiện tại. |
| Trace ID | ID cho telemetry trace xuyên process/adapter. |
| Canonical request hash | SHA-256 của canonical JSON v1 cho audit/phát hiện payload change; không thay ClientOrderId idempotency. |

## 2. Trading, risk và OMS

| Thuật ngữ | Định nghĩa chuẩn |
|---|---|
| ProposedOrderIntent | Proposal strategy tạo; chưa có ClientOrderId và không được submit. |
| OrderIntent | Intent canonical sau execution validation, có identity/scope/payload/audit metadata và đi qua risk. |
| RiskDecision | Kết quả APPROVE, REJECT hoặc REQUIRE_MANUAL_APPROVAL, kèm policy/snapshot/input hash, reason, expiry và reservation khi có. |
| Reservation | Hold balance/exposure trước submit; chuyển/release theo lifecycle, không được silently clear. |
| OMS | Order Management System quản lý canonical order state, event, attempt và reconciliation semantics. |
| SubmissionAttempt | Một attempt outbound đã persist trước request; timeout không cho phép tạo blind retry. |
| Unknown outcome | Không thể xác định external submit/cancel đã được venue xử lý hay chưa; phải reconcile. |
| Reconciliation | Đối soát internal với external snapshot/evidence, tạo case và safe state thay vì overwrite history. |
| EXTERNAL order | Order tồn tại ở venue nhưng không có canonical internal order; classification phục vụ reconciliation, không phải OMS state. |
| Terminal correction | Event/evidence append-only điều chỉnh outcome terminal khi venue evidence đến muộn; không reopen terminal state thành non-terminal. |
| Kill switch | Control theo hierarchy GLOBAL, VENUE, ACCOUNT, STRATEGY, INSTRUMENT; default FREEZE ngăn exposure tăng. |
| Manual approval | Workflow RiskDecision REQUIRE_MANUAL_APPROVAL; approver phải chạy fresh risk evaluation, không bypass policy. |

### OMS state name

Tên state wire/canonical dùng đúng chữ hoa:

~~~text
CREATED, PENDING_MANUAL_APPROVAL, RISK_APPROVED, RISK_REJECTED,
SUBMISSION_QUEUED, SUBMITTING, OPEN, PARTIALLY_FILLED, FILLED,
CANCEL_REQUESTED, CANCELLED, REJECTED, EXPIRED, UNKNOWN,
RECONCILING, LOST
~~~

## 3. Ledger, data và time

| Thuật ngữ | Định nghĩa chuẩn |
|---|---|
| Double-entry ledger | Accounting truth nội bộ gồm journal entry immutable và postings cân bằng; projection có thể rebuild. |
| Journal entry | Nhóm posting accounting của một economic event. |
| Posting | Dòng debit/credit/asset theo accounting policy; không sửa để khớp venue. |
| Projection | Read model derived từ event/ledger; có thể rebuild. |
| Dataset manifest | Metadata version/checksum/lineage của dữ liệu dùng cho replay/backtest. |
| Point-in-time correctness | Backtest/replay chỉ dùng data/reference có hiệu lực tại thời điểm quyết định, không look-ahead. |
| occurred_at | Thời điểm event xảy ra ở source/domain. |
| received_at | Thời điểm adapter nhận input. |
| processed_at | Thời điểm normalizer/handler xử lý hoàn tất. |
| recorded_at | Thời điểm PostgreSQL ghi record. |
| effective_at | Thời điểm rule/reference/config bắt đầu có hiệu lực. |
| created_at / updated_at | Thời điểm tạo/cập nhật mutable control/projection record; không thay event timestamp. |
| Decimal | Kiểu số domain cho price, quantity, money, fee và PnL; float bị cấm. |

## 4. Architecture và delivery

| Thuật ngữ | Định nghĩa chuẩn |
|---|---|
| Modular monolith | Một deployable system với bounded context/module rõ, không mặc định microservice. |
| Bounded context | Vùng sở hữu domain/data/contract riêng: reference, market_data, strategy, risk, execution, portfolio_ledger, research, operations, platform hoặc ai_memory theo phase. |
| Domain | Logic thuần Python, không import framework/vendor/IO. |
| Application | Use case/handler orchestration phụ thuộc domain và port. |
| Port | Interface/Protocol mô tả nhu cầu của application/domain với bên ngoài. |
| Adapter | Implementation vendor/framework của port, đặt global dưới adapters/<kind>/<provider>. |
| Composition root | Nơi duy nhất wire concrete adapter vào app/process. |
| Outbox / inbox | Persistent delivery records để hỗ trợ at-least-once publish/consume, dedupe và failure handling. |
| Contract | Machine-readable API, command, event hoặc config schema có version/canonical path. |
| ADR | Architecture Decision Record; chỉ status APPROVED được dùng để mở gate. |
| Task card | YAML authority xác định scope/allowlist/acceptance/evidence cho task; readable Markdown không thay YAML. |
| Gate record | Record có conditions, procedure, evidence, approver và decision PASS/FAIL/REVOKED. |

## 5. Mode và runtime

| Thuật ngữ | Định nghĩa chuẩn |
|---|---|
| BACKTEST | Historical data + simulated clock + simulator; không external network/order. |
| REPLAY | Recorded event/dataset + deterministic replay; không external execution. |
| PAPER_SIMULATOR | Live/replay data với simulator adapter; không gửi venue order. |
| SHADOW | Live data/decision observation với execution port disabled/fail-closed; không gửi venue order. |
| TESTNET | Venue test environment với credential testnet trade-only theo manifest. |
| CANARY | Live venue scope cực nhỏ, trade credential và gate riêng; không đồng nghĩa full live. |
| FULL_LIVE | Scope live mở rộng; ngoài tài liệu MVP, cần ADR/gate mới. |
| Execution leader | Trading node duy nhất được lease/fencing cho venue/account scope để claim/submission. |
| Deployment manifest | Immutable validated identity của code/config/risk/strategy/mode/credential class/deployment scope. |

## 6. Security và operations

| Thuật ngữ | Định nghĩa chuẩn |
|---|---|
| Least privilege | Process/actor chỉ có permission/credential/database role tối thiểu cần thiết. |
| Machine identity | Identity riêng của process/worker, không share human token. |
| Re-auth | Xác thực lại cho dangerous action như release kill switch hoặc credential rotation. |
| Safe state | State giảm/ngăn exposure theo policy, ví dụ FREEZE, BLOCKED hoặc strategy disabled. |
| Redaction | Loại/bảo vệ secret, account detail hoặc sensitive payload khỏi log, trace, fixture/evidence. |
| Waiver | Exception có ADR, scope, compensating control, approver và expiry; không áp dụng safety invariant. |
| BYOK | Bring Your Own Key: user dùng API key của chính họ cho provider được duyệt; không đồng nghĩa platform lưu/hiển thị lại key. |
| AI provider catalog | Registry immutable-versioned của provider/model/endpoint profile/adapter artifact capability/residency-retention đã duyệt; không phải danh sách arbitrary URL. |
| AIProviderConnection | Metadata connection scoped theo owner/environment, chọn provider/model/policy profile và internal opaque active/candidate binding; không chứa raw key. |
| Active/candidate binding | ID opaque nội bộ liên kết connection với secret boundary. Candidate chỉ để validation/rotation, không được inference; cả hai không phải raw key hoặc `secret_ref` public. |
| Secret enrollment | Luồng one-time write-only/no-store qua `secret_ingress` cô lập để user đưa API key vào secret boundary; không đi qua Control API normal middleware, durable command/audit payload, body hash hay key fingerprint. |
| Data-egress policy | Policy giới hạn dữ liệu nào được gửi tới provider/endpoint/model, gồm classification/residency/retention và allowlist field. |
| AI policy profile | Tập policy immutable-versioned bind provider/model/environment với endpoint, egress, usage/budget/timeout/rate/fallback; user chỉ chọn profile đã duyệt, không nhập các policy ID rời. |
| Silent fallback | Tự gửi một request sang provider/model/key khác mà không có policy/consent explicit; bị cấm mặc định. |

## 7. Quy tắc dùng từ

- Dùng OrderIntent thay vì “lệnh” khi nói canonical object trước/qua OMS; dùng venue order chỉ khi nói entity external.
- Không dùng “retry” cho unknown external outcome; dùng reconcile.
- Không gọi projection là source of truth accounting.
- Không gọi testnet/paper/shadow là live trading.
- Không gọi AI proposal là strategy approval, order approval hay execution.
- Không gọi mọi API/endpoint AI là "provider được hỗ trợ"; chỉ catalog entry có adapter/capability/security evidence mới được hỗ trợ.
- Không gọi credential binding, masked label hay validation state là API key; raw key không được read-back.
- Không dùng event_time/received_time nếu semantic là occurred_at/received_at như chuẩn timestamp.

## 8. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | Tạo glossary canonical để giảm ambiguity trong artifact Phase 0.0. | Technical Operator | Pending |
| 0.2.0 | 2026-07-31 | Bổ sung thuật ngữ AI đa provider, BYOK, secret enrollment và data egress. | Technical Operator | Pending |
