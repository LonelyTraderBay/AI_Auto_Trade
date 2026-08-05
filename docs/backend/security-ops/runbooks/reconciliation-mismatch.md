# RB-003 — Reconciliation mismatch

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.1 / DRAFT |
| Owner / Approver | Technical Operator + Risk Approver / Account Owner (pending) |
| Effective date / Last review | Chưa hiệu lực / 2026-08-02 |
| Trigger / Severity | Internal order/fill/balance/position/open-order state differs from approved external evidence / High; Critical when unsafe exposure or SLA breach |
| Scope / Incident commander | Affected environment/account/venue/instrument / Technical Operator with Risk Approver |
| Related | FR-REC-001, FR-EXEC-001, NFR-OPS-001; ADR-0004, ADR-0005, ADR-0007, ADR-0012; RB-001 |
| Change summary | Design procedure for read-only evidence first, canonical correction second. 1.0.1 (2026-08-02): bổ sung Owner/Approver + Effective/Last review theo GOV-DOC-001 §3 (audit toàn diện). |

## Safe-state objective

Freeze new exposure for the affected scope. Do not overwrite local facts, delete events, edit financial records or submit/cancel blindly. Reconcile using immutable evidence and append approved correction/incident records.

## Procedure

1. Open incident and capture mismatch type (order, fill, balance, position, open order, fee, reference), detection time, scope, correlation IDs, deployment/config/risk version and snapshot hashes.
2. Ensure strategy/execution scope is blocked. Activate kill switch under RB-004 when mismatch threatens broader exposure or policy requires it.
3. Create one idempotent `REQUEST_RECONCILIATION` command at `POST /api/v1/commands/reconciliations`; record command ID/Location and avoid duplicate commands for the same incident scope.
4. Collect external evidence through approved read-only adapter: account snapshot, open/closed orders, fills/trades, fees, balance/position and relevant stream watermark. Verify scope/environment and source timestamp before comparing.
5. Classify: delayed projection, duplicate/out-of-order input, unknown local order/external order, missing fill/fee, terminal correction, stale reference or external data inconsistency. Link all evidence hashes; raw vendor payload remains redacted/classified.
6. Apply only canonical state-machine/event/ledger correction through authorized handler. For external order without local order, create reconciliation case classified `EXTERNAL`; do not fabricate original strategy intent. For unknown external outcome, follow RB-001.
7. Recompute projections from immutable facts where required, verify journal balance and maintain incident/audit trail. Any unexplainable ledger imbalance is Critical and blocks resume.

## Verify and resume

Compare internal and external order/fill/fee/balance/position snapshot after correction; confirm no duplicate booking, resolved reservation, valid terminal rules, alert state, audit before/after hash and risk readiness. Technical Operator and Risk Approver record decision; Account Owner is involved for canary/live scope.

## Escalation and evidence

Escalate if venue evidence is unavailable/inconsistent, a local order is missing, a terminal state would be reopened, loss exceeds approved limit, audit chain is incomplete, or mismatch exceeds SLA. Preserve timelines, command status, checksums, projection/rebuild result and post-mortem action.

