# FE-CHARTER-001 — Frontend Charter (Flutter Dashboard)

| Thuộc tính | Giá trị |
|---|---|
| Document ID | FE-CHARTER-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | DRAFT |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực — đây là input thiết kế cho Phase 5/6, không cho phép bất kỳ implementation nào trước các gate đó |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §2.3, §3.4, §3.5, §11.2, §11.3, §11.4, §11.5, §14 (Phase 5, Phase 6); contracts/api/openapi.yaml v1.1.0-draft; docs/backend/security-ops/access-control-matrix.md (SEC-002); docs/backend/security-ops/slo-sli-alert-policy.md (OPS-001) §4.2 |
| Related requirements | FR-OPS-001, NFR-SEC-001, NFR-OPS-001, NFR-AUD-001; FR-FE-001..FR-FE-007 (DRAFT, đề xuất trong tài liệu này) |
| Related ADR | ADR-0014, ADR-0015 (DRAFT — auth provider chưa chốt), ADR-0016 (Phase 6 BYOK) |

> **Cảnh báo phạm vi:** Tài liệu này là đặc tả sản phẩm frontend ở trạng thái DRAFT, dùng làm input cho Phase 5 (dashboard core) và Phase 6 (BYOK UI). Nó **không cho phép viết code Flutter/Dart**, không cho phép tạo route API mới, không thay đổi contract backend. "Full Flutter dashboard" nằm ngoài phạm vi MVP (master §2.3) và Dart/Flutter chỉ được dùng "dashboard Phase 5 trở đi, chỉ qua Control API... không trước gate Phase 5" (master §3.5). Mọi câu quy phạm trong tài liệu này đều phải truy vết được về backend contract/master spec; nguồn được trích dẫn inline.

## 1. Mục đích và phạm vi

### 1.1 Dashboard là gì

Flutter dashboard **chỉ là một client của Control API** (master §11.5). Năm quy tắc nền tảng, trích nguyên gốc từ master §11.5:

1. Hiển thị **mode thật**, health, order/position/PnL, incident, reconciliation.
2. Gửi command **qua API theo quyền**.
3. Confirm/re-auth cho **action nguy hiểm**.
4. **Mất kết nối dashboard không ảnh hưởng trading node.**
5. **Không giữ secret hoặc logic risk/execution.**

Bổ sung từ master §3.4: dashboard không chứa secret, không gọi sàn trực tiếp và không chứa business logic; Streamlit (nếu dùng) chỉ là công cụ research read-only tạm thời, không phải control plane production.

### 1.2 Read-only client + user-rights passthrough (reconciliation với SEC-002)

SEC-002 §3 khai báo machine identity `dashboard` là "Read-only API client (Phase 5); displays metadata according to the authorization of the authenticated user session", với explicit deny: "DB role, venue credential, any secret, write/command path of its own". Điều này **không mâu thuẫn** với master §11.5 "gửi command qua API theo quyền" — cách đọc thống nhất (normative cho frontend):

- **Tiến trình dashboard** (app/process) không có standing credential, không có write path **của riêng nó**, không có DB role, không có venue credential, không có secret (SEC-002 §3 row `dashboard`).
- Mọi command mà UI gửi đi là **quyền của human actor đã xác thực** được pass through và đánh giá server-side, giống mô hình `cli` "caller identity passthrough only" (SEC-002 §3 row `cli`). Command là quyền của **user**, không phải của **app**.
- "A dashboard/client claim never grants access by itself" — authorization luôn được đánh giá server-side cho mọi command và data scope (SEC-002 §1).

### 1.3 Dashboard không là gì

- Không phải trading engine, không phải risk engine, không phải nơi đặt lệnh thủ công — **manual order endpoint không tồn tại trong MVP** (master §11.2: "Manual order endpoint không có trong MVP").
- Không phải nguồn sự thật: mọi dữ liệu hiển thị là **sanitized projection** do Control API trả về (master §11.1: control plane cung cấp "read projection cho dashboard/API" và "không trả secret raw").
- Không phải một thành phần mà trading path phụ thuộc: "UI không được chặn trading path" (master §3, bảng quyết định, hàng UI).
- Không truy cập database, không truy cập venue, không lưu secret trong browser/app storage (master §12.1: secret không được xuất hiện ở "UI, browser storage"; SEC-002 §3).

## 2. Người dùng và role

### 2.1 Bảng role và những gì UI cho phép thấy/làm

Nguồn: permission matrix master §11.3 + SEC-002 §2 (human action matrix). UI chỉ là lớp trình bày của matrix này; server luôn là nơi cưỡng chế.

| Role | UI cho phép THẤY | UI cho phép LÀM (gửi command) | Re-auth |
|---|---|---|---|
| Viewer | Health/readiness, sanitized projection (order/fill/portfolio/audit/incident), AI provider/model catalog trong owner scope (master §11.3; SEC-002 §2) | Không có command nào | — |
| Technical Operator | Như Viewer + operations views | Request reconciliation; activate kill switch; activate/stop paper strategy (master §11.3) | Không (kill-switch activate: "không, nhưng actor xác thực" — master §11.3) |
| Risk Approver | Như Viewer + pending approval/risk views | Approve pending risk intent; cùng Account Owner: release kill switch, change risk policy/deployment, approve canary (master §11.3) | Có cho mọi action liệt kê (master §11.3) |
| Account Owner | Như Viewer + AI connection metadata own scope (SEC-002 §2) | Cùng Risk Approver: release kill switch, approve canary; tạo/enroll/rotate/suspend/revoke AI connection own scope; cùng Security/Backup Owner: validate/activate AI connection (master §11.3) | Có cho mọi action liệt kê (master §11.3) |
| Security/Backup Owner | Như Viewer + security/backup/credential views | Rotate credential/topology; cùng Account Owner: validate/activate AI connection; emergency suspend/revoke AI connection ngoài scope đang thao tác (kèm Account Owner notification/review sau containment) (master §11.3) | Có (master §11.3) |

Ghi chú: "Security/Backup Owner may suspend/revoke an AI connection but cannot read its key" và "No role has... raw secret/key read" (SEC-002 §2). UI **không bao giờ** có màn hình hiển thị raw key cho bất kỳ role nào.

### 2.2 Nguyên tắc capability gating (normative)

1. UI **ẩn hoặc disable** action theo role của session hiện tại để giảm lỗi thao tác — đây chỉ là UX affordance.
2. **Authorization LUÔN được đánh giá server-side** cho mọi command và data scope; "a dashboard/client claim never grants access by itself" (SEC-002 §1). Client claim, local state hay feature flag phía client **không bao giờ tự cấp quyền**.
3. UI phải xử lý được `401 AUTHENTICATION_REQUIRED` / `403 AUTHORIZATION_DENIED` ở **mọi** call, kể cả khi UI tưởng rằng action được phép — vì server là thẩm quyền cuối (SEC-002 §4: "Authorization failures return the standard safe envelope; never reveal another account/resource existence").
4. Dangerous action (release kill switch, approve canary, thay risk policy, credential rotation, AI validate/activate/...) cần re-auth proof theo ADR-0015 provider tương lai; "Không có action high-risk nào chỉ dựa vào UI confirmation" (master §11.4). UI confirmation dialog là bổ trợ, không thay thế re-auth server-side.
5. Một người có thể giữ nhiều role pre-canary, nhưng audit ghi role hành động riêng biệt (master §11.4; SEC-002 §1) — UI phải cho actor chọn/hiển thị rõ role đang dùng cho action, không gộp.

## 3. Phase gating

### 3.1 Phase 5 — dashboard core

Master §14, Phase 5 ("Control plane và dashboard"): "Chỉ thực hiện sau paper/canary ổn định. Auth/RBAC tối thiểu đã bắt buộc ở Phase 3". Deliverables: Flutter dashboard; incident/audit/reconciliation/deployment view; dangerous-action re-auth và authorization tests.

**Exit gate Phase 5 (nguyên văn master §14):**

> "dashboard chỉ đọc projection/gửi command qua API, không giữ secret; mất dashboard không ảnh hưởng trading node; authorization/re-auth tests pass; actor/audit trail cho toàn bộ dangerous action có evidence."

### 3.2 Phase 6 — BYOK UI

Master §14, Phase 6: BYOK connection UI (user chọn provider/model/policy profile đã duyệt; create/rotation command không chứa key; isolated secret ingress enroll write-only candidate key; validate với synthetic/sanitized probe rồi activate atomically). Chỉ thực hiện khi ADR-0008 và ADR-0016 `APPROVED`, OD-008 `RESOLVED`, auth/machine identity và secret-provider topology được phê duyệt (master §14 Phase 6, điều kiện vào).

### 3.3 Quy tắc bắt đầu

- **Không viết code frontend trước khi có Phase 5 task card ở trạng thái READY** theo quy trình task card/gate của master §14.2 và §16. Master §14.1: "Không bỏ qua bước để làm UI, AI hoặc kết nối sàn sớm."
- Auth provider/session model là OD-006 + ADR-0015, hiện DRAFT ("provider/session choice unresolved" — docs/backend/adr/0015-authentication-session-machine-identity.md). Mọi thiết kế đăng nhập/re-auth trong tài liệu frontend là **placeholder** cho đến khi ADR-0015 APPROVED.
- Route API chỉ được dùng ở phase có quyền tương ứng: "health/read-only từ Phase 0, backtest/reconciliation theo Phase 2–3, action strategy/kill switch theo phase runtime và AI provider connection từ Phase 6" (master §11.2).

## 4. Yêu cầu chức năng frontend (FR-FE — DRAFT)

Bảng dưới là **đề xuất DRAFT**, cần Account Owner phê duyệt và sau đó cập nhật `docs/governance/requirements-traceability.md`. ID không được đổi meaning sau khi implementation dùng (quy tắc master §2.2).

| ID | Tên | Mô tả | Acceptance criteria (kiểm được) | Nguồn backend |
|---|---|---|---|---|
| FR-FE-001 | Runtime/mode/health thật | Hiển thị environment, run_mode, execution_target, safe_state, manifest_hash, deployment_id từ projection thật; **không dùng cache để che giấu trạng thái thật** | (a) Màn hình Overview render đủ các field required của schema `Runtime`; (b) khi `safe_state != READY` hiển thị banner cảnh báo; (c) dữ liệu cache phải có nhãn stale + timestamp `observed_at`, không bao giờ hiển thị như dữ liệu tươi; (d) mất kết nối hiển thị trạng thái mất kết nối, không hiển thị giá trị cũ như hiện hành | GET /runtime, /readiness, /health (openapi.yaml, schemas Runtime/Readiness/Health); master §11.5 "hiển thị mode thật" |
| FR-FE-002 | Order/position/PnL/fill views | Xem order detail + timeline bất biến, fills, portfolio snapshot | (a) Order detail render đủ 16 state và `terminal_reason` (openapi.yaml schema Order); (b) timeline dùng cursor pagination, không offset (master §11.2); (c) quantity/price/fee render từ DecimalString, không qua float; (d) portfolio snapshot hiển thị `as_of_at` + `source_hash`; 423 `RECONCILIATION_BLOCKED`/OperationBlocked được render là trạng thái blocked, không phải lỗi chung | GET /orders/{order_id}, /orders/{order_id}/timeline, /fills, /portfolio/snapshot (openapi.yaml); DOM-002 §2 |
| FR-FE-003 | Incident/reconciliation/audit views | Xem incident (severity/status), audit events bất biến, trạng thái reconciliation | (a) Incident list filter được theo severity CRITICAL/HIGH/MEDIUM/LOW và status OPEN/MITIGATING/RESOLVED/CLOSED (openapi.yaml schema Incident); (b) audit event hiển thị actor/action/before_hash/after_hash (schema AuditEvent); (c) cursor pagination; (d) đây là deliverable Phase 5 "incident/audit/reconciliation/deployment view" (master §14 Phase 5) | GET /incidents, /audit-events, /deployments/{deployment_id} (openapi.yaml) |
| FR-FE-004 | Command submission + async tracking | Gửi command theo quyền của actor; theo dõi lifecycle async | (a) Mọi POST command gửi Idempotency-Key (trừ credential-enrollments — master §11.2); (b) sau 202, UI theo Location header đến /commands/{command_id} và render lifecycle ACCEPTED→RUNNING→SUCCEEDED/FAILED/CANCELLED (master §11.2; openapi.yaml CommandStatus); (c) retry một submission dùng lại đúng Idempotency-Key cũ, không sinh key mới; (d) 409 IDEMPOTENCY_KEY_REUSED được xử lý bằng cách đọc command gốc, không auto-resubmit payload mới | POST /commands/* + GET /commands/{command_id} (openapi.yaml); master §11.2 |
| FR-FE-005 | Dangerous-action re-auth flow | Flow re-auth cho action nguy hiểm, có reason + audit | (a) Các route yêu cầu `ReauthenticationProof` (kill-switch-releases, toàn bộ AI lifecycle — openapi.yaml) không thể gửi từ UI khi thiếu proof; (b) UI bắt buộc nhập reason; secret-like input trong reason bị server reject (SEC-002 §4) và UI hiển thị lỗi tương ứng; (c) release kill switch yêu cầu `verification_evidence_ref` (openapi.yaml KillSwitchReleaseCommandRequest); (d) authorization/re-auth tests pass là điều kiện exit gate Phase 5 (master §14) | master §11.3, §11.4; SEC-002 §2, §4; openapi.yaml parameter ReauthenticationProof |
| FR-FE-006 | Mandatory ops views | Các view vận hành bắt buộc trước testnet | Hiển thị đủ 7 nhóm theo OPS-001 §4.2: UNKNOWN orders + tuổi từng order; reconciliation queue/case đang mở; lease/leader state; outbox/inbox/DLQ backlog (count + age); kill-switch state theo từng scope; backup age + last restore drill; AI budget/egress (Phase 6). "Thiếu view bắt buộc là gap đối với testnet gate evidence" (OPS-001 §4.2). Xem GAP register trong FE-SCREEN-001: một số view chưa có route trong OpenAPI v1.1 | OPS-001 §4.2 (DRAFT — cần phê duyệt) |
| FR-FE-007 | BYOK connection management (Phase 6) | UI quản lý AI provider connection theo owner scope | (a) Catalog/model/policy-profile browser chỉ hiển thị entry đã duyệt (openapi.yaml /ai/providers, /ai/providers/{provider_id}/models, /ai/policy-profiles); (b) connection list/detail render đủ 10 status (openapi.yaml AIProviderConnection.status); (c) key entry là write-only một lần, không read-back, không hiển thị lại, mất response thì đọc status chứ **không** resubmit key (openapi.yaml credential-enrollments description; master §11.2); (d) validate/activate hiển thị yêu cầu dual-role Account Owner + Security/Backup Owner (SEC-002 §2); (e) không tồn tại UI đọc raw key cho bất kỳ role nào (SEC-002 §2) | contracts/api/openapi.yaml (12 route /ai/*); master §14 Phase 6; ADR-0016; SEC-002 §2 |

## 5. Không thuộc phạm vi

| Hạng mục | Lý do / nguồn |
|---|---|
| Manual-order UI (đặt/hủy/sửa lệnh thủ công) | Không có endpoint: "Manual order endpoint không có trong MVP. Nếu thêm sau này phải đi qua exact risk flow, `ClientOrderId`, approval và quyền high-risk riêng" (master §11.2). UI không được vẽ trước một capability backend không có |
| Chart/TA nâng cao (candlestick, indicator overlay, drawing tools) | Ngoài MVP; không có route market-data chart trong openapi.yaml v1.1; nếu cần sau này phải bổ sung contract + ADR theo master §2.4 |
| Notification push (mobile push/email/webhook từ dashboard) | Chưa có contract; notification channel/escalation roster là OD-005, "No alert integration is created by this draft" (OPS-001 §4) |
| Đa ngôn ngữ | MVP chọn **một** ngôn ngữ UI: **tiếng Việt** (thuật ngữ kỹ thuật giữ tiếng Anh, nhất quán với glossary docs/shared/glossary.md). i18n framework là scope mở rộng sau, cần quyết định riêng |
| Offline mode | Không có offline mode ngoài read-cache **có nhãn stale rõ ràng** (kèm timestamp nguồn). Không cache secret/token vượt session policy (master §12.1); không queue command offline để phát lại — command chỉ được gửi khi online với Idempotency-Key (master §11.2) |
| Direct venue/DB access, secret storage, risk/business logic phía client | Cấm tuyệt đối theo master §3.4, §3.5 (hàng Dart/Flutter), §11.5 và SEC-002 §3 |

## Nhật ký thay đổi

| Ngày | Phiên bản | Người thực hiện | Phê duyệt | Nội dung |
|---|---|---|---|---|
| 2026-07-31 | 0.1.0 | Technical Operator | Pending | Khởi tạo frontend charter DRAFT: 5 quy tắc §11.5 + reconciliation với SEC-002 dashboard row; bảng role/capability gating; phase gating Phase 5/6 với gate conditions nguyên văn; FR-FE-001..007 DRAFT; danh mục ngoài phạm vi. Không cho phép implementation trước Phase 5 gate |
