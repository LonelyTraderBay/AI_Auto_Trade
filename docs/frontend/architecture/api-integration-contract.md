# API Integration Contract — ràng buộc client Flutter với backend contract

| Thuộc tính | Giá trị |
|---|---|
| Document ID | FE-API-001 |
| Phiên bản | 0.1.1 |
| Trạng thái | DRAFT |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực — chờ Account Owner phê duyệt và Phase 5 task card READY |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | `contracts/api/openapi.yaml` (C-API-001 v1.1.0-draft); `contracts/errors/error-catalog.md` (C-ERR-001 1.1.1); AI_AUTO_TRADE_MASTER_SPEC.md §1.5, §5.1, §5.8, §11.2, §11.3, §12.1; SEC-003 (`docs/backend/security-ops/auth-session-policy.md`); NFR (`docs/shared/product/non-functional-requirements.md`) §7; FE-ARC-001 |
| Related requirements | FR-OPS-001, FR-AI-001; NFR-SEC-001, NFR-SAFE-001, NFR-AUD-001, NFR-AI-001 |
| Related ADR | ADR-0014, ADR-0015 (pending), ADR-0016 |

> **Phạm vi hiệu lực:** Tài liệu này ràng buộc HÀNH VI client khi tiêu thụ Control API. Nó KHÔNG cho phép implementation trước khi Phase 5 task card đạt READY (master §0.2). Mọi lựa chọn công nghệ nhắc tới ở đây là **DRAFT — cần Account Owner phê duyệt**.

## 1. Nguồn sự thật

- `contracts/api/openapi.yaml` là **canonical HTTP wire contract duy nhất** (master §11.2: "contracts/api/openapi.yaml là canonical HTTP wire contract"; authority hierarchy master §1.5 đặt "Versioned DDL, OpenAPI, JSON Schema..." trên code và generated artifact).
- Tài liệu này chỉ **diễn giải cách client PHẢI tiêu thụ** contract đó. Nếu tài liệu này mâu thuẫn với OpenAPI, **OpenAPI thắng**; sự mâu thuẫn phải được sửa bằng cập nhật tài liệu này qua quy trình document control, không bằng "chọn cách hiểu thuận tiện" (master §1.5: artifact cấp thấp mâu thuẫn cấp cao → BLOCKED).
- Client được **sinh từ OpenAPI, không viết tay** (FE-ARC-001 §4; master §11.2: không implement route/field/status code trước khi OpenAPI được duyệt).
- Base path: `/api/v1` (master §11.2; `openapi.yaml` `servers`).

## 2. Wire types bắt buộc

| Type | Định nghĩa contract | Hành vi client bắt buộc |
|---|---|---|
| `DecimalString` | pattern `^-?(?:0\|[1-9][0-9]*)(?:\.[0-9]{1,18})?$`, "never JSON number/float" (`openapi.yaml` schema `DecimalString`) | KHÔNG BAO GIỜ parse thành `double`/`float` (master §5.1; NFR §7: "Decimal + NUMERIC(38,18); ... API decimal string"). Giữ nguyên `String` hoặc dùng package decimal (DRAFT — FE-ARC-001 §2). Hiển thị đúng chuỗi server trả, không round-trip qua binary floating point. |
| `UuidV7` | pattern `^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$` (`openapi.yaml` schema `UuidV7`) | Validate theo pattern khi client tự sinh (correlation id, §9); truyền nguyên văn khi nhận từ server. |
| `Timestamp` | UTC ISO-8601, pattern `Z$` (`openapi.yaml` schema `Timestamp`; master §5.1: "Timestamp luôn UTC, timezone-aware và ISO-8601 có Z") | Hiển thị theo local timezone của user, nhưng lưu trữ nội bộ/so sánh/sắp xếp LUÔN theo giá trị UTC gốc. Không cắt bỏ hoặc suy diễn timezone. |
| `schema_version` / event version | "Tất cả public contract có schema_version" (master §5.1); "Consumer không được crash chỉ vì gặp event version chưa hỗ trợ" (master §5.8) | Gặp version/field-shape chưa hỗ trợ → hiển thị lỗi an toàn ("dữ liệu ở phiên bản chưa hỗ trợ, hãy cập nhật app") thay cho vùng dữ liệu đó; KHÔNG crash, KHÔNG đoán nghĩa field. |

Ngoài ra, response thiếu field `required` theo schema (`openapi.yaml` khai `required` + `additionalProperties: false` trên các schema chính) là contract violation: client PHẢI fail hiển thị lỗi an toàn, không silent default (FE-ARC-001 §4).

## 3. Async command pattern

Theo master §11.2 và `openapi.yaml`:

1. Client POST command → server trả **`202`** với body `CommandAccepted` gồm `command_id` (UuidV7), `status` = const `ACCEPTED`, `location` (uri-reference), `correlation_id`, `accepted_at` (schema `CommandAccepted`, required đủ 5 field) và header `Location` bắt buộc trỏ tới command status resource (response `CommandAccepted` trong `openapi.yaml`).
2. Client poll `GET` theo `Location` (`/commands/{command_id}`, schema `CommandStatus`).
3. Lifecycle: `ACCEPTED → RUNNING → SUCCEEDED | FAILED | CANCELLED` (master §11.2; enum `CommandStatus.status`). Poll dùng exponential backoff và **dừng ở trạng thái terminal** (FE-ARC-001 §3).

Ràng buộc UI bắt buộc:

- **"Acceptance is not successful execution"** (`openapi.yaml` response `CommandAccepted` description). UI KHÔNG ĐƯỢC hiển thị "thành công" khi mới nhận 202; trạng thái hiển thị lúc đó là "đã tiếp nhận / đang xử lý". Chỉ `SUCCEEDED` mới được hiển thị thành công.
- `status = FAILED` → hiển thị error envelope từ `CommandStatus.error` (schema cho phép `null | ErrorEnvelope`) theo đúng quy tắc §8, kèm `correlation_id`.
- `result_ref` (nullable, `openapi.yaml`) chỉ là tham chiếu an toàn tới kết quả; không suy diễn nội dung kết quả từ nó.

## 4. Idempotency

- Header `Idempotency-Key` là **bắt buộc trên mọi POST command thường**: 8–128 ký tự, pattern `^[A-Za-z0-9._:-]+$` (`openapi.yaml` parameter `IdempotencyKey`, `required: true`).
- Scope phía server = **actor + route + key**: "Unique per authenticated actor and route scope" (`openapi.yaml` `IdempotencyKey` description); master §11.2: "Scope là actor_id + route_scope + key; payload canonical hash phải khớp."
- Quy tắc client:
  - Sinh **key mới cho mỗi intent người dùng** (mỗi lần user chủ động yêu cầu một hành động mới).
  - **GIỮ NGUYÊN key khi retry cùng intent** (timeout mạng, mất response): same key/same payload trả original command/response (master §11.2), nên retry với key cũ là an toàn và đúng.
  - Nhận **`409 IDEMPOTENCY_KEY_REUSED`** = cùng key nhưng payload khác payload gốc (C-ERR-001: "Same actor/route/key had a different canonical request hash"). Client KHÔNG tự sửa (không tự đổi key, không tự đổi payload) — hiển thị cho user rằng yêu cầu trùng key với một yêu cầu khác nội dung, để user quyết định tạo intent mới.
- **NGOẠI LỆ duy nhất — `POST /ai/provider-connections/{connection_id}/credential-enrollments`**: route này KHÔNG có `Idempotency-Key` (write-only secret boundary; `openapi.yaml` operation `enrollAiProviderCredential`: "It does not use Idempotency-Key or a body hash"; master §11.2: "Exception duy nhất là secret-ingress credential-enrollments"). `409` tại route này map vào response `OperationBlocked` (không phải IdempotencyKeyReused — xem responses của operation này trong `openapi.yaml`), với code catalog `AI_ENROLLMENT_NOT_PERMITTED` (C-ERR-001). Xử lý bắt buộc: **đọc safe connection status** (`GET /ai/provider-connections/{connection_id}`) — "If the client loses the response, it must query safe connection status instead of automatically resubmitting a key" (`openapi.yaml`). **TUYỆT ĐỐI không auto-resubmit `api_key`** (C-ERR-001 `AI_ENROLLMENT_NOT_PERMITTED`: "do not automatically resubmit a key").

## 5. Optimistic concurrency (`If-Match`)

- Header `If-Match` là **bắt buộc** (`openapi.yaml` parameter `IfMatch`, `required: true`) trên: `strategy-activations`, `strategy-stops`, `kill-switch-releases`, và **toàn bộ AI connection lifecycle POST** (`rotations`, `credential-enrollments`, `validations`, `activations`, `suspensions`, `revocations` — theo parameters từng operation trong `openapi.yaml`).
- Mismatch → **`412 PRECONDITION_FAILED`** (master §11.2; C-ERR-001: "`If-Match`/resource version or required safe state not met. Refresh/review state").
- Hành vi client bắt buộc khi nhận 412: **refresh resource** để lấy version/state mới → **hiển thị diff/state mới** cho user → user **xác nhận lại** rồi mới gửi lại với version mới. **KHÔNG auto-retry với version mới** — auto-retry sẽ vô hiệu hóa chính mục đích của optimistic concurrency (user phải thấy state đã thay đổi trước khi tái xác nhận một dangerous action; master §11.4: không action high-risk nào chỉ dựa vào UI confirmation).

## 6. Re-authentication (`X-Reauthentication-Proof`)

- Header `X-Reauthentication-Proof` là **bắt buộc** (`openapi.yaml` parameter `ReauthenticationProof`, `required: true`, 1–4096 chars) trên: `kill-switch-releases` và **toàn bộ AI connection lifecycle** (`POST /ai/provider-connections` create, `rotations`, `credential-enrollments`, `validations`, `activations`, `suspensions`, `revocations` — theo parameters từng operation).
- Proof lấy từ re-auth flow do ADR-0015 định nghĩa (đang pending; SEC-003 §1). Proof **bound to actor, action class, target scope, issued/expiry time và correlation ID; không replay cho action khác** (SEC-003 §4; `openapi.yaml`: "action/scope-bound short-lived proof").
- UI flow bắt buộc: mở re-auth dialog cho đúng action đang thực hiện → nhận proof → gửi kèm **đúng một request duy nhất** → **discard proof ngay** sau khi request hoàn tất. Không cache, không reuse, không log/echo proof (`openapi.yaml`: "It must never be logged or echoed").
- Re-auth thất bại/hết hạn → server trả lỗi authorization an toàn (SEC-003 §4); client hiển thị và yêu cầu re-auth lại, không tự lặp proof cũ.

## 7. Pagination

Theo `openapi.yaml` parameters `Cursor`/`Limit` và master §11.2:

- Cursor là **opaque** (1–2048 chars): client **không parse, không suy diễn, không tự tạo** cursor; chỉ truyền lại nguyên văn `next_cursor` server trả.
- `limit`: integer 1–500, default 100 (`openapi.yaml` `Limit`).
- **Không offset pagination** ("Offset pagination is not supported" — `openapi.yaml` `Cursor` description và response `FillPage`; master §11.2).
- `next_cursor = null` = hết dữ liệu (các page schema `OrderTimelinePage`, `FillPage`, ... khai `next_cursor: [string, 'null']`); client dừng, không gọi thêm.

## 8. Error handling contract

Mọi lỗi trả về `ErrorEnvelope` với đủ 6 field required: `code`, `message`, `details`, `correlation_id`, `retryable`, `remediation_hint` (`openapi.yaml` schema `ErrorEnvelope`; C-ERR-001 §1). Bảng dưới lấy đúng 26 code từ C-ERR-001 §2 (HTTP mặc định và retryable theo catalog):

| Code | HTTP | Retryable | Hành vi UI bắt buộc |
|---|---:|---|---|
| `VALIDATION_FAILED` | 400 | No | Hiển thị lỗi input theo `details`; user sửa input rồi gửi lại như intent mới. Không retry nguyên trạng. |
| `AUTHENTICATION_REQUIRED` | 401 | No | Chuyển user sang flow đăng nhập/re-auth theo provider được duyệt (ADR-0015); xóa state phiên hiện tại khỏi UI. |
| `AUTHORIZATION_DENIED` | 403 | No | Thông báo thiếu quyền; KHÔNG gợi ý tồn tại/không tồn tại resource khác (catalog: "Do not reveal alternate resource state"). |
| `IDEMPOTENCY_KEY_REUSED` | 409 | No | Báo user key trùng với yêu cầu khác nội dung; không tự đổi key/payload (xem §4). |
| `PRECONDITION_FAILED` | 412 | No | Refresh resource, hiển thị state mới, user xác nhận lại; không auto-retry (xem §5). |
| `COMMAND_NOT_FOUND` | 404 | No | Hiển thị "command không tồn tại hoặc ngoài phạm vi quyền"; dừng polling command đó. |
| `RESOURCE_NOT_FOUND` | 404 | No | Hiển thị "không tìm thấy trong phạm vi quyền"; không phân biệt "không tồn tại" với "không có quyền". |
| `COMMAND_STATE_CONFLICT` | 409 | No | Báo transition không hợp lệ với lifecycle hiện tại; refresh command status để hiển thị trạng thái thật. |
| `RISK_REJECTED` | 422 | No | Hiển thị từ chối bởi risk policy + `remediation_hint`; KHÔNG có nút retry, KHÔNG gợi ý bypass (catalog: "do not bypass"). |
| `RUNTIME_NOT_READY` | 503 | Yes — sau khi readiness phục hồi | Hiển thị runtime chưa sẵn sàng; **poll `GET /readiness`** và chỉ mở lại action khi `ready=true`; không retry command khi readiness chưa phục hồi. |
| `RECONCILIATION_BLOCKED` | 423 | No | Banner scope đang có mismatch chưa xử lý; disable submit trong scope; hướng dẫn theo `remediation_hint` ("Reconcile; do not force submit"). |
| `KILL_SWITCH_ACTIVE` | 423 | No | **Banner toàn cục kill switch** + disable mọi nút submit bị chặn; release chỉ qua flow high-risk được duyệt (§5, §6), không có "retry". |
| `EXTERNAL_OUTCOME_UNKNOWN` | 409 | No | Hiển thị guidance reconcile ("External submit/cancel result uncertain. Reconcile; never blind retry" — catalog); **KHÔNG hiển thị nút retry**. |
| `AI_PROVIDER_NOT_ALLOWED` | 403 | No | Yêu cầu chọn provider từ catalog đã duyệt (`GET /ai/providers`); không cho nhập URL tùy ý. |
| `AI_MODEL_NOT_ALLOWED` | 403 | No | Yêu cầu chọn model profile đã duyệt (`GET /ai/providers/{provider_id}/models`). |
| `AI_CONNECTION_SCOPE_DENIED` | 403/404 | No | Hiển thị "connection không tồn tại hoặc ngoài owner scope"; không tiết lộ trạng thái resource của owner khác. |
| `AI_CREDENTIAL_NOT_CONFIGURED` | 423 | No | Hướng user tới flow enrollment write-only được duyệt; disable action phụ thuộc credential. |
| `AI_CREDENTIAL_VALIDATION_FAILED` | 422 | No | Hiển thị probe validation thất bại + thông điệp catalog "no trading data was sent"; user review connection/catalog/policy. |
| `AI_ENROLLMENT_NOT_PERMITTED` | 409 | No | Đọc safe connection status rồi hiển thị; **TUYỆT ĐỐI không auto-resubmit key** (xem §4 ngoại lệ). |
| `AI_EGRESS_POLICY_DENIED` | 403 | No | Hiển thị vi phạm egress policy; không gợi ý bypass/fallback silent (catalog). |
| `AI_BUDGET_EXCEEDED` | 429 | No | **KHÔNG retry**; hiển thị thông tin budget window theo `details`/`remediation_hint` ("Wait for approved policy window/change; no provider request was made"). |
| `AI_PROVIDER_UNAVAILABLE` | 503 | Conditional | Chỉ retry theo approved AI policy khi `retryable=true`; hiển thị rõ "chỉ AI capability bị ảnh hưởng, trading không bị ảnh hưởng" (catalog). |
| `AI_OUTPUT_INVALID` | 422 | No | Hiển thị output provider không qua được schema/provenance validation; ghi rõ "no proposal/memory write occurred" (catalog); không retry. |
| `AI_OUTCOME_UNKNOWN` | 409 | No | Hiển thị outcome không chắc chắn; KHÔNG blind retry, KHÔNG gợi ý gửi sang provider khác (catalog). |
| `SENSITIVE_INPUT_REJECTED` | 400 | No | Báo user **xóa nội dung giống secret khỏi field reason/note** rồi nhập lại ("Remove it; never use an audit field to transmit a credential" — catalog); không giữ lại nội dung bị reject trong state/log. |
| `INTERNAL_ERROR` | 500 | Conditional | Hiển thị lỗi hệ thống an toàn + `correlation_id` làm evidence; retry chỉ khi `retryable=true` và policy cho phép (catalog). |

Quy tắc chung bắt buộc:

- `retryable=false` → **KHÔNG hiển thị nút retry** cho action đó; đường đi tiếp duy nhất là hành động khắc phục trong `remediation_hint`. Lưu ý: kể cả `retryable=true` cũng "never authorizes blind external submit retry" (C-ERR-001 §3).
- `correlation_id` **LUÔN hiển thị** trong error detail để user báo cáo/trace (envelope required field; NFR-AUD-001).
- `remediation_hint` hiển thị **nguyên văn** — server chịu trách nhiệm nội dung safe (C-ERR-001 §1); client không viết lại/diễn dịch.
- Envelope không bao giờ chứa stack trace/secret/vendor raw payload (C-ERR-001 §1) — nếu client phát hiện nội dung bất thường trong `details`, không render raw mà báo lỗi hiển thị an toàn.

## 9. Correlation

- `X-Correlation-Id` là header **optional**; client NÊN gửi UUIDv7 tự sinh cho **mọi request** — "Optional UUIDv7 supplied by the caller; runtime generates one if absent" (`openapi.yaml` parameter `CorrelationId`, có mặt trên mọi operation **trừ** `getHealth`/`getReadiness` — hai probe này không khai parameter trong v1.1; gửi kèm vẫn vô hại, server bỏ qua).
- `correlation_id` (từ `CommandAccepted`, `CommandStatus`, `ErrorEnvelope`, `Order`...) phải được hiển thị trong error view và audit view để user trace/báo cáo sự cố (NFR-AUD-001; master §11.3: mọi command nguy hiểm có correlation ID).

## 10. Cache policy và client logging

- **Mặc định: không cache response.** Ngoại lệ duy nhất được phép cân nhắc: catalog đọc-nhiều đổi-ít (`GET /ai/providers`, `/ai/providers/{provider_id}/models`, `/ai/policy-profiles`) với TTL ngắn — mức TTL là **DRAFT — cần Account Owner phê duyệt**.
- **Enrollment/credential path: `Cache-Control: no-store` là bắt buộc theo contract** — response `201` của `credential-enrollments` ("Credential enrollment responses must never be cached") và response `201` của `POST /ai/provider-connections` mang enrollment session ("must never be cached") đều khai header `Cache-Control: const no-store` trong `openapi.yaml`. Client KHÔNG cache, KHÔNG log các response này; enrollment-session cookie là Secure/HttpOnly/SameSite, "must be redacted from logs/evidence and may not be exposed to browser JS" (`openapi.yaml` header `Set-Cookie` của `createAiProviderConnection`).
- **Client logging**: không log request/response body chứa `reason`/`api_key` hay bất kỳ secret/token/proof nào — master §12.1 ("Secret ở approved secret provider/injection; không commit, log, trace, UI, browser storage..."), SEC-003 §5 (audit không capture raw token/cookie/authorization header), `openapi.yaml` (`ActorAuthentication`, `ReauthenticationProof`: never logged). Log phía client (nếu có, cho debug) chỉ chứa method, route template, status code và correlation_id.

## Nhật ký thay đổi

| Phiên bản | Ngày | Tác giả | Phê duyệt | Nội dung |
|---|---|---|---|---|
| 0.1.1 | 2026-08-02 | Technical Operator | Pending | Audit toàn diện: §9 sửa khẳng định "mọi operation" — `CorrelationId` không khai trên getHealth/getReadiness trong v1.1. |
| 0.1.0 | 2026-07-31 | Technical Operator | Pending | Bản DRAFT đầu tiên: nguồn sự thật OpenAPI, wire types, async command pattern, idempotency (kèm ngoại lệ credential-enrollments), If-Match, re-auth proof, pagination, bảng 26 error codes với hành vi UI, correlation và cache/logging policy. |
