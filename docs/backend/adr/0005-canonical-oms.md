# ADR-0005 — Canonical OMS lifecycle, selective event history and reconciliation semantics

| Thuộc tính | Giá trị |
|---|---|
| Status | DRAFT — required for Phase 0.0; chưa mở gate |
| Date | 2026-07-31 |
| Owner | Technical Operator |
| Approver | Account Owner |
| Related | FR-EXEC-001, FR-REC-001, NFR-AUD-001, NFR-SAFE-001; [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §5.4–§5.8, §7.6–§7.8, §8.6–§8.10; DOM-001, DOM-002 |
| Supersedes / superseded by | None / None |

## Context and decision drivers

Venue order states are inconsistent, responses can be lost, fill can arrive before acknowledgement and external/manual state can differ from local state. A canonical lifecycle must stop duplicate orders and make recovery/audit deterministic without event-sourcing every mutable configuration/reference record.

## Proposed decision

If approved, `execution` owns a canonical OMS aggregate and the state/transition contract in DOM-002. Strategy emits only `ProposedOrderIntent`; execution canonicalizes it, creates exactly one client order ID per venue/account and calls risk. Only risk-approved/reserved order may enter durable submit queue. State/event/fill history is append-only/replayable; mutable projection/order state is derived/controlled, while config/reference stays normal persistence with audit.

Submit timeout/disconnect becomes `UNKNOWN`, then `RECONCILING`; it is never an automatic resend. Reconciliation uses client order ID/history/open orders/fills and creates evidence/cases. `EXTERNAL` is a classification, not a state. Terminal state cannot become non-terminal. Late proven terminal evidence becomes auditable terminal correction; late open/partial evidence after `LOST` stays blocked as external reconciliation case. Direct venue replace is not MVP; cancel then new intent/new client order ID is the only supported expression.

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| Use venue status model directly | locks domain to provider semantics and cannot express common recovery/audit behavior |
| Treat timeout as reject and resend | creates duplicate exposure risk |
| Event-source all system tables | excessive complexity for config/reference/deployment with no safety benefit |
| Mutable fills/order history | destroys audit, dedupe and replay correctness |
| Allow direct UI/manual order endpoint | bypasses canonical risk/idempotency/approval path |

## Consequences

OMS needs transition tests, sequence uniqueness, venue capability mapping, reconciliation worker/runbook and durable client order identity. Venue adapter must reject unsupported capability explicitly. `executed_quantity` derives from immutable fills. Terminal correction preserves original reason/incident/evidence; it does not rewrite history.

## Migration, rollout and rollback/forward-fix

Phase 1 fake venue proves lifecycle before any external venue. A future state/semantic change is breaking: it requires ADR, new event/schema version where public, migration/upcaster/forward-fix plan and replay/property/chaos evidence. Existing applied history is never reinterpreted silently.

## Approval criteria

- [ ] Account Owner accepts DOM-002 canonical state meanings and no-blind-retry rule.
- [ ] Risk/reservation, concurrency and reconciliation maps are approved alongside ADR-0007/0012.
- [ ] Phase 1 task card links every OMS transition to test/evidence/contract.

