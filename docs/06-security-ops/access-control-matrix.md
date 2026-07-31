# SEC-002 — Access-control matrix

| Trường | Giá trị |
|---|---|
| Version / Status | 1.1.0 / IN_REVIEW |
| Owner / Approver | Security/Backup Owner / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | NFR-SEC-001, NFR-AI-001, SEC-AUTH-001, SEC-AI-002, SEC-AI-003; ADR-0007, ADR-0015, ADR-0016; contracts/api/openapi.yaml |
| Change summary | RBAC baseline independent of authentication provider, gồm owner-scoped AI BYOK connection lifecycle; provider selection remains OD-006/OD-008. |

## 1. Rules

Authorization is evaluated server-side for every command and data scope. A dashboard/client claim never grants access by itself. All machine identities are separate from human identities, non-interactive, scoped to one process/environment and cannot impersonate a human.

`Viewer`, `Technical Operator`, `Risk Approver`, `Security/Backup Owner` and `Account Owner` are roles, not credentials. One person may hold more than one role before canary, but audit records the active role/action separately. Canary/live safety/security approval requires the independent human review rule in master §1.6.

## 2. Human action matrix

| Action | Minimum role | Scope / conditions | Re-auth | Reason + immutable audit |
|---|---|---|---|---|
| Read health, readiness, sanitized projection | Viewer | Authorized environment/data scope | No | Correlation/access audit as policy requires |
| Read order/fill/portfolio/audit/incident | Viewer | Sanitized, least-data scope | No | Yes for sensitive audit export |
| Request reconciliation | Technical Operator | Environment/account scope | No | Yes |
| Activate kill switch | Technical Operator | Explicit scope, authenticated actor | No additional re-auth | Yes |
| Release kill switch | Risk Approver + Account Owner | Reconciliation/health preconditions met | Yes | Yes |
| Activate/stop paper strategy | Technical Operator | Approved paper manifest | No | Yes |
| Approve pending risk intent | Risk Approver | Fresh risk evaluation remains mandatory | Yes | Yes |
| Change risk policy or deployment | Risk Approver + Account Owner | Versioned immutable input / policy scope | Yes | Yes |
| Approve canary | Account Owner + Risk Approver | Gate and cap scope | Yes | Yes |
| Rotate credential/topology | Security/Backup Owner | New immutable manifest/restart; no raw secret | Yes | Yes |
| Read AI provider/model catalog | Viewer | Catalog entries only; no connection metadata or secret binding | No | Access audit as policy requires |
| Create AI connection metadata | Account Owner | Own owner scope; provider/model/profile must be ACTIVE in catalog | Yes | Yes |
| Enroll candidate AI provider key (initial/rotation) | Account Owner | Isolated one-time write-only secret ingress; no read-back, no Idempotency-Key/body hash/fingerprint or raw request persistence | Yes | Yes |
| Validate AI connection | Account Owner + Security/Backup Owner | Own scope, bounded synthetic/sanitized probe, egress/budget policy valid | Yes | Yes |
| Activate AI connection/candidate rotation | Account Owner + Security/Backup Owner | Own scope; catalog/egress/budget policy and lifecycle preconditions; both role records required | Yes | Yes |
| Suspend/revoke own AI connection | Account Owner | Own scope; re-auth, reason and audit; upstream revoke status stays unverified until provider evidence | Yes | Yes |
| Emergency suspend/revoke AI connection | Security/Backup Owner | Security incident/egress/key compromise; re-auth, reason/audit, Account Owner notification and post-containment review | Yes | Yes |
| Read AI connection metadata | Account Owner | Own scope, sanitized metadata only | No | Yes |
| Restore backup / alter incident evidence | Security/Backup Owner + required gate approver | Isolated restore first; no destructive shortcut | Yes | Yes |

No role has an MVP manual-order endpoint, direct venue console through Control API, raw secret/key read, audit-history delete, risk bypass or unilateral canary/provider activation permission. Security/Backup Owner may suspend/revoke an AI connection but cannot read its key.

## 3. Machine/process matrix

| Identity | Allowed | Explicitly denied |
|---|---|---|
| control-api | Control/operations write via approved handler; read sanitized projections | Venue trade credential, direct order submit, DB superuser |
| trading-node | Required market/strategy/risk/execution/ledger DB access; mode-allowed venue credential | Public management surface, credential rotation, raw secret export |
| data-worker | Market/reference ingest, data quality/catalog write | Trade credential, risk/ledger/execution write |
| research-worker | Catalog/read research candidate write | Trading OLTP write, external network by default, trade credential |
| ai-worker | Sanitized projection read, policy-filtered connection metadata, AI-memory proposal write; just-in-time active binding resolution for authorized owner/job | Execution tool/write, venue credential, raw-key read-back, cross-owner binding, manifest/config promotion, arbitrary endpoint |
| secret-ingress | One-time re-authenticated enrollment-session validation, direct provider-secret write and safe lifecycle receipt only | Normal command/event/outbox/audit body persistence, raw-body log/hash/fingerprint, provider inference, venue credential or broad DB access |
| CI | Validate/build in ephemeral environment | Real secret, real venue, canary/live DB/account |

Each process uses a separate database role. Database superuser is reserved for controlled infrastructure administration and never application runtime.

## 4. Enforcement requirements

- Ordinary command request needs authenticated actor, role evaluation, route scope, idempotency key/hash, correlation ID and immutable audit before/after hash. Isolated secret enrollment is the narrow exception: it uses an internal one-time enrollment session and must never hash/fingerprint/persist the key body.
- Dangerous actions need re-auth proof acceptable to the future ADR-0015 provider, explicit reason and high-risk audit event. Missing/expired proof is deny.
- Authorization failures return the standard safe `AUTHENTICATION_REQUIRED` or `AUTHORIZATION_DENIED` envelope; never reveal another account/resource existence.
- Query pagination/filter must be constrained by authorized scope; export and audit read require redaction/classification policy.
- Role grants/revocations are auditable and apply with bounded session/token lifetime. No shared human token.
- AI connection identifier/binding lookup is owner-scope checked before existence disclosure; public API returns only safe lifecycle metadata and never `secret_ref`/key material.
- Secret enrollment is handled outside durable command/event persistence by the isolated ingress/vault handoff. A normal operation command may record lifecycle state/reason, never secret input; secret-like text in reason is rejected before audit persistence.

## 5. Review and test evidence

Policy tests must cover deny-by-default, cross-environment/account/owner denial, role escalation denial, stale session/re-auth denial, machine/human impersonation denial, kill-switch release dual-role condition, AI validate/activate dual-role condition, emergency suspend/revoke notification path, AI connection read/use/rotate/revoke cross-owner denial, no raw key read-back/hash/fingerprint, secret-like reason rejection and audit completeness. Provider-specific mappings are blocked until ADR-0015 and ADR-0016 are `APPROVED`.
