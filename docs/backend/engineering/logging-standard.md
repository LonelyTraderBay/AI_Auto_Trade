# ENG-LOG-001 — Logging standard

| Thuộc tính | Giá trị |
|---|---|
| Document ID | ENG-LOG-001 |
| Phiên bản | 0.1.1 |
| Trạng thái | DRAFT |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-08-02 |
| Change summary | 0.1.1 (2026-08-02): bổ sung 2 row header còn thiếu theo GOV-DOC-001 §3 (Ngày hiệu lực, Change summary) — audit toàn diện; nội dung logging không đổi. |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §12.1–§12.5; docs/backend/engineering/coding-standards-python.md §5; docs/backend/security-ops/slo-sli-alert-policy.md |
| Related | NFR-AUD-001, NFR-OPS-001, SEC-AUD-001 |

> DRAFT — cần phê duyệt. Tài liệu chuẩn hóa logging cho toàn bộ backend từ Task 0.1; khi mâu thuẫn, master §12 và ADR `APPROVED` có quyền ưu tiên cao hơn.

## 1. Nguyên tắc

- Structured JSON-lines là định dạng log duy nhất từ Task 0.1; không log dạng free-text/plain.
- Dùng stdlib `logging` cộng JSON formatter đặt trong `shared_kernel`; không thêm dependency logging mới.
- Một logger factory duy nhất trong `shared_kernel` cấp logger cho mọi module; cấm `print()` trong source code.

## 2. Schema bắt buộc mỗi log record

Mỗi record phải có:

| Field | Yêu cầu |
|---|---|
| `timestamp` | UTC ISO-8601 có `Z` |
| `level` | Level chuẩn của stdlib logging |
| `logger` | Tên logger (module path) |
| `message` | Human-readable |
| `event` | Machine-readable, `snake_case` |
| `trace_id` | Bắt buộc |
| `correlation_id` | Bắt buộc |
| `causation_id` | Khi có |
| `actor` | Actor/machine identity |
| `deployment_id` | Khi runtime |
| `context` | Bounded context name |

Extra fields chỉ theo whitelist đã đăng ký; không nhận unbounded dict.

## 3. Level policy

- `DEBUG`: dev only; tắt ở testnet trở lên.
- `INFO`: lifecycle events.
- `WARNING`: retry/degraded/threshold gần chạm.
- `ERROR`: failed operation đã có xử lý.
- `CRITICAL`: safety invariant/kill switch/fail-closed; bắt buộc kèm alert theo OPS-001.

## 4. Redaction

- Mọi secret/credential/API key/PII bị chặn ở formatter layer bằng redaction hook: deny-list field names cộng pattern scan.
- Raw venue payload chỉ được log sau redaction.
- Vi phạm redaction là SEV finding theo SECURITY.md.

## 5. Correlation propagation

- `trace_id`/`correlation_id`/`causation_id` truyền qua chuỗi command -> event envelope (master §5.7) -> outbox -> inbox -> consumer log.
- Mọi log trong một unit of work dùng cùng `correlation_id`.

## 6. Retention và rotation

- Retention/rotation theo ADR-0013 khi được approve.
- Local dev không giữ log quá 7 ngày.
- Không commit log file vào repo.

## 7. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | Khởi tạo logging standard: JSON-lines, schema record, level policy, redaction, correlation propagation, retention. | Technical Operator | Pending |
