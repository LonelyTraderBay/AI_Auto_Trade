# Flutter App Architecture — thin client cho Control API

| Thuộc tính | Giá trị |
|---|---|
| Document ID | FE-ARC-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | DRAFT |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực — chờ Account Owner phê duyệt và Phase 5 task card READY |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §1.5, §3.4, §4.8, §5.8, §11.2, §11.3, §11.5, §12.1; `contracts/api/openapi.yaml` (C-API-001 v1.1.0-draft); `contracts/errors/error-catalog.md` (C-ERR-001 v1.1); SEC-003 (`docs/backend/security-ops/auth-session-policy.md`); NFR (`docs/shared/product/non-functional-requirements.md`) |
| Related requirements | FR-OPS-001, FR-AI-001; NFR-SAFE-001, NFR-SEC-001, NFR-OPS-001, NFR-AI-001 |
| Related ADR | ADR-0014, ADR-0015 (pending), ADR-0016 |

> **Phạm vi hiệu lực:** Tài liệu này là hồ sơ kiến trúc DRAFT cho Flutter dashboard Phase 5+. Nó KHÔNG cho phép bất kỳ implementation, scaffold, package install hay code generation nào trước khi Phase 5 task card tương ứng đạt trạng thái READY theo master §0.2 (Definition of Ready). Mọi lựa chọn công nghệ trong tài liệu này là **DRAFT — cần Account Owner phê duyệt**.

## 1. Nguyên tắc kiến trúc: thin client tuyệt đối

Flutter app là **thin client** của Control API và chỉ là thin client:

- App KHÔNG chứa business logic, risk logic hay execution logic dưới bất kỳ hình thức nào — "Dashboard không chứa secret, không gọi sàn trực tiếp và không chứa business logic" (master §3.4) và "không giữ secret hoặc logic risk/execution" (master §11.5).
- Mọi quyết định (risk check, kill switch, reconciliation, activation gate...) là **server-side**; app chỉ (a) render projection đã sanitize do server trả về và (b) submit command qua Control API theo quyền của user đã xác thực (master §11.5: "hiển thị mode thật, health, order/position/PnL, incident, reconciliation; gửi command qua API theo quyền").
- App KHÔNG gọi venue/sàn trực tiếp và KHÔNG gọi AI provider trực tiếp; process `dashboard` chỉ có quyền "chỉ gọi Control API" (master §12.3).
- Không có action high-risk nào chỉ dựa vào UI confirmation (master §11.4); UI confirm dialog chỉ là bước thu thập intent + re-auth proof, quyết định cuối cùng luôn ở server.

Hệ quả bắt buộc: nếu một tính năng đòi hỏi tính toán quyết định phía client (ví dụ "tự tính risk trước khi gửi"), tính năng đó bị từ chối ở mức kiến trúc — phải đề xuất API server-side mới qua quy trình contract change (master §1.5, ADR-0014).

## 2. Layer structure (DRAFT — cần Account Owner phê duyệt)

Ba layer duy nhất, phụ thuộc một chiều từ trên xuống:

~~~text
presentation  (widgets / screens)
    ↓
application   (state notifiers / controllers — orchestration UI state, KHÔNG domain logic)
    ↓
api_client    (generated từ contracts/api/openapi.yaml — xem §4)
~~~

- **presentation**: widgets/screens thuần render; không gọi HTTP, không format quyết định nghiệp vụ.
- **application**: state notifiers/controllers chỉ orchestrate UI state (loading/error/data, polling lifecycle, navigation). KHÔNG chứa domain logic — tương tự tinh thần phân tầng backend "domain/ chỉ chứa logic thuần; application/ đặt use case" (master §4.8), nhưng phía client thì không có layer domain nào cả vì mọi domain logic là server-side (§1).
- **api_client**: client sinh tự động từ OpenAPI (§4). Không có layer nào khác (không "repository", không "service" chứa logic riêng).

**Cấm tuyệt đối** (normative):

1. Gọi HTTP ngoài `api_client` — mọi network call phải đi qua client sinh từ OpenAPI vì `contracts/api/openapi.yaml` là canonical HTTP wire contract duy nhất (master §11.2, §1.5 authority hierarchy).
2. Parse `DecimalString` thành `double`/`float` — wire contract quy định "Base-10 Decimal serialized as string; never JSON number/float" (`openapi.yaml` schema `DecimalString`) và "Money, price, quantity, fee và PnL không dùng float" (master §5.1; NFR §7: "Decimal + NUMERIC(38,18); ... API decimal string"). Client giữ nguyên `String` hoặc dùng package `decimal` — lựa chọn cụ thể là **DRAFT — cần Account Owner phê duyệt**.
3. Tự tính PnL/position/exposure phía client — app chỉ hiển thị giá trị server trả về trong projection (master §3.4, §11.5). Kể cả phép cộng "tổng PnL" từ nhiều dòng cũng không được làm nếu server đã có field tương ứng; thiếu field thì đề xuất contract change, không tự tính.

## 3. State management (DRAFT — cần Account Owner phê duyệt)

**Đề xuất DRAFT: Riverpod.** Lý do: compile-safe (provider được resolve tĩnh), testable (override provider trong test không cần widget tree), không phụ thuộc `BuildContext` cho logic orchestration. **Alternatives được ghi nhận: Bloc, Provider** — quyết định cuối cùng thuộc Account Owner trước Phase 5; đây không phải quyết định đã chốt.

Quy tắc normative (áp dụng bất kể package nào được duyệt):

- Mỗi API resource (readiness, runtime, orders, fills, portfolio snapshot, incidents, audit events, commands, AI catalog/connections — danh mục route theo master §11.2 và `openapi.yaml` `paths`) map vào một provider/notifier riêng; không gom state nhiều resource vào một object god-state.
- **Polling strategy cho command status**: sau khi POST command nhận `202 CommandAccepted`, client poll `GET` theo `Location` header (response `CommandAccepted` trong `openapi.yaml` yêu cầu header `Location` bắt buộc) với **exponential backoff**, và **dừng poll khi command đạt trạng thái terminal** `SUCCEEDED | FAILED | CANCELLED` (lifecycle theo master §11.2 và schema `CommandStatus.status` enum `[ACCEPTED, RUNNING, SUCCEEDED, FAILED, CANCELLED]`). Chi tiết binding tại FE-API-001 §3.
- Không dùng global mutable singleton cho state; mọi state đi qua provider graph để có thể reset/test/scope theo session.

## 4. API client: generated, không viết tay

- API client được **sinh tự động** từ `contracts/api/openapi.yaml` — canonical HTTP wire contract (master §11.2: "contracts/api/openapi.yaml là canonical HTTP wire contract. Không implement route, request field, response field hay status code trước khi OpenAPI và fixture tương ứng được duyệt").
- Toolchain đề xuất: `openapi-generator` với generator `dart-dio` hoặc công cụ tương đương — **DRAFT — cần Account Owner phê duyệt**.
- Generated code đặt trong thư mục `generated/` theo quy tắc generated-artifact của master §4.8: "Generated artifact vào `generated/` hoặc đường dẫn task chỉ định, có banner/source link; không dùng generated file làm nơi sửa tay." Mỗi file generated phải có banner ghi nguồn (OpenAPI version + tool version) và KHÔNG BAO GIỜ được sửa tay.
- Mọi thay đổi API = cập nhật `contracts/api/openapi.yaml` qua quy trình contract governance rồi **regenerate**; không vá tay generated code (master §1.5: contract machine-readable mâu thuẫn thì tạo issue/ADR, không tự sửa code; ADR-0014 contract authority).
- Client PHẢI **fail khi gặp field `required` bị thiếu** trong response — không silent default. Cơ sở: các schema trong `openapi.yaml` khai báo `required` + `additionalProperties: false` (ví dụ `CommandStatus`, `ErrorEnvelope`, `Order`); một response thiếu field required là contract violation và phải hiển thị lỗi an toàn, không "đoán" giá trị — nhất quán với fail-closed behavior (NFR-SAFE-001).

## 5. Session / auth layer (placeholder — bị block bởi OD-006 / ADR-0015)

- Authentication provider, session/token format, MFA và identity lifecycle **chưa được resolve**: OD-006 và ADR-0015 là điều kiện bắt buộc (SEC-003 §1: "Authentication provider, issuer, token/session format, MFA mechanism... are unresolved under OD-006 and require ADR-0015"; `openapi.yaml` securityScheme `ActorAuthentication`: "Provider-neutral placeholder. Authentication/session implementation is blocked by OD-006 and ADR-0015").
- Do đó auth layer trong app là một **interface tách riêng** (ví dụ `AuthSessionPort`): screens/application chỉ phụ thuộc interface; khi ADR-0015 chốt provider, chỉ thay adapter, không đụng screens.
- Token/session artifact **KHÔNG lưu browser localStorage**: SEC-003 §3 quy định session artifacts "not persist in browser local storage unless ADR-0015 evaluates the threat/control, and never appear in telemetry/evidence". Mặc định fail-closed: không lưu cho đến khi ADR-0015 phê duyệt cơ chế lưu trữ cụ thể.
- **Re-authentication proof flow là module riêng**: re-auth bắt buộc cho kill-switch release, AI connection lifecycle và các dangerous action khác (SEC-003 §4; master §11.3). Proof phải "bound to actor, action class, target scope, issued/expiry time and correlation ID; it cannot be replayed for another action" (SEC-003 §4) — module re-auth phát proof cho đúng một action+scope, không cache, không reuse; chi tiết wire tại FE-API-001 §6.
- Token/proof không bao giờ được log (`openapi.yaml` `ActorAuthentication`: "Tokens/proofs must never be logged"; header `X-Reauthentication-Proof`: "must never be logged or echoed").

## 6. Data freshness và mất kết nối

- Mọi projection hiển thị kèm **as-of timestamp** lấy từ field server trả (`observed_at` cho health/readiness/runtime, `recorded_at` cho event/audit, `updated_at` cho projection — hợp đồng timestamp theo master §5.1 và các schema `Health`, `Readiness`, `Runtime`, `OrderTimelineEvent` trong `openapi.yaml`). Người dùng luôn biết dữ liệu "tính đến lúc nào".
- Mất kết nối → hiển thị **banner offline toàn cục** + gắn nhãn **stale** trên mọi dữ liệu cũ đang hiển thị. KHÔNG che giấu tình trạng mất kết nối, không âm thầm hiển thị data cũ như thể đang live — nhất quán với nguyên tắc "hiển thị mode thật" (master §11.5) và auditability (NFR-AUD-001).
- **Dashboard mất kết nối không được ảnh hưởng trading node** (master §11.5: "mất kết nối dashboard không ảnh hưởng trading node"). Hệ quả: không có retry storm từ client — reconnect/poll dùng **backoff có jitter**, số lần và trần thời gian theo policy vận hành được duyệt; client không bao giờ coi việc "gọi dồn dập cho nhanh" là chấp nhận được.
- `safe_state != READY` (tức `BLOCKED | FROZEN | KILL_SWITCH_ACTIVE` theo enum `Readiness.safe_state` / `Runtime.safe_state` trong `openapi.yaml`) → hiển thị **banner cảnh báo toàn cục** trên mọi màn hình, kèm `blocking_reasons` từ `Readiness.blocking_reasons`.

## 7. Cấu trúc thư mục Flutter đề xuất (DRAFT — cần Account Owner phê duyệt)

~~~text
lib/
  screens/        # presentation: màn hình
  widgets/        # presentation: widget tái sử dụng
  state/          # application: notifiers/controllers (UI orchestration only)
  api/
    generated/    # api_client sinh từ contracts/api/openapi.yaml — banner, không sửa tay (master §4.8)
  auth/           # session/auth interface + re-auth proof module (placeholder chờ ADR-0015, §5)
  theme/          # design tokens / theming
  l10n/           # localization
test/             # tests mirror cấu trúc lib/ theo tinh thần "test mirror source/capability" (master §4.8)
  screens/...
  state/...
  api/...
~~~

## 8. Ràng buộc phase và open decision

- Flutter dashboard thuộc **Phase 5+**; hiện tại hệ thống là API/CLI-first (master §3.4: "Phase đầu: CLI và FastAPI control endpoints. Flutter là dashboard mục tiêu ở phase sau"; `docs/frontend/README.md`).
- Tài liệu này và FE-API-001 KHÔNG cho phép implementation trước khi Phase 5 task card đạt READY (master §0.2); chúng chỉ cố định ràng buộc kiến trúc để task card Phase 5 viết trên nền đã duyệt.
- **Open decision — vị trí repo frontend** (DRAFT, cần owner quyết định trước Phase 5): đề xuất (a) cùng monorepo dưới `frontend/` (ưu điểm: cùng contract source `contracts/`, cùng CI governance) hoặc (b) repo riêng (ưu điểm: toolchain Dart/Flutter tách khỏi Python backend). Chưa có quyết định; ghi nhận là open decision theo cơ chế Open Decision Register (master §0.3) và phải được Account Owner chốt trước khi Phase 5 task card đầu tiên được viết.
- Các quyết định DRAFT đang chờ Account Owner phê duyệt trong tài liệu này: state management package (§3), cách biểu diễn Decimal phía client (§2), codegen toolchain (§4), cấu trúc thư mục (§7), vị trí repo (§8).

## 9. Dart code-quality gates (DRAFT — open item Phase 5)

Backend đã có ngân sách chất lượng cưỡng chế bằng tooling (ENG-PY-001 §5a/§5b); phía Dart/Flutter chưa có tương đương — đây là **open item bắt buộc đóng khi viết Phase 5 task card đầu tiên**, không được để trống như hiện trạng. Đề xuất baseline (DRAFT, cần Account Owner phê duyệt):

- Command profile Dart tương đương master §13.2: `dart format --set-exit-if-changed .`, `flutter analyze` (0 warning), `flutter test` — CI chạy đúng các lệnh local.
- `analysis_options.yaml` pin `flutter_lints` version + bật analyzer strict modes: `strict-casts`, `strict-raw-types`, `strict-inference`; cấm `// ignore:` không kèm reference issue/waiver (tương đương lệnh cấm `noqa` của ENG-PY-001 §3).
- Ngân sách complexity/size và anti-pattern AI áp dụng nguyên tắc ENG-PY-001 §5a/§5b (function ≤ ~50 dòng, không speculative abstraction/wrapper, không dead code, comment không diễn tả lại code); enforcement bằng lint rule Dart tương ứng chọn khi viết task card Phase 5.
- `analysis_options.yaml` là config authority phía Dart, cùng cơ chế kiểm soát nới lỏng như `pyproject.toml` (task card + lý do; waiver nếu đụng safety).

## Nhật ký thay đổi

| Phiên bản | Ngày | Tác giả | Phê duyệt | Nội dung |
|---|---|---|---|---|
| 0.2.0 | 2026-07-31 | Technical Operator | Pending | Thêm §9 Dart code-quality gates (DRAFT): command profile Dart, analyzer strict modes, config authority — đăng ký gap chất lượng phía frontend làm open item Phase 5 thay vì để trống. |
| 0.1.0 | 2026-07-31 | Technical Operator | Pending | Bản DRAFT đầu tiên: nguyên tắc thin client, layer structure, state management, generated API client, auth placeholder, data freshness, cấu trúc thư mục và open decision vị trí repo. |
