# SEC-AI-POL-001 — AI BYOK security and data-egress policy

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.0 / DRAFT — Phase 6 only |
| Owner / Approver | Security/Backup Owner / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | FR-AI-001, NFR-AI-001, SEC-AI-001–003; ADR-0008, ADR-0015, ADR-0016; SEC-001–004, OPS-001, RB-009 |
| Change summary | Consolidated mandatory policy for user-supplied AI provider keys, provider/model egress and AI failure isolation. |

> This policy is intentionally provider-neutral. It does not select OpenAI, a secret-vault product, an identity provider or a runtime endpoint. It authorizes no key enrollment or external provider call until the referenced ADR/OD/gate conditions are approved.

## 1. Control objective

Allow an Account Owner to use their own key with an approved AI provider/model without granting the key, provider or model any trading authority. Protect the key and data egress, make cost/use auditable, and ensure AI failure cannot alter strategy/risk/OMS/ledger behavior.

## 2. Credential boundary

| Requirement | Mandatory behavior |
|---|---|
| Input | API key is accepted only at authenticated, re-authenticated, transport-protected **isolated secret-ingress** for an existing owner-scoped connection. The ingress writes directly to the approved secret provider and is not a normal Control API middleware path. |
| Storage | Raw key lives only in the approved secret provider. PostgreSQL stores opaque metadata/binding ID; public API/dashboard never receives secret reference resolution. |
| Read-back | Prohibited for every role, including Account Owner and Security/Backup Owner. A user can replace/rotate, not retrieve, a key. |
| Processing | Normal Control API command/event/outbox/audit pipeline, app logs, proxy/WAF/APM, traces, errors, fixtures, browser storage and backups cannot receive raw key/body. The ingress uses a server-side one-time enrollment session, `Cache-Control: no-store`, and never uses Idempotency-Key/body hash/key fingerprint. |
| Runtime use | `ai_worker` resolves a single active binding just in time for authorized owner/job with a short owner/connection/revision/job lease. It does not receive a global key environment or venue key. |
| Rotation/revoke | Keep the old active binding during candidate enrollment/validation, atomically cut over only after validation, then retire old binding. Suspend/revoke invalidates issuance immediately; worker rechecks revision before outbound call, zeroizes after use, cancels when possible and discards revoked in-flight output. `SUSPENDED`, `EXPIRED` and `REVOKED` are terminal in v1: an opaque binding ID may remain only for retention/audit and is never resolvable; recovery is a new reviewed connection lifecycle. A disconnect only proves platform stop-use unless upstream revocation is verified. |

Forbidden shortcuts: storing encrypted key blobs in PostgreSQL, config/YAML/manifest secret values, passing key through AI prompt, generating a key fingerprint/last-four/payload hash for UI/idempotency, copying key to an incident ticket, blindly retrying enrollment after lost response or trusting client-side key masking as protection.

## 3. Provider, model and endpoint control

- The only selectable entries are `ACTIVE` provider/model profiles in the versioned catalog.
- A catalog entry pins adapter/version/**artifact digest**, opaque approved endpoint profile, `API_KEY` authentication mode in BYOK v1, allowed environment, structured-output capability, egress class, terms/residency/retention policy reference and limit policy. It is immutable once ACTIVE; change creates a new reviewed version.
- A provider/model/endpoint supplied by a user that is not catalog-approved is denied before DNS/network activity.
- OpenAI-compatible does not imply trusted or approved. Private/local gateways require an approved endpoint profile, network policy and adapter capability review. Egress gateway enforces hostname/SNI allowlist, TLS validation, redirect deny, gateway-only DNS resolution and deny of private/link-local addresses except a named approved-private route; provider adapter cannot use caller proxy/base URL/environment override.
- Provider SDK, HTTP client and credentials reside only behind `adapters/llm/<provider>` and composition wiring. Domain/application code never imports a provider SDK or resolves secret.
- Tool/function calling is disabled. No adapter may expose execution, venue, database, filesystem, browser or unbounded network capability to a model.

## 4. Owner scope and authorization

Initial MVP scope is one authenticated Account Owner + account environment. This is not a claim of multi-tenant support. Future workspace/tenant/user sharing requires a new ADR, schema version and access-control review.

| Action | Required authorization |
|---|---|
| View catalog/model profile | Viewer in authorized scope; catalog metadata only. |
| Create connection / start rotation / enroll candidate key | Account Owner for own scope, re-auth, explicit reason. Enrollment needs a one-time secret-ingress session; secret-like reason is rejected before audit. |
| Validate/activate/egress or budget policy change | Account Owner plus Security/Backup Owner review, re-auth and audit. |
| Suspend/revoke | Account Owner may suspend/revoke own scope with re-auth/reason/audit. Security/Backup Owner may emergency suspend/revoke unilaterally for incident containment, then must notify Account Owner and complete post-containment review; never read key. |
| Resolve binding/use provider | `ai_worker` machine identity for an ACTIVE connection and authorized owner/job only. |
| Read raw key | No role. |

Connection lookup must be scope-checked before resource-existence disclosure. Errors are normalized as `AI_CONNECTION_SCOPE_DENIED`/safe not-found behavior, never reveal another owner’s connection or binding.

## 5. Data-egress and privacy policy

Before each call, the worker checks connection state, owner scope, provider/model capability, purpose, data classification, egress policy and hard budget reservation. Only an explicit sanitized projection allowlist may leave the platform.

Never egress: venue credential, session/auth artifact, raw API key, secret reference resolution, raw private account/order/balance payload, full audit evidence, unapproved source code, customer identity that is not needed for the task, or data barred by residency/retention policy. Pseudonymize account/order/strategy identifiers when semantic identity is unnecessary.

Prompt, retrieved memory and provider response are untrusted data. Structured output/provenance validation is required before proposal/memory persistence. Raw prompt/response retention is off by default; any retention needs a named classification, legal/terms/residency decision, retention period and owner approval.

## 6. Budget, rate, failure and fallback

- Hard limits apply by owner scope, connection, provider/model, environment and purpose: daily/monthly cost, token counts, concurrency, RPM/TPM and timeout.
- Reserve bounded budget atomically before network call; reconcile actual usage afterwards. Reservation failure denies the AI request without calling provider.
- Provider/key/model invalid, quota/rate breach, timeout, circuit open, output invalid or unknown outcome disables/fails AI capability safely. Candidate rotation failure destroys candidate and retains old active binding; initial validation failure has no active binding. Trading remains independent.
- Default is no automatic fallback. An explicit fallback requires the same owner scope, equivalent egress/capability/output schema, approved policy and available budget; it is audited.
- An uncertain request outcome is `AI_OUTCOME_UNKNOWN`; do not blind retry or send the content to a different provider.

## 7. Safe telemetry, audit and retention

Allowed telemetry/audit: actor/owner scope, opaque connection ID/revision, provider/model/catalog/adapter artifact/policy versions, purpose/classification, timing, normalized result/error code, usage/cost metadata, correlation ID, re-auth/approval outcome and hash of sanitized canonical input when policy allows.

Prohibited telemetry/audit: raw key, authorization header, raw secret reference, provider raw error/payload, raw prompt/response by default, key fingerprint/length, session artifact or another owner’s metadata.

Security alert is High/Critical for suspected key leak, unauthorized egress, arbitrary endpoint attempt that evades policy, cross-owner binding use or failed revoke. Provider latency/quota/output failure is Low/Medium unless it exposes data/security; it never masks trading alerts.

## 8. Verification and gate

Before Phase 6 enablement, prove:

- secret enrollment and key rotation are write-only/no-store/no-body-hash; no secret leaks through API, UI, logs, proxy/WAF/APM, traces, database, event, fixture, dump or backup;
- provider/model/endpoint/policy-profile allowlist, adapter-drift/deprecation and owner-scope isolation deny tests pass;
- egress redaction/classification, DNS/redirect/private-route deny, quota reservation/concurrency, timeout/rate/circuit and no-silent-fallback tests pass;
- fake/disabled provider is default for CI and no real provider/key call occurs in CI;
- zero AI-to-execution/venue/risk/config/deployment tool path is demonstrated;
- initial/rotation lifecycle, dual-role validate/activate, emergency suspend/revoke notification, binding lease/revoke in-flight and secret-like audit reason rejection tests pass;
- RB-009 provider/key incident and revoke/rotation/outage/budget drills have approved evidence.

This policy remains DRAFT until ADR-0008, ADR-0016, OD-008, secret topology, auth/machine identity and Phase 6 gate are approved.
