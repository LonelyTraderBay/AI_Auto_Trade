# AI đa provider và BYOK architecture

| Thuộc tính | Giá trị |
|---|---|
| Document ID | ARC-AI-001 |
| Phiên bản | 0.2.0 |
| Trạng thái | DRAFT — thiết kế Phase 6, chưa cho phép runtime/provider/key thật |
| Owner | Technical Operator + Security/Backup Owner |
| Approver | Account Owner |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §6.4, §10.1, §10.6–§10.8, §11–§12, §14 Phase 6 |
| Related requirements | FR-AI-001, NFR-AI-001, SEC-AI-001, SEC-AI-002, SEC-AI-003 |
| Change summary | 0.2.0 (2026-08-02): bổ sung changelog (§10) và row Change summary — audit phát hiện đây là file duy nhất trong scope architecture không có nhật ký thay đổi; thêm SEC-AI-001 vào Related (zero-execution/proposal-only là nội dung cốt lõi §1/§3). Nội dung kiến trúc không đổi. |
| Related ADR | ADR-0008, ADR-0015, ADR-0016 |

> Tài liệu này làm rõ “đa provider” và “BYOK” để agent không tự giả định OpenAI là bắt buộc hoặc tự cho phép endpoint tùy ý. Nó là design authority DRAFT, không phải authorization để tạo key, gọi provider, tạo endpoint, migration hay runtime dependency.

## 1. Mục tiêu và non-goals

### Mục tiêu

- Người dùng trong owner scope được chọn một provider/model đã được duyệt và dùng API key của chính họ.
- Không provider nào, kể cả OpenAI, là dependency bắt buộc cho hệ thống.
- Key luôn ở secret boundary; user không thể đọc lại sau khi submit và dashboard không giữ key.
- AI vẫn proposal-only, ngoài hot path, không trade/execution/risk/config/deployment authority.
- Provider outage, budget exhaustion, output invalid hoặc revoke key chỉ ảnh hưởng AI capability.

### Không thuộc phạm vi

- Không hỗ trợ người dùng nhập arbitrary URL, proxy, model ID hoặc provider SDK tùy ý.
- Không tạo multi-tenant trading architecture trong MVP; initial owner scope là Account Owner/account environment. Multi-user/tenant cần ADR mở rộng.
- Không cho AI tool/function call để truy cập execution, database, filesystem, browser, network tùy ý hoặc secret.
- Không lưu raw prompt/response mặc định và không tự huấn luyện/tự fine-tune từ dữ liệu user.

## 2. Nguyên tắc quyết định

| Nguyên tắc | Quy tắc có thể kiểm chứng |
|---|---|
| Provider-neutral | Adapter ở `adapters/llm/<provider>` implement port chuẩn; SDK provider không đi vào domain/application. |
| Catalog, không arbitrary endpoint | User chọn provider/model từ `ACTIVE` catalog/profile; endpoint là ID profile được Security Owner phê duyệt. |
| BYOK không đồng nghĩa key read-back | Key chỉ đi vào secret enrollment write-only; API/UI/database chỉ thấy metadata opaque. |
| Least privilege | `ai_worker` resolve đúng binding của job/owner scope khi cần, không được cấp venue key hay tất cả AI key. |
| Privacy by policy | Chỉ sanitized projection allowlist được egress; raw account/order/secret/session/source không rời platform. |
| No hidden failover | Default không fallback. Fallback chỉ khi connection/profile được pre-approve trong cùng scope và cùng egress/capability class. |
| No trading dependency | AI failure không block strategy, risk, OMS, ledger, reconciliation hoặc replay. |

## 3. Thành phần và trust boundary

~~~text
Authenticated Account Owner
  | select provider/model/policy profile
  v
Control API
  | creates safe metadata / rotation command (no key)
  |
  +--> Operations metadata + audit (no raw secret)
  |
  +--> Isolated secret_ingress -- one-time write-only key --> Approved Secret Provider (raw key only)
  v
AI connection/profile policy
  | owner scope, catalog, egress, budget, timeout
  v
ai_worker machine identity
  | resolves one active binding just-in-time
  v
adapters/llm/<approved-provider>
  | TLS only to approved endpoint profile
  v
External AI provider
  | structured response only
  v
schema validation -> ai proposal/memory -> human/research workflow

No path exists from any box above to an execution port, venue credential,
risk/config promotion, deployment action, direct database write or trading tool.
~~~

| Component | Allowed responsibility | Explicitly forbidden |
|---|---|---|
| Dashboard | Display catalog/policy-profile/connection metadata; collect a key only through dedicated secure enrollment UI. | Store key in local/session storage, display/read back key, call provider directly. |
| Control API | Auth/RBAC/re-auth, connection lifecycle metadata, ordinary rotation/validation/activation command and safe audit. | Receive/process key body, put key in durable command/outbox/audit body, resolve/read key for UI. |
| `secret_ingress` | Isolated one-time enrollment session, reject secret-like reason, write raw key directly to secret provider, return safe receipt. | Enter normal Control API middleware/log/APM path, hash/fingerprint/persist key, or expose a reusable key/token. |
| Secret provider | Hold encrypted raw key and issue a narrow just-in-time binding. | Become a source of venue/execution permission. |
| `ai_worker` | Apply policy, resolve authorized binding, invoke adapter, validate output. | Receive trade key, execute tool, change risk/config/deployment or bypass egress policy. |
| Provider adapter | Translate canonical request/result and normalize errors/capabilities through approved egress gateway. | Guess model capability, accept arbitrary endpoint/proxy/redirect or write AI output directly to execution. |
| Operations/audit storage | Store lifecycle and usage metadata/hash. | Store raw key, authorization header, raw prompt/response by default. |

## 4. Canonical metadata

### 4.1 Provider catalog

`AIProviderCatalog` is operated by the platform, versioned and approved before a user can select an entry. Required metadata:

- `provider_id`, `catalog_version`, `adapter_id`, `adapter_version`, pinned adapter artifact digest, endpoint-profile ID and lifecycle status;
- `API_KEY` authentication mode for BYOK v1 and allowed environment; workload identity/OAuth needs a separate approved credential-flow contract;
- model profiles: `model_id`, provider model revision, structured-output/embedding capability, maximum context/output policy and deprecation status;
- data residency/retention/training terms classification, egress class, rate/cost limits and supported idempotency semantics;
- source/evidence, approval, capability-test and provider/model drift/deprecation reference.

The catalog may list examples such as OpenAI, Anthropic, Gemini, Azure-hosted, OpenAI-compatible gateway or private gateway, but an example is not an approved runtime selection. A new provider or endpoint family is a new adapter/capability/security change. An `ACTIVE` catalog entry is immutable: hostname/SNI/route, retention/residency, adapter digest, model capability or commercial terms change must create a new reviewed catalog/policy version; affected connections are revalidated, suspended or expired by policy.

### 4.2 User provider connection

`AIProviderConnection` stores no secret. It holds:

| Field group | Safe metadata |
|---|---|
| Identity/scope | `connection_id`, owner scope ID/type, environment, revision, lifecycle status. |
| Selection | provider/model/catalog/adapter profile IDs, artifact digest and versions. |
| Secret binding | internal opaque `active_binding_id` and `candidate_binding_id`; no mapping/reference is returned by public API/UI/event. `PENDING_SECRET` has neither; candidate never serves inference. |
| Policy | approved policy-profile ID/version resolved to endpoint, data-egress and usage/budget/timeout/rate/circuit policy IDs/versions plus purpose allowlist. |
| Audit | creator/actor, created/validated/activated/rotated/revoked timestamps and safe normalized result code. |

Connection lifecycle:

~~~text
DRAFT -> PENDING_SECRET -> PENDING_VALIDATION -> ACTIVE
         |                    -> VALIDATION_FAILED -> PENDING_SECRET (explicit retry)
ACTIVE -> ROTATION_PENDING_SECRET -> ROTATION_PENDING_VALIDATION -> ACTIVE
             (old active binding remains eligible; candidate failure discards candidate)
any non-terminal state -> SUSPENDED | EXPIRED | REVOKED
(SUSPENDED, EXPIRED and REVOKED are terminal in BYOK v1; recovery requires a new,
 separately reviewed connection lifecycle, never an implicit resume of this connection.)
~~~

`ACTIVE`, `ROTATION_PENDING_SECRET` and `ROTATION_PENDING_VALIDATION` may use only the existing `active_binding`; candidate binding is validation-only. Replacing a key creates a new opaque binding/revision; it does not mutate a secret value in place. Atomic activation swaps bindings only after candidate success, and validation failure leaves the old active binding untouched.

An opaque active binding ID may be retained on a terminal connection only for retention/audit. The worker must never resolve it after `SUSPENDED`, `EXPIRED` or `REVOKED`. BYOK v1 has no unsuspend/reactivate route for the same connection; recovery creates a new, reviewed lifecycle.

### 4.3 AI profile and provenance

An AI job/proposal pins the selected connection revision, provider/model/catalog/adapter version, prompt-policy/template version, egress/budget policy hash, input classification, structured-output schema ID/hash, timing, normalized result and usage/cost metadata. It must not pin or expose raw credential material.

## 5. Secure connection flows

### 5.1 Create and enroll a connection

~~~text
Account Owner -> Control API: choose approved provider/model/policy profile + reason
Control API -> policy/RBAC: verify owner scope, re-auth, catalog/profile compatibility and egress eligibility
Control API -> operations metadata: create PENDING_SECRET connection (no key)
Account Owner -> secret_ingress: submit key one time via protected write-only path/session
secret_ingress -> secret provider: write encrypted candidate secret and return opaque binding ID only
secret_ingress -> operations audit: record safe enrollment success/failure metadata, never request body/hash/fingerprint
Control API -> Account Owner: safe connection metadata; no key, secret ref or provider raw response
~~~

Preferred implementation is a single-use direct-vault enrollment session. For browser UI, Control API creation returns a short-lived Secure/HttpOnly/SameSite cookie scoped only to the isolated enrollment path; browser JavaScript cannot read it and the response is `Cache-Control: no-store`. The canonical HTTP route is physically served by `secret_ingress`, not the normal Control API process; it writes directly to the approved secret provider and keeps the raw field out of normal request logs, proxy/WAF/APM, command persistence, tracing and error handling. It uses no `Idempotency-Key`, body hash or key fingerprint. If the client loses a response, it reads safe connection status and never automatically posts a key again. PostgreSQL storage of a key or encrypted key blob is prohibited.

### 5.2 Validate and activate

~~~text
Account Owner + Security review -> Control API: validate/activate request with reason + re-auth
Control API -> approval workflow: require Account Owner + Security/Backup Owner role records
Control API -> ai_worker validation job: scoped minimal synthetic/sanitized probe against candidate binding
ai_worker -> policy: catalog capability, owner scope, egress and bounded quota check
ai_worker -> secret provider: resolve one binding just in time
ai_worker -> provider adapter: minimal request, no trading data
adapter -> ai_worker: normalized capability/result, raw vendor payload redacted
ai_worker -> Control API: safe status + metadata
Control API -> audit: lifecycle event without secret
~~~

The validation endpoint must not infer a key is valid merely because a network request reached an endpoint. It records a normalized capability outcome and leaves an initial connection inactive on uncertain, denied or invalid results. Activation atomically swaps a validated candidate into `active_binding`; for rotation, old binding remains active until this transaction completes.

### 5.3 Rotation, suspension and revoke race

~~~text
Account Owner -> Control API: start rotation command (no key)
Control API -> operations: ACTIVE -> ROTATION_PENDING_SECRET; active binding stays usable
Account Owner -> secret_ingress: one-time candidate key enrollment
secret_ingress -> secret provider: candidate binding only
Control API -> ai_worker: validate candidate with synthetic/sanitized probe
approval workflow -> Control API: dual-role approval
Control API -> operations + secret provider: atomic candidate -> active cutover; retire old binding
candidate failure -> discard candidate + stay ACTIVE

Security incident -> suspend/revoke: invalidate new leases immediately
ai_worker -> policy: recheck connection revision immediately before egress
in-flight request -> cancel when supported; discard result if revocation wins
~~~

Suspend/revoke commands have ordinary owner-scope authorization; Security/Backup Owner may issue an emergency unilateral suspension/revocation with re-auth/reason/audit and mandatory Account Owner notification/review. A binding lease is short, owner/connection/revision/job-bound, not reusable and zeroized after use. Revocation cannot unsend an already departed external request, but it must stop new egress and prevent its output from being committed.

### 5.4 Inference and failure

~~~text
ai_worker -> policy: verify active binding state/revision + scope + profile/egress + budget reservation
ai_worker -> secret provider: resolve short-lived active binding lease just in time
ai_worker -> policy: recheck state/revision before egress
ai_worker -> adapter/egress gateway: canonical sanitized request, no tools, approved host/SNI/TLS only
adapter -> provider -> adapter: structured response or normalized error
ai_worker -> validator: schema/provenance/budget reconciliation
ai_worker -> ai_memory: proposal/memory only when validation passes
failure -> AI capability suspended/failed per policy; trading path is unchanged
~~~

If outcome is unknown after request departure, do not blind retry or send the same data to another provider. There is no automatic cross-provider fallback by default. Redirects, caller-provided proxies, DNS rebinding and private/link-local destination resolution are denied before network egress except a named approved private route.

## 6. Port and adapter contract

Ports remain framework- and provider-free. Provider SDK/HTTP client lives only in `adapters/llm/<provider>`.

| Port | Canonical responsibility |
|---|---|
| `AIInferencePort` | `generate_structured` using a declared output schema; returns provider/model/catalog/adapter provenance and normalized usage/status. |
| `EmbeddingProviderPort` | Optional embedding operation for approved retrieval only. |
| `AIProviderCatalogPort` | Resolves versioned provider/model capability profile; denies unknown/deprecated profiles. |
| `AIPolicyProfilePort` | Resolves one approved provider/model/environment profile to pinned endpoint, data-egress and usage policies; callers cannot select sub-policy IDs freely. |
| `AIConnectionValidationPort` | Performs a bounded non-trading probe and returns normalized validation outcome. |
| `AIConnectionRepositoryPort` | Reads/writes connection metadata with owner scope/version checks; never stores raw key. |
| `AISecretResolverPort` | Adapter/composition-only short-lease active-binding resolution, not a domain service and not available to UI/domain/execution. |
| `AIEgressGatewayPort` | Enforces endpoint profile hostname/SNI/TLS/DNS/redirect/private-route decision before adapter network call. |

Canonical adapter result includes `provider_id`, `model_id`, catalog/adapter version, internal run ID, structured schema ID/hash, usage/cost metadata, normalized status/error and redacted request reference/hash. It excludes raw key, authorization header and raw vendor payload.

## 7. Data egress, budget and fallback rules

### Data egress policy

- Allow input only from sanitized projection fields explicitly declared for purpose/profile.
- Deny secrets, venue credentials, session artifacts, raw private account/order payload, full audit evidence, unapproved source code and unneeded identifiers.
- Pseudonymize account/order/strategy identifiers where semantic identity is not needed.
- Egress only to the endpoint profile resolved by an ACTIVE policy profile through approved TLS/network route; gateway enforces hostname/SNI allowlist, redirect deny, DNS-at-gateway and private/link-local deny unless the profile names an approved private route. Provider term/residency/retention classification must satisfy the selected policy.
- Raw prompt/response retention is disabled by default. Any exception requires a separate retention/classification decision and owner consent.

### Budget and rate limit

Policy defines hard limit by owner scope, connection, provider/model, environment and purpose, including daily/monthly cost, concurrency, RPM/TPM, max token and timeout. The worker reserves a bounded upper cost before call and reconciles actual usage afterward. If reservation fails, it denies the AI request without calling the provider.

### Fallback/retry

- BYOK v1: fallback is `DISABLED`; no request is moved to another provider/key.
- Same-provider retry only when the adapter proves the request did not leave the system or the provider supports the required idempotency semantics.
- A future fallback requires a new approved contract/profile, same owner scope, equivalent egress/capability/output schema and available budget; it is audited.
- `AI_OUTCOME_UNKNOWN` blocks blind retry/fallback and is handled as a controlled AI failure, never as a trading incident unless another independent trading control is affected.

## 8. Required controls and tests before implementation

- Fake/disabled provider is the default for local/CI; no real key or external provider request in CI.
- Test provider/model/endpoint/policy-profile allowlist rejection, arbitrary URL/proxy rejection, adapter capability drift and deprecation/retirement behavior.
- Test no key or key hash/fingerprint in API response, log, proxy/WAF/APM, trace, error, event, audit, database dump, fixture, browser storage or prompt; enrollment route is no-store and lost response never auto-resubmits key.
- Test initial PENDING_SECRET, candidate rotation, atomic cutover/candidate rollback, dual-role validate/activate and owner-scope isolation; a connection cannot be enumerated, used, rotated or revoked across owner scope.
- Test redaction/data-egress/DNS/redirect/private-route deny, atomic budget reservation under concurrency, rate/timeout/circuit behavior and no blind fallback.
- Test invalid structured output/provenance cannot create an approved proposal/memory record.
- Test suspend/revoke lease invalidation, recheck-before-call, zeroization and discard of invalidated in-flight output; test Security emergency suspend/revoke notification/review.
- Test `ai_worker` has zero execution/venue/risk/config/deploy/tool capability.
- Run revoke/rotation, provider outage, budget exhaustion and suspected key exposure drills.

## 9. Approval gates

Before any provider runtime or key enrollment, ADR-0008 and ADR-0016 must be `APPROVED`, OD-008 resolved, auth/machine identity and secret topology approved, provider catalog/capability evidence reviewed, and Phase 6 gate evidence complete. This document never upgrades Phase 0.0, Phase 6 or any security gate by itself.

## 10. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.2.0 | 2026-08-02 | Bổ sung changelog + row Change summary theo GOV-DOC-001 §3 (audit toàn diện); thêm SEC-AI-001 vào Related requirements. Nội dung kiến trúc không đổi. | Technical Operator | Pending |
| 0.1.0 | 2026-07-31 | Khởi tạo kiến trúc AI đa provider/BYOK (DRAFT Phase 6): catalog, connection lifecycle, secret ingress write-only, egress/budget policy, failure isolation. | Technical Operator | Pending |
