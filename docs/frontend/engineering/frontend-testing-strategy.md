# FE-TEST-001 — Frontend testing strategy (Flutter dashboard)

| Thuộc tính | Giá trị |
|---|---|
| Document ID | FE-TEST-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | DRAFT |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực — chờ Account Owner phê duyệt |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §11.3, §13.4, §14 Phase 5; [C-ERR-001](../../../contracts/errors/error-catalog.md); `contracts/api/openapi.yaml`; `contracts/fixtures/`; [SEC-002](../../backend/security-ops/access-control-matrix.md); [NFR](../../shared/product/non-functional-requirements.md) (NFR-DET-001); [FE-DS-001](../design/design-system.md); [FE-SEC-001](../security/frontend-security-policy.md); FE-API-001 §8 |
| Related requirements | NFR-DET-001, NFR-SEC-001, NFR-SAFE-001, NFR-OPS-001 |
| Related ADR | ADR-0015 (auth/re-auth test phụ thuộc), ADR-0016 (BYOK Phase 6) |

> Chiến lược test cho Flutter dashboard, đối xứng với test-strategy backend nhưng điều chỉnh cho client. Các lựa chọn tooling/ngưỡng đánh dấu DRAFT — cần Account Owner phê duyệt. FE-API-001 (frontend API integration guide, soạn cùng đợt tài liệu này) là nguồn hành vi UI chuẩn cho từng error code.

## 1. Test pyramid frontend (DRAFT — cần Account Owner phê duyệt)

| Tầng | Phạm vi | Yêu cầu |
|---|---|---|
| Unit | State notifiers, formatters | Formatter `DecimalString` (hiển thị nguyên văn precision, thousand separator không đổi chữ số — FE-DS-001 §3.1) và timestamp/relative-age display (FE-DS-001 §3.2) phải có unit test biên: số âm, 18 chữ số thập phân (pattern `DecimalString`, openapi.yaml), timezone khác UTC. |
| Widget | Mỗi screen | Mỗi screen test đủ **4 state chuẩn**: loading skeleton, empty, error, stale (FE-DS-001 §5.1). |
| Golden | Screens chuẩn | Bao gồm render semantic colors cho OMS states — 16 state theo DOM-002 §2 map đúng nhóm màu FE-DS-001 §2.1, kèm icon/label (không chỉ màu — FE-DS-001 §2.5). |
| Integration | Flows với mock API | Mock/response lấy từ OpenAPI examples và `contracts/fixtures/` (§2), không tự bịa payload. |
| Contract | Generated client vs `contracts/api/openapi.yaml` | Client PHẢI fail khi response thiếu required field (ví dụ `Readiness` thiếu `blocking_reasons`, `ErrorEnvelope` thiếu `correlation_id`); suite chạy lại mỗi khi OpenAPI đổi (CI trigger theo path `contracts/api/**`). |
| Authorization / re-auth | Phase 5 gate bắt buộc | Exit gate Phase 5 yêu cầu nguyên văn "authorization/re-auth tests pass" (master §14, Phase 5). Mọi dangerous action trong master §11.3 phải có test verify flow re-auth tồn tại và không bypass được ở client (FE-SEC-001 §4); mọi role thấy đúng UI theo permission matrix §11.3 (Viewer không thấy nút command, v.v.) — lưu ý UI gating chỉ là UX, test server-side thuộc backend suite (SEC-002 §1). |
| E2E smoke | Với Control API skeleton | Flow đọc health/readiness/projection và một command an toàn end-to-end; xác nhận "dashboard chỉ đọc projection/gửi command qua API, không giữ secret" (master §14 Phase 5 exit gate). |

## 2. Fixtures

- Dùng chung `contracts/fixtures/` khi áp dụng (ví dụ `submit-order.v1.valid.json`, `ai-provider-connection.*.v1.valid.json`, `control-command.v1.valid.json`) — fixture là immutable/có checksum theo master §13.4.
- UI fixture bổ sung phải mirror đúng OpenAPI components (schema names/required fields), không fork schema riêng cho frontend.
- **Không fixture nào chứa secret**; recorded response phải redaction theo quy tắc chung: "Recorded venue fixture phải redaction secret/account detail, có source/version/checksum và không tự refresh" (master §13.4). Với BYOK: fixture không được chứa key/hash/fingerprint dưới bất kỳ dạng nào (ARC-AI-001 §8; SEC-001 T-013).

## 3. Error-path coverage bắt buộc

Mỗi error code trong C-ERR-001 §2 (`contracts/errors/error-catalog.md`) có **ít nhất 1 test** verify hành vi UI đúng như FE-API-001 §8 quy định. Tối thiểu:

- `retryable=false` ⇒ **không render nút retry** (envelope field `retryable`, C-ERR-001 §1; "a `retryable` response never authorizes blind external submit retry", C-ERR-001 §3);
- `correlation_id` luôn hiển thị và copy được (FE-DS-001 §3.3);
- `remediation_hint` hiển thị trong error state (FE-DS-001 §5.1);
- `KILL_SWITCH_ACTIVE` (423) ⇒ banner theo FE-DS-001 §2.3, không auto-retry;
- `EXTERNAL_OUTCOME_UNKNOWN` / `AI_OUTCOME_UNKNOWN` (409) ⇒ copy dùng từ "reconcile", không "retry" (glossary §7);
- `AUTHENTICATION_REQUIRED` (401) ⇒ điều hướng re-authenticate, xóa state nhạy cảm theo FE-SEC-001 §3;
- `AI_ENROLLMENT_NOT_PERMITTED` (409) ⇒ chỉ đọc status, không resubmit key (ARC-AI-001 §5.1, FE-SEC-001 §5);
- `SENSITIVE_INPUT_REJECTED` (400) ⇒ hiển thị yêu cầu gỡ secret-like text khỏi reason (FE-SEC-001 §2.4).

Suite này fail khi error catalog thêm code mới mà chưa có test tương ứng (exhaustiveness check trên danh sách code v1).

## 4. Determinism

Khớp triết lý NFR-DET-001 ("Fixture pin UTC, locale, Decimal context, seed và data/version checksum" — NFR §1; master §13.4: test không có "network, clock thật, global random, locale"):

- Golden/widget tests pin font, locale, screen size và seed — kết quả render phải reproducible trên mọi máy/CI.
- **Clock inject** cho mọi logic age/relative-time (FE-DS-001 §3.2): test dùng fixed clock, không `DateTime.now()` trực tiếp trong code hiển thị.
- Không network thật trong unit/widget/golden test; integration dùng mock API từ fixtures (§2).

## 5. Evidence

Kết quả test run là gate evidence Phase 5, ghi theo mẫu evidence của `docs/governance/` (xem `docs/governance/evidence/tasks/0.1/README.md`): "command/procedure, UTC timestamp, runner/version, exit code, artifact path/hash, quyết định reviewer và gate link. Không lưu secret, credential... hoặc log chưa redaction". Tối thiểu mỗi run ghi: đường dẫn artifact, hash, runner (Flutter/Dart version), UTC timestamp. Gate record theo template `docs/governance/templates/gate-record.md` và điều kiện exit gate Phase 5 (master §14): authorization/re-auth tests pass, dashboard không giữ secret, actor/audit trail cho dangerous action có evidence.

## 6. Tooling (DRAFT — cần Account Owner phê duyệt)

| Mục | Đề xuất DRAFT |
|---|---|
| Test framework | `flutter_test` (built-in) |
| Golden | `golden_toolkit` hoặc built-in goldens của `flutter_test` — chọn một, ghi ADR/task khi chốt |
| Mocking | `mocktail` |
| Coverage floor | **70% cho state/application layer** — thấp hơn baseline backend "domain core từ 80% trở lên" (master §13.4) vì widget/render code khó đạt coverage ý nghĩa; DRAFT cần duyệt. Coverage không thay thế các suite bắt buộc §1/§3 (khớp nguyên tắc master §13.4: "Coverage không thay thế invariant test"). |

Mọi dependency test mới theo quy trình CONTRIBUTING §3 (Task ID, license/security review, locked version, test đi kèm) — áp dụng cho pub packages như FE-SEC-001 §6.

## Nhật ký thay đổi

| Ngày | Phiên bản | Người thực hiện | Phê duyệt | Nội dung |
|---|---|---|---|---|
| 2026-07-31 | 0.1.0 | Technical Operator | Pending | Khởi tạo frontend testing strategy: test pyramid (unit/widget/golden/integration/contract/authorization-re-auth/e2e), fixture rules dùng chung contracts/fixtures, error-path coverage bắt buộc theo C-ERR-001, determinism theo NFR-DET-001, evidence Phase 5 và tooling DRAFT với coverage floor 70%. |
