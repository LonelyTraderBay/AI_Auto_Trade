# Contract — Error catalog v1

| Trường | Giá trị |
|---|---|
| Contract ID / Version / Status | C-ERR-001 / 1.1.1 / IN_REVIEW |
| Owner / Approver | Technical Operator / Account Owner (pending) |
| Canonical path | `contracts/errors/error-catalog.md` |
| Effective date / Last review | Chưa hiệu lực / 2026-08-02 |
| Related | FR-OPS-001, FR-AI-001, NFR-SEC-001, NFR-AI-001; ADR-0005, ADR-0007, ADR-0012, ADR-0015, ADR-0016; C-API-001 |
| Change summary | 1.1.1 (2026-08-02): chuẩn hóa version 2 thành phần "v1.1" thành semantic version 3 thành phần theo GOV-DOC-001 §3; bổ sung Effective date/Last review (audit toàn diện — không đổi code/HTTP mapping nào, vẫn 26 code). 1.1.0 trở về trước: safe error vocabulary and HTTP mapping for OpenAPI v1 skeleton, gồm BYOK AI provider errors không lộ key/provider raw payload. |

## 1. Envelope invariant

Every public error response uses the OpenAPI `ErrorEnvelope`:

~~~json
{
  "code": "MACHINE_READABLE_CODE",
  "message": "Safe human-readable summary",
  "details": {},
  "correlation_id": "uuidv7",
  "retryable": false,
  "remediation_hint": "Safe next action"
}
~~~

No envelope contains stack trace, raw secret, authorization header, token, vendor raw payload, hidden resource existence, unredacted account data or PII not needed for remediation. `details` is structured and schema/route-specific; it never becomes an escape hatch for raw exception text.

## 2. Error codes

| Code | Default HTTP | Retryable | Meaning / safe remediation |
|---|---:|---|---|
| `VALIDATION_FAILED` | 400 | No | Request/schema/domain input invalid. Correct input; do not retry unchanged. |
| `AUTHENTICATION_REQUIRED` | 401 | No | Actor/session absent, expired or invalid. Authenticate/re-authenticate through approved flow. |
| `AUTHORIZATION_DENIED` | 403 | No | Authenticated actor lacks role/scope. Do not reveal alternate resource state. |
| `IDEMPOTENCY_KEY_REUSED` | 409 | No | Same actor/route/key had a different canonical request hash. Use original command or a new key only for a new intent. |
| `PRECONDITION_FAILED` | 412 | No | `If-Match`/resource version or required safe state not met. Refresh/review state. |
| `COMMAND_NOT_FOUND` | 404 | No | Command is absent or not visible in authorized scope. |
| `RESOURCE_NOT_FOUND` | 404 | No | Non-command resource is absent or not visible in authorized scope. |
| `COMMAND_STATE_CONFLICT` | 409 | No | Transition not valid for current immutable command lifecycle. |
| `RISK_REJECTED` | 422 | No | Deterministic risk policy rejected intent. Review policy/input; do not bypass. |
| `RUNTIME_NOT_READY` | 503 | Yes after readiness recovers | Health/lease/config/reconciliation prerequisite is not met. Keep strategy disabled. |
| `RECONCILIATION_BLOCKED` | 423 | No | Scope has unresolved mismatch/unknown condition. Reconcile; do not force submit. |
| `KILL_SWITCH_ACTIVE` | 423 | No | Submission/action blocked by active kill switch. Release only through high-risk approved procedure. |
| `EXTERNAL_OUTCOME_UNKNOWN` | 409 | No | External submit/cancel result uncertain. Reconcile; never blind retry. |
| `AI_PROVIDER_NOT_ALLOWED` | 403 | No | Provider/endpoint profile is absent, inactive or not permitted in actor/environment scope. Select an approved catalog entry; do not provide an arbitrary URL. |
| `AI_MODEL_NOT_ALLOWED` | 403 | No | Model is not active/capable for the selected provider/profile. Select an approved model profile. |
| `AI_CONNECTION_SCOPE_DENIED` | 403/404 | No | Connection is absent or not visible in the owner scope. Do not reveal another owner's resource state. |
| `AI_CREDENTIAL_NOT_CONFIGURED` | 423 | No | Connection has no active opaque credential binding. Enroll/validate through the approved write-only flow. |
| `AI_CREDENTIAL_VALIDATION_FAILED` | 422 | No | Safe validation probe failed or is uncertain. Review connection/catalog/policy; no trading data was sent. |
| `AI_ENROLLMENT_NOT_PERMITTED` | 409 | No | Connection state/revision or one-time secret-enrollment session is not eligible. Read safe connection status; do not automatically resubmit a key. |
| `AI_EGRESS_POLICY_DENIED` | 403 | No | Provider/model/input/purpose violates the approved egress policy. Review policy; do not bypass or fallback silently. |
| `AI_BUDGET_EXCEEDED` | 429 | No | Hard budget/quota reservation failed. Wait for approved policy window/change; no provider request was made. |
| `AI_PROVIDER_UNAVAILABLE` | 503 | Conditional | Provider/rate/circuit failure affected only AI capability. Retry only by approved AI policy; trading remains unaffected. |
| `AI_OUTPUT_INVALID` | 422 | No | Provider output failed structured schema/provenance validation. No proposal/memory write occurred. |
| `AI_OUTCOME_UNKNOWN` | 409 | No | Provider request may have left the platform but outcome is uncertain. Do not blind retry or send data to another provider. |
| `SENSITIVE_INPUT_REJECTED` | 400 | No | Free-text reason/note appears to contain secret-like material. Remove it; never use an audit field to transmit a credential. |
| `INTERNAL_ERROR` | 500 | Conditional | Unexpected safe failure; correlation ID is evidence. Client retries only when `retryable=true` and policy allows. |

## 3. Compatibility and governance

Codes are stable within v1. Additive code may be compatible only when consumer behavior is documented; changing code meaning/default action is breaking and requires a new major contract/compatibility plan. Error behavior remains subordinate to master safety invariants: a `retryable` response never authorizes blind external submit retry.
