# SEC-003 — Authentication and session policy

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.0 / DRAFT |
| Owner / Approver | Security/Backup Owner / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | SEC-AUTH-001, NFR-SEC-001; OD-006; ADR-0015; SEC-002 |
| Change summary | Provider-neutral mandatory controls. Không phải quyết định provider/session implementation. |

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

Re-auth is mandatory for kill-switch release, canary approval, risk policy change, credential/topology rotation, deployment promotion and other policy-defined dangerous actions. Re-auth proof must be bound to actor, action class, target scope, issued/expiry time and correlation ID; it cannot be replayed for another action.

If re-auth fails/expired/uncertain, return safe authorization error, keep safe state and audit denial without recording the proof itself.

## 5. Audit, privacy and incident response

Audit records capture actor ID, active role, action, target scope, decision, reason, correlation ID, timestamp and before/after hashes where relevant. They never capture raw password, token, MFA code, cookie, authorization header or secret reference resolution.

Suspected session compromise: revoke/disable according to provider procedure, activate safe state where scope could trade, open incident, assess commands since last trusted auth and re-authenticate only after Security/Backup Owner review. The provider-specific procedure is a Phase 3 dependency.

## 6. Acceptance before Phase 3

ADR-0015 must select provider/model and define identity provisioning/deprovisioning, human and machine authentication, session/re-auth TTL, CSRF/replay defense, key rotation, audit fields, emergency revocation, test strategy and failure behavior. Tests must prove the SEC-002 matrix, deny conditions and no secret/session artifact leakage.

