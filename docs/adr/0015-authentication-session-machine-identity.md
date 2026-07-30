# ADR-0015 — Control-plane authentication, session model, machine identity and authorization

| Thuộc tính | Giá trị |
|---|---|
| Status | DRAFT — required before Phase 3; provider/session choice unresolved |
| Date | 2026-07-31 |
| Owner | Security/Backup Owner |
| Approver | Account Owner |
| Related | FR-OPS-001, NFR-SEC-001, NFR-AUD-001, NFR-OPS-001; [Master](../../AI_AUTO_TRADE_MASTER_SPEC.md) §0.3 OD-006, §11.2–§11.4, §12; docs/06-security-ops access/auth artifacts |
| Supersedes / superseded by | None / None |

## Context and decision drivers

Control actions affect deployment, strategy, reconciliation and kill switch. Authentication provider/session lifecycle/machine identity are open under OD-006. A local bootstrap loopback API cannot be carried implicitly into external venue/testnet operation, and anonymous/shared credentials cannot produce trustworthy audit.

## Proposed decision

No provider, token/session format, external network exposure or human identity is selected by this DRAFT. Before Phase 3, an approved design must define provider, human auth/session lifecycle, machine identities per process, credential issuance/rotation/revocation, loopback/bootstrap transition, network restrictions, RBAC/permission matrix, re-auth for dangerous action, service-to-service authentication, audit correlation and incident/break-glass process.

Non-negotiable proposed constraints: every command has actor or machine identity; dashboard has no direct DB/venue access; Control API creates auditable command/approval evidence then owner handler acts; manual order endpoint is absent in MVP; dangerous kill/release/config/deployment actions require role and re-auth; AI has no execution identity; no shared trade credential between unrelated processes/environments.

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| Leave local API unauthenticated for testnet | creates silent privilege escalation when network/venue capability changes |
| One shared admin/API token | no actor attribution, least privilege or revocation boundary |
| UI directly calls DB/venue | bypasses authorization/audit/OMS/risk contract |
| Choose a provider now without constraints/owner input | provider choice affects security, operations and account environment |

## Consequences

Phase 3 remains BLOCKED until OD-006, permission matrix, threat model, access-control/auth-session policy and provider/machine identity evidence are approved. API contract must state auth/error/idempotency/precondition behavior. Auth logs/audit must redact secret while retaining identity/action/reason/correlation.

## Migration, rollout and rollback/forward-fix

No auth deployment now. Future rollout begins local loopback/bootstrap only, then approved human/machine identities in testnet scope with revoke/expiry/test evidence. Provider/session change requires compatible migration, audit continuity, key rotation/revocation plan and rollback/forward-fix; it cannot invalidate existing audit facts.

## Approval criteria

- [ ] OD-006 resolved with provider/session/machine/network decision and Security/Backup Owner review.
- [ ] Access-control matrix and dangerous-action re-auth/authorization tests pass.
- [ ] Audit/secret-redaction/revocation/break-glass runbooks are reviewed before external venue command.

