# ADR-0016 — Provider-neutral AI/BYOK connection, catalog and credential boundary

| Thuộc tính | Giá trị |
|---|---|
| Status | DRAFT — required before Phase 6; no AI provider runtime or user key is authorized |
| Date | 2026-07-31 |
| Owner | Technical Operator + Security/Backup Owner |
| Approver | Account Owner |
| Related | FR-AI-001, NFR-AI-001, SEC-AI-002, SEC-AI-003; [Master](../../AI_AUTO_TRADE_MASTER_SPEC.md) §6.4, §10.1, §10.6–§10.8, §11–§12, §14 Phase 6; ADR-0008, ADR-0015 |
| Supersedes / superseded by | None / None |

## Context and decision drivers

AI is optional and advisory only. The project already requires a separate `ai_worker`, a provider allowlist, structured output, budget/timeout/circuit breaker and zero execution/trade credential. It does not yet specify how a human user supplies an AI provider key, selects a model, controls cost/data egress or revokes a connection.

The product must not be locked to OpenAI. At the same time, accepting an arbitrary URL, model name or credential from a dashboard would create SSRF, credential theft, data-exfiltration, billing-abuse, supply-chain and cross-owner isolation risks. A provider outage or an invalid model must never alter trading, risk, OMS or ledger behavior.

## Proposed decision

### 1. Provider-neutral catalog, not arbitrary endpoint access

The platform uses versioned `AIProviderCatalog` entries and provider adapters at `adapters/llm/<provider>`. A catalog entry declares provider ID, approved endpoint profile, adapter/version/**artifact digest**, authentication mode, model profiles, structured-output/embedding capability, allowed environments, data-egress class, residency/retention/terms, rate/cost limits and lifecycle status. An `ACTIVE` entry is immutable; provider/model/adapter/terms/endpoint drift creates a new reviewed version and may require revalidation/suspension/expiry of affected connections.

No provider is mandatory; OpenAI is only one possible approved adapter. BYOK v1 admits only an `API_KEY` provider/model plus a compatible active `AIPolicyProfile`; the profile pins approved endpoint, data-egress and usage/budget policy and prevents a caller from choosing component IDs freely. Workload identity/OAuth needs a separate credential-flow contract. Custom OpenAI-compatible, local or private gateway support requires its own approved endpoint profile, adapter capability test, dependency/security review and catalog entry. The UI does not accept an arbitrary `base_url`, proxy, model ID or policy ID.

### 2. User-managed connection and ownership

An `AIProviderConnection` is metadata, not a secret. It has an opaque `connection_id`, owner scope, provider/model catalog version, resolved policy-profile IDs/versions, status, revision, internal opaque `active_binding` and `candidate_binding` IDs, and audit timestamps. `PENDING_SECRET` has neither binding; candidate binding is validation-only and never public API/event data. In the initial single-account MVP, owner scope is the authenticated Account Owner/account environment. A later multi-user or multi-tenant scope requires an approved extension; no connection may be implicitly shared across users or environments.

Lifecycle is:

~~~text
DRAFT -> PENDING_SECRET -> PENDING_VALIDATION -> ACTIVE
         |                    -> VALIDATION_FAILED -> PENDING_SECRET (explicit retry)
ACTIVE -> ROTATION_PENDING_SECRET -> ROTATION_PENDING_VALIDATION -> ACTIVE
             (old active binding stays usable; candidate failure discards candidate)
any non-terminal state -> SUSPENDED | EXPIRED | REVOKED
(SUSPENDED, EXPIRED and REVOKED are terminal in BYOK v1; recovery requires a new,
 separately reviewed connection lifecycle, never an implicit resume of this connection.)
~~~

Rotation starts with a normal durable command that carries no key, creates a new candidate binding/revision through secret ingress, validates it, then atomically switches the active binding. Active binding stays usable during rotation and a candidate failure cannot interrupt it. Revocation/suspension invalidates new binding leases immediately; worker must re-check connection revision immediately before egress, zeroize after use and discard an in-flight result if revocation wins. Disconnect removes platform access; it does not claim that an upstream provider key is revoked unless that provider procedure returns verified evidence.

A terminal connection may retain an opaque binding ID only for retention/audit; that binding is never eligible or resolvable for inference. BYOK v1 deliberately has no unsuspend/reactivate API for the same `connection_id`: recovery starts a new reviewed connection lifecycle.

### 3. BYOK credential ingress and storage

The user supplies a provider key only through a one-time, transport-protected, write-only secret-enrollment path. The canonical HTTP route is physically served by an isolated `secret_ingress` boundary (or direct-vault handoff) that writes directly to the approved secret provider; it is not a normal Control API middleware path. It uses a server-side one-time enrollment session bound to actor/owner/connection/revision, `Cache-Control: no-store`, and no Idempotency-Key, raw-body hash or key fingerprint. If the client loses the response, it reads safe connection status and never automatically submits a key again. The normal Control API command/event/audit pipeline never persists the raw input.

No raw key, encrypted key blob, authorization header, key fingerprint, key length, payload hash or recoverable derivative may appear in PostgreSQL, YAML, deployment manifest, browser storage, command/event/audit payload, log, proxy/WAF/APM, trace, fixture, backup, Markdown or API response. Database records only opaque internal connection/binding metadata; a synthetic opaque UUID may appear only in a schema fixture and never maps to a vault secret. Secret provider, encryption hierarchy, break-glass and production injection topology remain subject to OD-008 and the approved security decision; storing a user key in PostgreSQL is not an allowed fallback.

`ai_worker` resolves only the active binding required for an authorized job, just in time. It must not receive venue credentials or a broad environment containing every user key.

### 4. Egress, capability, budget and failure policy

Before an inference request, the worker verifies owner scope, active binding state/revision/lease, provider/model capability, adapter/catalog artifact version, resolved policy profile, data-egress policy, purpose and atomic budget/quota reservation. Only a sanitized, allowlisted projection may leave the platform. Egress is through an approved gateway that enforces hostname/SNI allowlist, TLS validation, redirect deny, gateway-only DNS resolution and private/link-local address deny except a named approved private route. Secret, venue credential, session token, raw private account/order payload, unapproved source code and unneeded identity data are prohibited. Prompt/provider output is untrusted data.

Tool/function calling is disabled by default. AI has no execution, risk, deployment, configuration, database, filesystem or browser tool. It can write only validated proposal/memory/post-mortem records through owned ports.

BYOK v1 has fallback `DISABLED`. A future retry/fallback needs a separate approved contract/profile that explicitly names an equivalent connection in the same owner scope, with equivalent egress class/capability/schema and sufficient budget. An unknown external outcome is never blind-retried or duplicated to another provider. AI failure disables the AI capability; trading continues independently.

### 5. Authorization and audit

No application role can read a raw provider key. Account Owner may create, enroll, rotate, revoke and request validation of a connection in their own scope with re-authentication and audit reason; reason is rejected before persistence if secret-like. Validate/activate requires recorded Account Owner and Security/Backup Owner roles. Security/Backup Owner reviews provider catalog, egress and activation policy and may emergency suspend/revoke unilaterally with re-auth/reason/audit and mandatory Account Owner notification/review, but cannot read raw key. `ai_worker` has a machine identity that may resolve only an active binding for the authorized owner/job. Viewer and Technical Operator receive sanitized metadata only.

Audit records connection lifecycle, actor/owner scope, catalog/policy/version, reason, correlation ID, validation result, usage/budget result and normalized error; they never record raw credentials or raw prompt/response by default.

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| OpenAI-only integration | Locks user choice, conflicts with provider-neutral adapter topology and creates avoidable vendor dependency. |
| Allow arbitrary URL/provider/model from UI | Enables SSRF, key exfiltration, unreviewed data egress and capability ambiguity. |
| Store encrypted user API key in PostgreSQL | Weakens secret boundary, backup handling and least privilege; violates the no-secret persistence rule. |
| Apply normal `Idempotency-Key` canonical body hashing to secret enrollment | Can retain a key fingerprint/derivative and makes retry semantics unsafe; isolated one-time ingress session is required. |
| One platform-owned shared AI key | Does not meet BYOK ownership/isolation needs and increases billing/data blast radius. |
| Silent fallback to any available provider | Can duplicate cost and send data to a different provider without explicit consent. |

## Consequences

The system gains user choice without making a particular provider mandatory. Each additional provider requires a narrow adapter/capability/security delivery unit rather than a speculative universal SDK. The initial implementation has more lifecycle/RBAC/observability work than a single static environment variable, but it keeps secret ownership, cost and data egress auditable.

This ADR does not authorize a live AI connection, secret, provider SDK, UI, endpoint, migration or external call. It also does not change ADR-0008: AI remains proposal-only and off the trading hot path.

## Migration, rollout and rollback/forward-fix

1. Documentation/contract baseline: catalog, connection metadata, secret-ingress semantics, policies and negative tests only.
2. Phase 6.0: disabled/fake provider, provider port/capability tests and no-execution tests.
3. Phase 6.1: one approved BYOK provider in sandbox/paper using synthetic/sanitized probe data; validate create/rotate/revoke/redaction/budget behavior.
4. Each additional provider or endpoint family: separate adapter/capability/security evidence and catalog approval.
5. Rollback: suspend/revoke the connection or disable `ai_worker`; no trading fact, risk decision, order, ledger entry or replay result depends on the provider.

## Approval criteria

- [ ] OD-008 is resolved with owner scope, provider/model catalog, legal/data-egress, budget/fallback and secret-provider topology evidence.
- [ ] ADR-0008 and applicable ADR-0015 controls are approved; AI machine identity/RBAC is testable.
- [ ] Catalog, endpoint, data-egress, usage, policy-profile, connection, command/event and isolated HTTP secret-ingress contracts are reviewed without any secret sample.
- [ ] Threat model, access matrix, credential policy, SLO/alert and runbooks cover enrollment leak, cross-owner access, provider outage, budget exhaustion, revoke/rotation and data-egress denial.
- [ ] Negative tests prove no key read-back/hash/fingerprint/logging, no arbitrary endpoint/proxy/DNS/redirect bypass, no cross-owner use, no execution tool and no silent cross-provider fallback.
- [ ] Initial/rotation candidate lifecycle, dual-role validation/activation, emergency suspend/revoke notification, adapter/catalog drift and binding-lease/revocation-in-flight behavior have approved test/drill evidence.
