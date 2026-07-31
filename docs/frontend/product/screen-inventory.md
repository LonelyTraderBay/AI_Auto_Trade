# FE-SCREEN-001 — Information Architecture và Screen Inventory (Flutter Dashboard)

| Thuộc tính | Giá trị |
|---|---|
| Document ID | FE-SCREEN-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | DRAFT |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực — đây là input thiết kế cho Phase 5/6, không cho phép bất kỳ implementation nào trước các gate đó |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | contracts/api/openapi.yaml v1.1.0-draft (28 routes /api/v1); AI_AUTO_TRADE_MASTER_SPEC.md §11.2, §11.3, §11.5, §14; docs/backend/security-ops/access-control-matrix.md (SEC-002); docs/backend/security-ops/slo-sli-alert-policy.md (OPS-001) §4.2; docs/backend/domain/oms-state-machine.md (DOM-002); docs/frontend/product/frontend-charter.md (FE-CHARTER-001) |
| Related requirements | FR-FE-001..FR-FE-007 (DRAFT — FE-CHARTER-001 §4); FR-OPS-001, NFR-SEC-001, NFR-OPS-001 |
| Related ADR | ADR-0014, ADR-0015 (DRAFT — auth provider TBD), ADR-0016 (Phase 6) |

> **Cảnh báo phạm vi:** Screen inventory này là DRAFT input cho Phase 5 (screens A–L) và Phase 6 (screens M). Nó không cho phép viết code, không tạo route API mới. Mọi route liệt kê dưới đây tồn tại trong contracts/api/openapi.yaml v1.1.0-draft trừ khi được đánh dấu **GAP** (xem §4). Không screen nào được phép hiển thị/giữ secret hoặc chứa business logic (master §3.4, §11.5; SEC-002 §3 row `dashboard`).

## 1. Quy ước chung cho mọi screen

- **Prefix API:** mọi path dưới đây là tương đối so với `/api/v1` (master §11.2).
- **States phải render:** mọi screen dữ liệu tối thiểu phải xử lý 4 trạng thái: `loading`, `empty`, `error` (render error envelope an toàn: code, message, correlation_id, retryable, remediation_hint — master §11.2), và `stale` (dữ liệu cache phải mang nhãn stale + timestamp; không bao giờ hiển thị như dữ liệu tươi — FE-CHARTER-001 FR-FE-001). Cột "States" bên dưới chỉ ghi các trạng thái **đặc thù thêm** của screen đó.
- **Role:** cột "Role thấy được" là visibility gating phía UI; authorization luôn được đánh giá server-side (SEC-002 §1). Viewer thấy mọi read view sanitized (master §11.3 "đọc health/projection: Viewer").
- **Pagination:** mọi list dùng cursor pagination với opaque cursor (`cursor`/`limit` parameters, openapi.yaml); không offset (master §11.2).
- **Số liệu tài chính:** DecimalString, không parse qua float (master §11.2 "Decimal là string"); timestamp UTC ISO-8601 Z.

## 2. Information architecture

~~~text
Shell (A: navigation + session)
├── Overview / Runtime (B)
├── Trading
│   ├── Orders list/detail + UNKNOWN view (C)
│   ├── Fills (D)
│   └── Portfolio (E)
├── Operations
│   ├── Reconciliation queue (F)   [một phần GAP]
│   ├── Kill switch (G)            [state view GAP]
│   ├── Incidents (H)
│   ├── Audit (I)
│   ├── Commands center (J)
│   ├── Deployments (K)
│   └── Ops health views (L)       [GAP]
└── AI / BYOK (M) — Phase 6
~~~

## 3. Screen inventory

### A. Shell / Navigation + phiên đăng nhập — Phase 5

| Mục | Nội dung |
|---|---|
| Mục đích | Khung điều hướng, hiển thị danh tính actor + role đang hoạt động, quản lý phiên đăng nhập và re-auth prompt |
| API | Không có route đăng nhập trong openapi.yaml v1.1 — **auth provider/session model là OD-006 + ADR-0015, hiện DRAFT ("provider/session choice unresolved"). Toàn bộ login/logout/refresh/re-auth flow trong tài liệu này là PLACEHOLDER cho đến khi ADR-0015 APPROVED.** SecurityScheme hiện tại chỉ là bearer placeholder "provider-defined" (openapi.yaml components.securitySchemes.ActorAuthentication) |
| Role | Tất cả role đã xác thực; navigation ẩn/disable mục theo role (FE-CHARTER-001 §2.2) nhưng không tự cấp quyền |
| States | `unauthenticated`, `session-expired` (401 AUTHENTICATION_REQUIRED ở bất kỳ call nào → về login), `reauth-required` (dangerous action), `disconnected` (mất kết nối API — hiển thị rõ, không che; mất dashboard không ảnh hưởng trading node, master §11.5) |
| Ràng buộc | Token/proof không bao giờ được log (openapi.yaml ActorAuthentication description); không lưu secret trong browser/app storage (master §12.1) |

### B. Overview / Runtime — Phase 5

| Mục | Nội dung |
|---|---|
| Mục đích | Hiển thị "mode thật" của hệ thống (master §11.5): danh tính runtime, safe state, manifest |
| API | GET /runtime; GET /readiness (no-auth); GET /health (no-auth) — openapi.yaml |
| Dữ liệu | `environment` (local/ci/paper/testnet/canary/live), `run_mode` (BACKTEST/REPLAY/SHADOW/PAPER_SIMULATOR/TESTNET/CANARY/FULL_LIVE), `execution_target` (INTERNAL_SIMULATOR/DISABLED/VENUE_TESTNET/VENUE_LIVE), `safe_state` (READY/BLOCKED/FROZEN/KILL_SWITCH_ACTIVE), `manifest_hash`, `deployment_id`, `observed_at` — schema Runtime (openapi.yaml); `ready` + `blocking_reasons` — schema Readiness |
| Role | Viewer trở lên (health/readiness không cần auth theo openapi.yaml `security: []`; /runtime cần auth) |
| States | **Banner cảnh báo nổi bật khi `safe_state != READY`**, liệt kê `blocking_reasons`; `degraded` khi Health.status = DEGRADED; 503 RUNTIME_NOT_READY render là trạng thái hệ thống, không phải lỗi UI |
| Phase | 5 |

### C. Orders list/detail — Phase 5

| Mục | Nội dung |
|---|---|
| Mục đích | Xem canonical order projection và timeline bất biến; giám sát UNKNOWN orders |
| API | GET /orders/{order_id}; GET /orders/{order_id}/timeline (cursor pagination, thứ tự recorded-at/event-ID ổn định) — openapi.yaml. **GAP:** không có GET /orders (list/search) trong OpenAPI v1.1 — xem §4 |
| Dữ liệu | Đủ **16 states**: CREATED, PENDING_MANUAL_APPROVAL, RISK_APPROVED, RISK_REJECTED, SUBMISSION_QUEUED, SUBMITTING, OPEN, PARTIALLY_FILLED, FILLED, REJECTED, CANCEL_REQUESTED, CANCELLED, EXPIRED, UNKNOWN, RECONCILING, LOST (openapi.yaml schema Order.state; DOM-002 §2). `terminal_reason` hiển thị khi terminal; DOM-002 §5 định nghĩa các reason chi tiết (IOC_REMAINDER_CANCELLED, INTENT_EXPIRED, DECISION_EXPIRED, APPROVAL_EXPIRED, VENUE_TIF_EXPIRED) — **lưu ý alignment với enum OpenAPI hiện tại, xem §4 mục 5**. `executed_quantity`/`requested_quantity` là DecimalString. Risk verdict hiển thị trong timeline theo APPROVE/REJECT/REQUIRE_MANUAL_APPROVAL (docs/backend/domain/risk-policy.md, bảng verdict) |
| View bắt buộc | **UNKNOWN orders view với AGE của từng order** — OPS-001 §4.2 view 1 ("`UNKNOWN` orders và tuổi của từng order"); escalate hiển thị theo `unknown_order_sla_s` (OPS-001 §2). **GAP:** cần route list/filter theo state — xem §4 |
| Role | Viewer trở lên (sanitized, least-data scope — SEC-002 §2) |
| States | UNKNOWN/RECONCILING render là safe-block nổi bật, không phải lỗi; terminal state render kèm terminal_reason; 404 an toàn (không tiết lộ tồn tại resource khác scope — SEC-002 §4) |
| Phase | 5 |

### D. Fills — Phase 5

| Mục | Nội dung |
|---|---|
| Mục đích | Danh sách fill bất biến phục vụ đối chiếu PnL/ledger |
| API | GET /fills với filter `account_id`, `instrument_id` (parameters AccountIdFilter/InstrumentIdFilter, openapi.yaml) + cursor/limit |
| Dữ liệu | fill_id, order_id, quantity/price/fee (DecimalString), occurred_at/recorded_at (schema Fill, openapi.yaml) |
| Role | Viewer trở lên |
| States | Chuẩn (loading/empty/error/stale) |
| Phase | 5 |

### E. Portfolio — Phase 5

| Mục | Nội dung |
|---|---|
| Mục đích | Snapshot position có version phục vụ giám sát exposure; "không phải một trading instruction" (openapi.yaml mô tả response) |
| API | GET /portfolio/snapshot với filter `account_id` — openapi.yaml |
| Dữ liệu | snapshot_id, account_id, `as_of_at`, `source_hash`, positions[] {instrument_id, quantity DecimalString} (schema PortfolioSnapshot, openapi.yaml) |
| Role | Viewer trở lên |
| States | **423 OperationBlocked** ("Kill switch, reconciliation, or another safety control blocks the requested action" — openapi.yaml responses.OperationBlocked) render là trạng thái blocked có ngữ cảnh (link tới màn Reconciliation/Kill switch), không phải error chung; luôn hiển thị `as_of_at` để người xem biết độ tươi |
| Phase | 5 |

### F. Reconciliation queue — Phase 5 (view bắt buộc 2, một phần GAP)

| Mục | Nội dung |
|---|---|
| Mục đích | "Reconciliation queue/case đang mở" — OPS-001 §4.2 view 2; theo dõi mismatch age/count (OPS-001 §2) |
| API hiện có | Nguồn gián tiếp: GET /incidents (case reconciliation thể hiện qua incident scope) + GET /commands/{command_id} (trạng thái REQUEST_RECONCILIATION command); POST /commands/reconciliations để request reconciliation (Technical Operator — openapi.yaml) |
| **GAP đã biết** | **Không có route riêng cho reconciliation cases (list case/mismatch, tuổi, scope bị block) trong OpenAPI v1.1.** Đây là GAP phải bổ sung OpenAPI trước Phase 5 vì OPS-001 §4.2 yêu cầu view này trước testnet. Xem §4 |
| Role | Viewer xem; Technical Operator gửi POST /commands/reconciliations (master §11.3) |
| States | Case mở render theo tuổi; scope bị freeze ("Freeze affected new exposure" — OPS-001 §2) phải nhìn thấy được |
| Phase | 5 |

### G. Kill switch — Phase 5

| Mục | Nội dung |
|---|---|
| Mục đích | "Kill-switch state theo từng scope" (OPS-001 §4.2 view 5) + activate/release |
| API | POST /commands/kill-switch-activations (Idempotency-Key; "Activation blocks new submission; it does not assume in-flight venue operations failed" — openapi.yaml); POST /commands/kill-switch-releases (Idempotency-Key + If-Match + **ReauthenticationProof**; body bắt buộc `kill_switch_id`, `scope`, **`verification_evidence_ref`** — openapi.yaml KillSwitchReleaseCommandRequest); GET /commands/{command_id} theo dõi kết quả. **GAP:** không có GET route đọc danh sách/trạng thái kill switch theo scope trong OpenAPI v1.1 — hiện chỉ suy ra được từ Runtime.safe_state=KILL_SWITCH_ACTIVE (toàn cục) — xem §4 |
| Role | State view: Viewer trở lên. Activate: Technical Operator ("không, nhưng actor xác thực" — master §11.3). Release: **Risk Approver + Account Owner, re-auth bắt buộc** (master §11.3; SEC-002 §2 "Reconciliation/health preconditions met") |
| States | Release flow render: form reason + verification_evidence_ref + re-auth → 202 → theo dõi command; 423 OperationBlocked khi precondition chưa đạt; 412 PRECONDITION_FAILED khi If-Match lệch version |
| Phase | 5 |

### H. Incidents — Phase 5

| Mục | Nội dung |
|---|---|
| Mục đích | Danh sách incident cho vận hành; deliverable Phase 5 "incident/audit/reconciliation/deployment view" (master §14 Phase 5) |
| API | GET /incidents (cursor/limit) — openapi.yaml |
| Dữ liệu | severity CRITICAL/HIGH/MEDIUM/LOW, status OPEN/MITIGATING/RESOLVED/CLOSED, detected_at, scope, correlation_ids (schema Incident, openapi.yaml) |
| Role | Viewer trở lên |
| States | Chuẩn; CRITICAL nổi bật theo severity policy OPS-001 §4 |
| Phase | 5 |

### I. Audit — Phase 5

| Mục | Nội dung |
|---|---|
| Mục đích | Xem audit-event bất biến, phục vụ evidence "actor/audit trail cho toàn bộ dangerous action" (exit gate Phase 5, master §14) |
| API | GET /audit-events (cursor/limit; "redacted audit events in stable recorded-at/event-ID order" — openapi.yaml) |
| Dữ liệu | audit_event_id, actor_id, action, subject_ref, recorded_at, correlation_id, before_hash, after_hash (schema AuditEvent, openapi.yaml) |
| Role | Viewer trở lên (sanitized); "sensitive audit export" cần reason theo SEC-002 §2 — export không thuộc scope UI v1 |
| States | Chuẩn |
| Phase | 5 |

### J. Commands center — Phase 5

| Mục | Nội dung |
|---|---|
| Mục đích | Theo dõi mọi async command mà actor đã gửi từ UI |
| API | GET /commands/{command_id}; polling theo **Location header** trả về từ 202 CommandAccepted (openapi.yaml responses.CommandAccepted headers.Location "Relative command status resource location") |
| Dữ liệu | command_type (11 giá trị enum, openapi.yaml CommandStatus.command_type), status lifecycle **ACCEPTED → RUNNING → SUCCEEDED / FAILED / CANCELLED** (master §11.2; openapi.yaml CommandStatus.status), requested_at/completed_at, correlation_id, result_ref, error |
| Role | Actor đã gửi command trong scope của mình; 404 COMMAND_NOT_FOUND an toàn ngoài scope |
| States | In-flight (ACCEPTED/RUNNING) polling có backoff; terminal record là append-only audit evidence (master §11.2), UI không cho "gửi lại" tự động — resubmit là hành động mới của actor với Idempotency-Key mới hoặc key cũ theo FE-CHARTER-001 FR-FE-004 |
| Ghi chú | **GAP:** không có GET /commands (list) trong OpenAPI v1.1 — command center v1 chỉ theo dõi được command_id do chính UI session lưu lại; xem §4 |
| Phase | 5 |

### K. Deployments — Phase 5

| Mục | Nội dung |
|---|---|
| Mục đích | Xem danh tính deployment bất biến, đối chiếu manifest_hash với Runtime |
| API | GET /deployments/{deployment_id} — openapi.yaml ("Immutable deployment manifest projection without secret values") |
| Dữ liệu | deployment_id, environment, run_mode, execution_target, manifest_hash, approved_at, created_at (schema Deployment, openapi.yaml) |
| Role | Viewer trở lên |
| States | Chuẩn; highlight khi manifest_hash không khớp Runtime.manifest_hash đang chạy |
| Phase | 5 |

### L. Ops health views (lease/leader, outbox/DLQ, backup) — Phase 5 (GAP)

| Mục | Nội dung |
|---|---|
| Mục đích | Ba view bắt buộc còn lại của OPS-001 §4.2: **view 3** lease/leader state; **view 4** outbox/inbox/DLQ backlog (count và age); **view 6** backup age và last restore drill |
| API | **GAP — KHÔNG CÓ route nào trong OpenAPI v1.1 phục vụ 3 view này.** Không được vẽ UI đọc trực tiếp DB/metrics để lách (SEC-002 §3: dashboard không có DB role). Contract phải được bổ sung vào openapi.yaml **trước Phase 5**, vì OPS-001 §4.2 tuyên bố "Thiếu view bắt buộc là gap đối với testnet gate evidence" |
| Role | Viewer trở lên (sanitized) — dự kiến, chốt khi bổ sung contract |
| States | Dự kiến: lease mất/ambiguous là Critical ("Block submission on lost/ambiguous lease" — OPS-001 §2); backlog theo age/count; backup age vượt policy là High/Critical (OPS-001 §2) |
| Phase | 5 — nhưng BLOCKED bởi GAP register §4 |

### M. BYOK screens — Phase 6

Toàn bộ nhóm M chỉ mở sau điều kiện vào Phase 6: ADR-0008 + ADR-0016 APPROVED, OD-008 RESOLVED, auth/machine identity + secret topology được duyệt (master §14 Phase 6). Không screen nào hiển thị/hồi tồn raw key, secret reference hay fingerprint (openapi.yaml mô tả tag `ai`; SEC-002 §2).

#### M1. Catalog browser

- **API:** GET /ai/providers; GET /ai/providers/{provider_id}/models — openapi.yaml ("never endpoint URL, credential material or another owner's connection").
- **Dữ liệu:** provider lifecycle_status ACTIVE/SUSPENDED/RETIRED, data_egress_class, model lifecycle_status ACTIVE/DEPRECATED/RETIRED, capability metadata (openapi.yaml schemas). Unknown/deprecated/scope-ineligible không dùng được cho connection (openapi.yaml mô tả route models).
- **Role:** Viewer trong owner scope (master §11.3 "xem AI provider/model catalog đã duyệt").

#### M2. Policy profiles

- **API:** GET /ai/policy-profiles — openapi.yaml ("Returns only Security-approved profile metadata. Individual endpoint/egress/budget policy IDs cannot be supplied by a caller outside an active profile").
- **Role:** Viewer/Account Owner theo scope.

#### M3. Connections list/detail

- **API:** GET /ai/provider-connections (cursor); GET /ai/provider-connections/{connection_id} — openapi.yaml.
- **Dữ liệu:** render đủ **10 status**: DRAFT, PENDING_SECRET, PENDING_VALIDATION, ACTIVE, ROTATION_PENDING_SECRET, ROTATION_PENDING_VALIDATION, SUSPENDED, VALIDATION_FAILED, EXPIRED, REVOKED (openapi.yaml AIProviderConnection.status). SUSPENDED/EXPIRED/REVOKED là terminal trong BYOK v1 — UI hiển thị hướng dẫn "tạo connection lifecycle mới, không reactivate" (openapi.yaml status description). Metadata sanitized: revision, environment (paper/testnet/canary/live), provider_selection, policies, timestamps.
- **Role:** Account Owner own scope (SEC-002 §2 "Read AI connection metadata").

#### M4. Create flow + credential enrollment UI

- **API:** POST /ai/provider-connections (Idempotency-Key + ReauthenticationProof; 201 tạo PENDING_SECRET + Location + one-time enrollment-session cookie Secure/HttpOnly/SameSite, Cache-Control: no-store — openapi.yaml); sau đó POST /ai/provider-connections/{connection_id}/credential-enrollments (ReauthenticationProof + If-Match; **không có Idempotency-Key** — openapi.yaml).
- **Quy tắc UI bắt buộc (nguồn: openapi.yaml mô tả credential-enrollments + master §11.2):** ô nhập key là **write-only, một lần**; không hiển thị lại, không copy-back, không lưu local; response chỉ là safe receipt ("never the API key, secret reference, fingerprint, length or raw provider result"); **nếu mất response → GET connection status, KHÔNG resubmit key tự động**; 409 tại route này là OperationBlocked (openapi.yaml responses của credential-enrollments), không phải idempotency-reuse.
- **Role:** Account Owner own scope, re-auth (SEC-002 §2 "Enroll candidate AI provider key").

#### M5. Validate / Activate (dual-role)

- **API:** POST .../validations; POST .../activations (đều Idempotency-Key + ReauthenticationProof + If-Match; 202 → command lifecycle) — openapi.yaml.
- **UI render pending states:** PENDING_VALIDATION / ROTATION_PENDING_VALIDATION; server-side workflow phải ghi **cả hai role approval Account Owner + Security/Backup Owner** trước khi dispatch (openapi.yaml mô tả validations/activations; SEC-002 §2) — UI hiển thị tiến trình chờ role thứ hai, không tự bypass; cùng-cá-nhân-hai-role pre-canary cần record hai role + waiver theo master §11.4.
- **States:** VALIDATION_FAILED render kèm safe reason; activation cho rotation là atomic swap candidate↔active (openapi.yaml mô tả activations); 423 khi lifecycle precondition chặn.

#### M6. Rotation flow

- **API:** POST .../rotations (Idempotency-Key + ReauthenticationProof + If-Match) — ACTIVE → ROTATION_PENDING_SECRET; "existing active binding remains the only binding eligible for inference until a candidate is enrolled, validated and atomically activated. It never carries credential material" (openapi.yaml). Sau đó tái dùng M4 (enrollment) và M5 (validate/activate).
- **Role:** Account Owner own scope (SEC-002 §2, master §11.3 "tạo/enroll/rotate/revoke AI connection của scope mình").

#### M7. Suspend / Revoke

- **API:** POST .../suspensions; POST .../revocations (Idempotency-Key + ReauthenticationProof + If-Match) — openapi.yaml.
- **Role:** Account Owner own scope; **Security/Backup Owner emergency unilateral** với re-auth/reason/audit + Account Owner notification/post-containment review (openapi.yaml mô tả; master §11.3; SEC-002 §2).
- **States:** upstream key revocation hiển thị "unverified" cho đến khi có provider evidence (openapi.yaml mô tả revocations; SEC-002 §2).

## 4. GAP register — route còn thiếu trong OpenAPI v1.1

Các mandatory view sau (OPS-001 §4.2 + nhu cầu screen ở §3) **chưa có route trong contracts/api/openapi.yaml v1.1.0-draft**. Theo master §11.2 ("Không implement route... trước khi OpenAPI và fixture tương ứng được duyệt"), frontend **không được** tự chế nguồn dữ liệu thay thế (đọc DB, đọc metrics nội bộ). Mỗi GAP là **required-before-Phase-5**: phải bổ sung OpenAPI + fixture và được duyệt trước khi Phase 5 task card liên quan chuyển READY, vì OPS-001 §4.2 coi thiếu view bắt buộc là gap đối với testnet gate evidence.

| # | GAP | Mandatory view bị chặn | Route cần bổ sung (đề xuất, cần contract review) | Trạng thái |
|---|---|---|---|---|
| 1 | Reconciliation cases: không có route list case/mismatch (tuổi, scope bị block, tolerance) | OPS-001 §4.2 view 2 (reconciliation queue/case) → screen F | GET danh sách reconciliation case (cursor + filter scope/status) | **required-before-Phase-5** |
| 2 | Lease/leader state: không có route đọc leader/lease health theo venue/account queue | OPS-001 §4.2 view 3 → screen L | GET lease/leader state projection | **required-before-Phase-5** |
| 3 | Outbox/inbox/DLQ metrics: không có route đọc backlog count/age | OPS-001 §4.2 view 4 → screen L | GET outbox/inbox/DLQ backlog projection | **required-before-Phase-5** |
| 4 | Backup status: không có route đọc backup age/last restore drill | OPS-001 §4.2 view 6 → screen L | GET backup/restore-drill status projection (sanitized) | **required-before-Phase-5** |
| 5 | Kill-switch state per scope: không có GET route; chỉ suy ra được KILL_SWITCH_ACTIVE toàn cục từ Runtime.safe_state | OPS-001 §4.2 view 5 → screen G | GET kill-switch state theo scope | **required-before-Phase-5** |
| 6 | Orders list/filter: không có GET /orders (list) — UNKNOWN orders view cần list theo state + age | OPS-001 §4.2 view 1 → screen C | GET orders list (cursor + filter state/account/instrument) | **required-before-Phase-5** |
| 7 | Commands list: không có GET /commands (list) — commands center chỉ theo dõi được ID tự lưu | Screen J (tiện vận hành, không thuộc OPS-001 §4.2) | GET commands list theo actor/scope | Nên có trước Phase 5, ưu tiên thấp hơn 1–6 |
| 8 | Alignment `terminal_reason`: openapi.yaml Order.terminal_reason enum hiện là [RISK_REJECTED, REJECTED, CANCELLED, EXPIRED, FILLED, LOST] trong khi DOM-002 §5 (v0.2.0 DRAFT) định nghĩa reason chi tiết IOC_REMAINDER_CANCELLED / INTENT_EXPIRED / DECISION_EXPIRED / APPROVAL_EXPIRED / VENUE_TIF_EXPIRED | Screen C (order detail render terminal_reason) | Đồng bộ enum giữa DOM-002 và OpenAPI khi ADR-0005/0009 chốt; UI không tự bịa reason ngoài enum contract | Contract-alignment, cần đóng trước Phase 5 |

AI budget/egress view (OPS-001 §4.2, Phase 6) hiện cũng chưa có route đọc budget/usage trong 12 route /ai/* của v1.1; GAP này thuộc điều kiện Phase 6, ghi nhận tại đây để theo dõi cùng ADR-0016/OD-008.

## Nhật ký thay đổi

| Ngày | Phiên bản | Người thực hiện | Phê duyệt | Nội dung |
|---|---|---|---|---|
| 2026-07-31 | 0.1.0 | Technical Operator | Pending | Khởi tạo screen inventory DRAFT: IA + 13 nhóm screen (A–M) map vào 28 route /api/v1 của openapi.yaml v1.1.0-draft, role gating theo master §11.3/SEC-002, states bắt buộc (loading/empty/error/stale + đặc thù), phase gating 5/6; GAP register 8 mục required-before-Phase-5. Không cho phép implementation trước Phase 5 gate |
