# RB-005 — Trading node crash or restart

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.0 / DRAFT |
| Trigger / Severity | Process crash, health failure, forced restart, lease heartbeat loss, configuration/image mismatch / High; Critical with in-flight external uncertainty or split brain |
| Scope / Incident commander | Affected runtime instance/deployment/account scope / Technical Operator |
| Related | FR-OMS-001, FR-REC-001, NFR-OPS-001; ADR-0004, ADR-0005, ADR-0012; RB-001, RB-003 |
| Change summary | Restart procedure that preserves fencing/idempotency/reconciliation. |

## Safe-state objective

One execution leader only. A lost/ambiguous lease blocks submission; in-flight external operations are treated as `UNKNOWN` until reconciled. Restart never changes run mode, credential class or manifest in place.

## Procedure

1. Capture incident scope, process exit/health reason, last heartbeat/fencing token, deployment ID, immutable manifest/config hash, image digest and active order/command counts.
2. Confirm old instance cannot continue: revoke/expire lease through normal fencing mechanism; do not start a second node while ownership is ambiguous. If split brain is suspected, activate kill switch and escalate Critical.
3. Preserve durable state: outbox/inbox offsets, order/submission attempt status, risk reservations, checkpoints and audit. No queue purge or local state reset.
4. Start only the approved artifact/manifest after infrastructure health check. Verify code/image/lock/config hash, environment/mode/account/credential tuple and database role. Any mismatch blocks start.
5. Acquire execution lease/fencing safely. Before strategy enable, run startup reconciliation of orders, fills, balance, position and private stream state. Mark any in-flight request `UNKNOWN`; use RB-001.
6. Process durable outbox/inbox with dedupe and established order; do not regenerate ClientOrderId or resubmit uncertain requests.

## Verify and resume

Evidence must show exactly one active execution leader, current heartbeat/fencing, clean health/readiness, matching manifest/config hash, replay/checkpoint result, reconciliation completion, no unresolved unknown/mismatch, risk/kill-switch state and alert route. Strategy enable remains a separate authorized action.

## Escalation and evidence

Escalate for simultaneous leaders, inability to prove old process stopped, lost/duplicate order, migration/schema mismatch, corrupted checkpoint, missing audit or failed reconciliation. Retain process/lease timeline, hashes, command/event offsets, incident and resume approval.

