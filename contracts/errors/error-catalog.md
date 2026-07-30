# Contract — Error catalog v1

| Trường | Giá trị |
|---|---|
| Contract ID / Version / Status | C-ERR-001 / v1 / IN_REVIEW |
| Owner / Approver | Technical Operator / Account Owner |
| Canonical path | `contracts/errors/error-catalog.md` |
| Related | FR-OPS-001, NFR-SEC-001; ADR-0005, ADR-0007, ADR-0012, ADR-0015; C-API-001 |
| Change summary | Safe error vocabulary and HTTP mapping for OpenAPI v1 skeleton. |

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
| `INTERNAL_ERROR` | 500 | Conditional | Unexpected safe failure; correlation ID is evidence. Client retries only when `retryable=true` and policy allows. |

## 3. Compatibility and governance

Codes are stable within v1. Additive code may be compatible only when consumer behavior is documented; changing code meaning/default action is breaking and requires a new major contract/compatibility plan. Error behavior remains subordinate to master safety invariants: a `retryable` response never authorizes blind external submit retry.
