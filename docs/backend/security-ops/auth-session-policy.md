# SEC-003 — Authentication and session policy

| Trường | Giá trị |
|---|---|
| Version / Status | 1.1.1 / DRAFT |
| Owner / Approver | Security/Backup Owner / Account Owner (pending) |
| Effective date / Last review | Chưa hiệu lực / 2026-08-02 |
| Related | SEC-AUTH-001, SEC-AI-002, SEC-AI-003, NFR-SEC-001, NFR-AI-001; OD-006, OD-008; ADR-0015, ADR-0016; SEC-002 |
| Change summary | 1.1.1 (2026-08-02, Technical Operator soạn thay Owner, Pending): registry doc-ID trong DOCS_INDEX đổi thành SEC-AUTH-POL-001 (title SEC-003 giữ nguyên) để hết va chạm với requirement ID SEC-AUTH-001; ghi lineage version vào Change summary thay cho changelog table còn thiếu; thêm "(pending)". 1.1.0/1.0.0 (2026-07-31): provider-neutral mandatory controls, gồm re-auth/owner scope cho BYOK AI connection; không phải quyết định provider/session implementation. |

## 1. Decision boundary

Authentication provider, issuer, token/session format, MFA mechanism, identity lifecycle and production network topology are unresolved under OD-006 and require ADR-0015 before Phase 3. This document specifies non-negotiable behavior only; no service or secret is selected here.

Local Phase 0 may bind a bootstrap Control API to loopback only with no venue credential/external command. It is not an exemption to task audit or future provider enforcement.

## 2. Identity classes

| Class | Use | Required properties |
|---|---|---|
| Human actor | Control-plane reads/commands/approvals | Unique subject, active role(s), expiry/revocation, auditable authentication event. |
| Machine identity | One runtime process | Non-interactive, least privilege, environment/process-bound, rotatable, no human role. |
| CI identity | Build/validation only | Ephemeral, no trade/production secret, cannot deploy or approve gate. |
| Service integration | Future approved internal integration | Contract-scoped, time-bounded, no implicit role inheritance. |

Shared human accounts, static never-expiring sessions, credentials in URLs/logs and client-only authorization are prohibited.

## 3. Session/token behavior

- Default deny when issuer, audience, signature, expiry, environment, actor status or requested role/scope cannot be validated.
- Authorization is evaluated on each dangerous command and at session/token renewal; a cached dashboard permission is insufficient.
- Session lifetime, idle timeout, refresh policy, logout/revocation propagation and clock-skew tolerance must be explicit ADR-0015 fields. Until then no external control plane can start.
- Session artifacts must be transport-protected, not persist in browser local storage unless ADR-0015 evaluates the threat/control, and never appear in telemetry/evidence.
- CSRF protection is required for cookie-based sessions. Bearer/token flows require replay, audience and storage controls chosen in ADR-0015.

## 4. Re-authentication

Re-auth is mandatory for kill-switch release, canary approval, risk policy change, credential/topology rotation, deployment promotion, AI provider key enrollment/rotation/revoke, AI connection validation/activation and other policy-defined dangerous actions. Re-auth proof must be bound to actor, action class, target scope, issued/expiry time and correlation ID; it cannot be replayed for another action.

If re-auth fails/expired/uncertain, return safe authorization error, keep safe state and audit denial without recording the proof itself.

## 5. Audit, privacy and incident response

Audit records capture actor ID, active role, action, target scope, decision, reason, correlation ID, timestamp and before/after hashes where relevant. They never capture raw password, token, MFA code, cookie, authorization header or secret reference resolution.

For AI BYOK, target scope includes the owner scope and opaque connection ID. Authorization must deny connection enumeration/use outside that scope without disclosing whether another connection exists. Secret enrollment itself is handled by the isolated one-time ingress/vault handoff, not stored as an audit request body or Idempotency-Key/body hash; audit records only safe lifecycle/result metadata. Secret-like text in reason/note is rejected before audit persistence.

Suspected session compromise: revoke/disable according to provider procedure, activate safe state where scope could trade, open incident, assess commands since last trusted auth and re-authenticate only after Security/Backup Owner review. The provider-specific procedure is a Phase 3 dependency.

## 6. Acceptance before Phase 3

ADR-0015 must select provider/model and define identity provisioning/deprovisioning, human and machine authentication, session/re-auth TTL, CSRF/replay defense, key rotation, audit fields, emergency revocation, test strategy and failure behavior. ADR-0016 must additionally define owner-scoped AI connection lifecycle handoff, dual-role validation/activation and emergency suspend/revoke notification. Tests must prove the SEC-002 matrix, deny conditions, cross-owner AI connection denial and no secret/session artifact leakage.
