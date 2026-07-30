# RB-001 — Unknown order / outcome recovery

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.0 / DRAFT |
| Trigger / Severity | Order state `UNKNOWN`, cancel outcome unknown, or age > `unknown_order_sla_s` / Critical after SLA |
| Scope / Incident commander | Affected venue-account-instrument-order / Technical Operator; Risk Approver for exposure decision |
| Related | FR-OMS-001, FR-REC-001, NFR-OPS-001; ADR-0005, ADR-0007, ADR-0012; OPS-001 |
| Change summary | Design procedure; execute only after Control API/runtime is approved. |

## Safe-state objective

Do not retry submission or cancel blindly. Freeze conflicting new exposure for the affected account/instrument/strategy, preserve order/submission/audit evidence, and determine venue truth through reconciliation. `UNKNOWN` is not a rejection.

## Preconditions and immediate containment

1. Record incident ID, environment, deployment/manifest/config hash, order/client-order ID, correlation/causation/trace IDs, last known state and timestamps.
2. Verify the active execution leader/lease. If lease is missing/ambiguous, block submission and follow RB-005 as needed.
3. Disable/freeze affected strategy scope or activate kill switch under RB-004 if exposure/risk policy requires it. Do not delete queue rows, recreate ClientOrderId or call direct venue console as a substitute for audit.
4. Preserve request hash, submission attempt, adapter logs after redaction, private-stream state, balance/position snapshot and relevant market/reference freshness evidence.

## Procedure

1. Read canonical order timeline via `GET /api/v1/orders/{order_id}` and `/timeline` when implemented; verify idempotency/client-order reference and no duplicate local intent.
2. Submit exactly one authenticated, idempotent reconciliation command to `POST /api/v1/commands/reconciliations` with `command_type=REQUEST_RECONCILIATION`, reason and affected scope. Record returned command ID/Location; do not submit a replacement order.
3. Obtain venue evidence through the approved adapter: client order ID, venue order reference, fills, trades, open orders, balance/position and private stream sequence. No raw credential or raw vendor payload enters evidence.
4. Apply canonical state-machine result: ack/reject/open/partial/filled/cancelled/expired as proven; persist immutable fill/ledger evidence before projection. If evidence remains incomplete, keep `RECONCILING`/safe scope until policy SLA.
5. At/after `unknown_order_sla_s`, raise Critical incident. If unresolved evidence makes exposure unsafe, mark/handle as `LOST` only through approved reconciliation procedure; never reopen terminal aggregate to non-terminal state.

## Verify and resume

Verify one canonical internal order per ClientOrderId, no duplicate fill booking, order/position/balance reconciliation, risk reservation state, ledger balance, audit chain and cleared/justified alert. Risk Approver plus required runtime owner approves scope resume; a green API response alone is insufficient.

## Escalation and evidence

Escalate immediately for duplicate/unapproved order, missing audit, conflicting venue evidence, ledger imbalance or failed reconciliation. Store incident record, command result, redacted evidence hashes, timeline, state transition, actor/role and decision. Post-incident: add fixture/test if a new failure pattern was discovered.

