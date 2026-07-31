# ADR-0006 — NautilusTrader evaluation boundary

| Thuộc tính | Giá trị |
|---|---|
| Status | DRAFT — not required before Phase 5; no adoption authorized |
| Date | 2026-07-31 |
| Owner | Technical Operator |
| Approver | Account Owner |
| Related | FR-STR-001, FR-EXEC-001, NFR-DET-001; [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §3.1, §4, §10; ADR-0002, ADR-0005 |
| Supersedes / superseded by | None / None |

## Context and decision drivers

NautilusTrader may offer runtime/backtest capability, but adopting its domain as canonical would duplicate or displace system-owned OMS/risk/ledger/audit/reconciliation semantics. MVP does not need it before Phase 5 and cannot carry an unbounded integration dependency.

## Proposed decision

Until this ADR is APPROVED after a measured evaluation, NautilusTrader is **forbidden from runtime and dependency graph**. If later approved, it may be an adapter behind ports for a specifically scoped backtest/runtime capability only. It will not own or replace canonical OrderIntent, RiskDecision, OMS state machine, client order ID, ledger, event contract, audit or reconciliation.

The evaluation must document one-way mappings, ownership, deterministic replay parity, error/unknown-order behavior, performance/operations cost, pin/version/license/security review and removal path. One logic must not be implemented twice merely to keep two kernels “in sync”.

## Alternatives considered

| Alternative | Why not proposed now |
|---|---|
| Adopt Nautilus as canonical core | transfers safety/domain authority to an external model and risks incompatible lifecycle/accounting semantics |
| Use it opportunistically inside contexts | creates hidden vendor coupling and duplicate logic |
| Never evaluate it | premature rejection; evaluation is permitted later under explicit boundary |

## Consequences

Current Phase 0–4 implementation stays pure Python domain/ports and fake/simulator/venue adapters. Any import/package/config/worker attributed to Nautilus before approval is a policy violation. Approval would require contract tests proving mapping/replay and a feature flag/deployment scope that can be removed without losing canonical facts.

## Migration, rollout and rollback/forward-fix

No migration or rollout now. A future proposal must first run isolated research/test fixture evaluation, then shadow/paper evidence, with no new system of record. Rollback is disabling/removing the adapter and continuing from canonical events/ledger; no data format becomes canonical solely due to the adapter.

## Approval criteria

- [ ] Measured need exists after Phase 4 rather than speculation.
- [ ] Mapping/ownership/replay/unknown-outcome test report exists.
- [ ] Dependency/security/license/operational review and removal plan are accepted by Account Owner.

