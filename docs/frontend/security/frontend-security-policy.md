# FE-SEC-001 — Frontend security policy (Flutter dashboard)

| Thuộc tính | Giá trị |
|---|---|
| Document ID | FE-SEC-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | DRAFT |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực — chờ Account Owner phê duyệt |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §11.3–§11.5, §12.1; [SEC-002](../../backend/security-ops/access-control-matrix.md); [SEC-003](../../backend/security-ops/auth-session-policy.md); [SEC-001](../../backend/security-ops/threat-model.md); [ARC-AI-001](../../backend/architecture/ai-provider-byok-architecture.md) §3, §5.1; [C-ERR-001](../../../contracts/errors/error-catalog.md); [CONTRIBUTING](../../../CONTRIBUTING.md) §3 |
| Related requirements | NFR-SEC-001, NFR-SAFE-001, NFR-AUD-001; SEC-AUTH-001, SEC-AI-002, SEC-AI-003 |
| Related ADR | ADR-0015 (auth provider/session — blocker), ADR-0016 (BYOK — blocker Phase 6) |

> Policy này ràng buộc mọi code Flutter dashboard. Nó không quyết định auth provider, token format hay session model — các quyết định đó thuộc OD-006/ADR-0015 (SEC-003 §1). Mọi lựa chọn implementation đánh dấu DRAFT — cần Account Owner phê duyệt.

## 1. Nguyên tắc: client không bao giờ là ranh giới bảo mật

- Mọi authorization là server-side: "Authorization is evaluated server-side for every command and data scope. A dashboard/client claim never grants access by itself" (SEC-002 §1). "Client-only authorization" bị cấm tuyệt đối (SEC-003 §2).
- UI gating (ẩn/disable nút theo role) chỉ là UX để giảm lỗi thao tác — **không phải security control**. Server luôn phải từ chối request ngoài quyền bất kể UI đã render gì; "One check never replaces another" (SEC-001 §4).
- Dashboard "chỉ gọi Control API" (master §12.3) và "không giữ secret hoặc logic risk/execution" (master §11.5). Không gọi venue, database hay provider trực tiếp (SEC-001 §4: "AI/UI never calls venue directly").

## 2. Secret rules

1. **KHÔNG secret/token/key** trong: source code, localStorage/sessionStorage, log, error report, screenshot tự động, analytics/telemetry — theo master §12.1: "Secret ở approved secret provider/injection; không commit, log, trace, **UI, browser storage**, DB/manifest/fixture/evidence hoặc prompt".
2. **BYOK `api_key` (Phase 6):** chỉ tồn tại trong memory của form đúng lúc nhập; gửi đúng **một lần** qua enrollment route cô lập (ARC-AI-001 §5.1); zeroize/xóa state ngay sau submit (tương tự nghĩa vụ zeroize của binding lease, ARC-AI-001 §5.3). Cụ thể:
   - dùng obscured/password field, tắt autofill, autocorrect và mọi cơ chế đưa giá trị vào clipboard-history/keyboard suggestion;
   - không đưa field value vào crash report, state restoration, navigation argument, log widget-tree;
   - không tính hash/fingerprint phía client — enrollment "uses no Idempotency-Key, body hash or key fingerprint" (ARC-AI-001 §5.1; T-013 SEC-001 §3).
3. **Session artifact không persist vào browser local storage** khi ADR-0015 chưa đánh giá threat/control: "Session artifacts must be transport-protected, not persist in browser local storage unless ADR-0015 evaluates the threat/control, and never appear in telemetry/evidence" (SEC-003 §3).
4. Free-text reason/note không được dùng để truyền credential; client validate chặn secret-like input trước khi gửi (server sẽ reject bằng `SENSITIVE_INPUT_REJECTED`, C-ERR-001 §2; SEC-003 §5: "Secret-like text in reason/note is rejected before audit persistence").

## 3. Session & CSRF

Theo SEC-003 (provider-neutral, chi tiết chốt ở ADR-0015):

- **Cookie-based session ⇒ CSRF protection bắt buộc**; bearer/token flow cần replay, audience và storage controls do ADR-0015 quyết (SEC-003 §3).
- **Idle timeout/expiry:** UI hiển thị cảnh báo trước khi session hết hạn để operator chủ động re-authenticate; giá trị TTL là field bắt buộc của ADR-0015 (SEC-003 §3), client không tự đặt.
- **Logout** xóa toàn bộ state nhạy cảm phía client: session artifact, cached projection chứa account detail, form state; khớp yêu cầu revocation/logout propagation của SEC-003 §3.
- **Không dùng role cache để enable dangerous action:** "Authorization is evaluated on each dangerous command and at session/token renewal; a cached dashboard permission is insufficient" (SEC-003 §3). Trước mỗi dangerous action, UI phải re-check quyền qua server (và server tự enforce lần nữa); trạng thái enable/disable của nút không được lấy từ role cache cũ.
- Default deny: khi không xác định được trạng thái session/quyền, UI hiển thị trạng thái chưa xác thực và không cho gửi command (SEC-003 §3 default-deny).

## 4. Dangerous action UX

Danh sách action cần re-auth (master §11.3 permission matrix; SEC-003 §4):

| Action | Role tối thiểu (master §11.3) |
|---|---|
| Release kill switch | Risk Approver + Account Owner |
| Approve pending risk intent | Risk Approver |
| Change risk policy/deployment | Risk Approver + Account Owner theo scope |
| Approve canary | Account Owner + Risk Approver |
| Rotate credential/topology | Security/Backup Owner |
| Tạo/enroll/rotate/revoke AI connection (Phase 6) | Account Owner |
| Validate/activate AI connection, thay egress/budget policy (Phase 6) | Account Owner + Security/Backup Owner |
| Emergency suspend/revoke AI connection ngoài scope (Phase 6) | Security/Backup Owner |

Flow chuẩn (mọi dangerous action):

1. **Confirm dialog** nêu rõ hậu quả và scope (target scope là thành phần bắt buộc của re-auth proof, SEC-003 §4);
2. **Re-auth** — proof bound vào actor, action class, target scope, issued/expiry time và correlation ID, không replay được cho action khác (SEC-003 §4);
3. **Submit** command với idempotency key, actor, reason, correlation ID (master §11.3: "Mọi command nguy hiểm phải có idempotency key, actor, reason, correlation ID và audit before/after hash");
4. **Async command tracking** — hiển thị trạng thái command đã accept (theo `CommandAccepted` trong `contracts/api/openapi.yaml`), không giả định thành công đồng bộ.

**Audit reason bắt buộc nhập** cho mọi action có cột "Audit reason: có" (master §11.3); client validate chống secret-like input trước khi gửi (§2.4, C-ERR-001 `SENSITIVE_INPUT_REJECTED`). Nếu re-auth fail/expired/uncertain: hiển thị lỗi authorization an toàn, không lưu proof, không auto-retry (SEC-003 §4).

## 5. BYOK UI (Phase 6)

Tuân thủ nguyên văn ARC-AI-001 §3, dòng "Dashboard" trong bảng component:

> Allowed: "Display catalog/policy-profile/connection metadata; collect a key only through dedicated secure enrollment UI."
> Forbidden: "Store key in local/session storage, display/read back key, call provider directly."

Quy tắc triển khai:

- **Enrollment cookie là HttpOnly, server-managed** — "Control API creation returns a short-lived Secure/HttpOnly/SameSite cookie scoped only to the isolated enrollment path; browser JavaScript cannot read it" (ARC-AI-001 §5.1). Client code không đọc, không lưu, không đính kèm thủ công cookie này.
- **Mất response ⇒ chỉ đọc status, không resubmit:** "If the client loses a response, it reads safe connection status and never automatically posts a key again" (ARC-AI-001 §5.1); server enforce bằng `AI_ENROLLMENT_NOT_PERMITTED` (C-ERR-001 §2: "do not automatically resubmit a key").
- **Không hiển thị fingerprint/độ dài key** hay bất kỳ dẫn xuất nào của key — enrollment không tạo "body hash or key fingerprint" (ARC-AI-001 §5.1; test bắt buộc §8: "no key or key hash/fingerprint in ... browser storage").
- UI chỉ hiển thị safe metadata: connection lifecycle state (10 state, ARC-AI-001 §4.2), masked label, provider/model/policy-profile ID — và không gọi các metadata này là "API key" (glossary §7).
- Connection ngoài owner scope: không suy diễn/hiển thị sự tồn tại — server trả `AI_CONNECTION_SCOPE_DENIED` 403/404 không lộ resource state (C-ERR-001 §2; SEC-003 §5).

## 6. Content security

- **CSP cho web build** (nếu deploy web): `connect-src` chỉ Control API origin; không cho phép origin khác — dashboard "chỉ gọi Control API" (master §12.3). DRAFT — cấu hình cụ thể chốt cùng ADR-0015/topology.
- **Certificate pinning cân nhắc cho mobile build** (DRAFT — cần Account Owner phê duyệt, phụ thuộc topology ADR): transport phải authenticated theo master §12.2 ("remote API/telemetry dùng transport được xác thực").
- **Không third-party analytics/CDN/font service** trong dashboard vận hành — tránh kênh egress dữ liệu ngoài Control API và giảm supply-chain surface (master §12.2; SEC-001 T-010).
- **Dependency frontend** (pub package) theo cùng quy trình review backend: "Dependency mới cần: Task ID cho phép, lý do ghi rõ, license/security review, locked version..., và test đi kèm" (CONTRIBUTING §3); lock file pinning theo master §12.2.

## 7. Threat mapping (client-side controls)

Map các threat liên quan từ SEC-001 (`docs/backend/security-ops/threat-model.md` §3) sang control phía client. Control client là lớp bổ sung, không thay control server (SEC-001 §4.5).

| Threat (SEC-001) | Mô tả | Control phía client |
|---|---|---|
| T-008 | Dashboard session theft / CSRF | Không persist session artifact ngoài phạm vi ADR-0015 cho phép (§2.3); cảnh báo expiry + logout xóa state (§3); re-auth cho dangerous action (§4); không đưa session artifact vào log/telemetry (SEC-003 §3) |
| T-013 | BYOK enrollment leak (raw key/body hash/fingerprint trong log/browser/proxy/…) | Toàn bộ §5: key chỉ trong memory form, một lần submit, zeroize, không hash/fingerprint client-side, không lưu browser storage, không resubmit khi mất response |
| T-017 | Control API DoS/resource exhaustion, "kể cả vô ý từ script lỗi (retry loop, runaway client)" | Client không retry storm: chỉ retry khi `retryable=true` và theo policy (C-ERR-001 §3: "a `retryable` response never authorizes blind external submit retry"); backoff có giới hạn; không polling vô hạn tần suất cao; 423/409 (`KILL_SWITCH_ACTIVE`, `EXTERNAL_OUTCOME_UNKNOWN`) không bao giờ auto-retry |

Liên quan gián tiếp: T-002 (unauthorized command) — client hỗ trợ bằng §1/§4 nhưng control chính là server-side RBAC/re-auth/audit (SEC-001 §3).

## Nhật ký thay đổi

| Ngày | Phiên bản | Người thực hiện | Phê duyệt | Nội dung |
|---|---|---|---|---|
| 2026-07-31 | 0.1.0 | Technical Operator | Pending | Khởi tạo frontend security policy: client không là ranh giới bảo mật, secret rules (kể cả BYOK api_key in-memory-only), session/CSRF theo SEC-003, dangerous action UX theo master §11.3, BYOK UI theo ARC-AI-001 §3/§5.1, content security và threat mapping T-008/T-013/T-017. |
