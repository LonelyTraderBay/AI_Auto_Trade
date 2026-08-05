# RB-007 — Credential revocation and rotation

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.1 / DRAFT |
| Owner / Approver | Security/Backup Owner / Account Owner (pending) |
| Effective date / Last review | Chưa hiệu lực / 2026-08-02 |
| Trigger / Severity | Scheduled rotation, provider/venue revocation, privilege drift, suspected exposure or personnel/access change / High; Critical for possible trade credential compromise |
| Scope / Incident commander | Credential reference/environment/process/account scope / Security/Backup Owner |
| Related | NFR-SEC-001, SEC-AUTH-001; ADR-0010, ADR-0015; SEC-004; RB-004, RB-008; OPS-001 |
| Change summary | Rotation procedure using references/manifest, never secret values. 1.0.1 (2026-08-02): bổ sung Owner/Approver + Effective/Last review theo GOV-DOC-001 §3 (audit toàn diện). |

## Safe-state objective

No raw secret is revealed. A credential class/mode/account cannot change in a running process. Suspected exposure is contained first; a replacement credential does not itself prove safety or authorize resume.

## Procedure

1. Open incident/change record with reference ID/class (never value), owner, environment/process, reason, scope, creation/expiry policy and affected manifest IDs. For suspected compromise, activate kill switch for trading scope under RB-004.
2. Confirm target privilege: unique environment/account/process, least privilege, no withdrawal for trade key, approved IP/network restrictions and class permitted by deployment matrix. Reject privilege escalation or cross-environment reuse.
3. Security/Backup Owner provisions/revokes through approved provider procedure. Record only audit metadata and verification result; do not paste key/token, secret URI resolution or provider raw payload.
4. Create a new immutable approved deployment/config manifest referencing the new secret reference. Do not hot-edit the running manifest, modify environment mode or silently reload a credential.
5. Restart/roll over process following RB-005. Validate identity/privilege using safe approved method, then reconcile account/orders/fills/balances because prior external operations may be uncertain.
6. Revoke/retire prior material only after replacement and reconciliation plan are verified, except immediate compromise containment where revocation happens first. Review audit activity from last trusted point.

## Verify and close

Evidence proves old reference revoked/retired as policy requires, new reference is not exposed, correct class/environment/process binding, no withdrawal permission, manifest/config hash changed under approval, process least-privilege verification and reconciliation/health completion. Risk/Account Owner joins closure for canary/live impact.

## Escalation and evidence

Escalate Critical for suspected live trade key exposure, withdrawal privilege, impossible revocation, unauthorized use, secret logged/committed or cross-environment credential. Preserve access/rotation audit metadata, command/manifest hashes, incident timeline and reconciliation result; rotate any derivative access as provider policy requires.

