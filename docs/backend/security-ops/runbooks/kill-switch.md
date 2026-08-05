# RB-004 — Kill-switch activation and release

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.1 / DRAFT |
| Owner / Approver | Technical Operator; release: Risk Approver + Account Owner / Account Owner (pending) |
| Effective date / Last review | Chưa hiệu lực / 2026-08-02 |
| Trigger / Severity | Safety breach, risk/data/reconciliation/credential/lease condition, manual operator decision / Critical or High by approved policy |
| Scope / Incident commander | Explicit global/account/instrument/strategy scope / Technical Operator; Risk Approver + Account Owner for release |
| Related | FR-RSK-001, FR-OPS-001, NFR-SEC-001; ADR-0007, ADR-0015; SEC-002 |
| Change summary | Design procedure; no endpoint is executed until implementation/authorization exists. 1.0.1 (2026-08-02): bổ sung Owner/Approver + Effective/Last review theo GOV-DOC-001 §3 (audit toàn diện). |

## Safe-state objective

Activation blocks new order submission in the requested scope and preserves all in-flight uncertainty for reconciliation. It is not permission to discard or blindly cancel order state. Release is a high-risk, re-authenticated, auditable decision, not a toggle.

## Activation

1. Identify trigger, scope, environment, affected deployment/strategy/account/instrument and immediate risk. Open incident for Critical/high-impact action.
2. An authenticated Technical Operator sends an idempotent command to `POST /api/v1/commands/kill-switch-activations` with command type `ACTIVATE_KILL_SWITCH`, explicit reason and correlation ID. The accepted command must be audited; record command ID/Location.
3. Verify runtime acknowledgement: scope blocked, strategy disabled/frozen as applicable, no new submission attempts, lease/queue state recorded and current orders classified. Do not assume an in-flight request failed.
4. For any uncertain order or private stream/reconciliation condition, execute RB-001/RB-002/RB-003. For credential compromise execute RB-007.

## Release preconditions

Release is prohibited until the original trigger is resolved or an approved policy decision explicitly defines safe residual exposure. Required evidence: root trigger/timeline, reconciliation result for affected scope, current market/reference/private-data health, no unresolved `UNKNOWN`/mismatch, risk policy/config/manifest hash, audit completeness and verification that activation actually blocked submission.

## Release

1. Risk Approver and Account Owner re-authenticate for the exact scope/action, supply explicit reason and review evidence. The provider-independent re-auth requirement is mandatory even before provider choice is finalized.
2. Submit one idempotent `RELEASE_KILL_SWITCH` command to `POST /api/v1/commands/kill-switch-releases`; record command ID/Location and approvals. No UI-only confirmation.
3. Verify release only changes approved scope, then run readiness/health, lease, config hash, reconciliation and risk checks before enabling a strategy. Do not automatically resume strategy solely because kill switch is released.

## Escalation and evidence

Failed activation, scope ambiguity, any submission after activation, release denial, stale evidence or missing audit is Critical. Retain trigger, command/audit IDs, pre/post state hashes, actor/roles, re-auth result metadata (never proof/token), reconciliation and final approval. Review all kill-switch events in operational cadence.

