# ADR-0011 — Accounting policy, chart of accounts and ledger invariants

| Thuộc tính | Giá trị |
|---|---|
| Status | DRAFT — required for Phase 0.0; chưa mở gate |
| Date | 2026-07-31 |
| Owner | Technical Operator |
| Approver | Account Owner |
| Consulted | Risk Approver, Security/Backup Owner |
| Related | FR-LED-001, FR-EXEC-001, FR-REC-001, NFR-AUD-001, NFR-SAFE-001; [Master](../../AI_AUTO_TRADE_MASTER_SPEC.md) §7.8, §8.11; DOM-004; DATA-004–DATA-007 |
| Supersedes / superseded by | None / None |

## Context and decision drivers

The platform requires internal accounting truth that is replayable, deduplicated and reconcilable with external venue state. Venue reports alone do not preserve internal causality/risk/audit. Accounting cannot be left to implicit code defaults because scale, rounding, fee, cost basis, valuation and adjustment change safety/PnL meaning.

## Proposed decision

If approved, `portfolio_ledger` uses append-only double-entry, multi-commodity journal entries and postings. A posting records canonical account, asset/commodity, a positive `NUMERIC(38,18)` quantity and approved debit/credit direction. Each journal entry balances per asset/commodity at transaction commit. The ledger write path and database enforcement mechanism are the only permitted writers; the proposed enforcement is a deferred transaction-end balance check owned by the ledger schema, subject to implementation review.

Journal/posting are immutable accounting truth. Balance, position and PnL are rebuildable projections. Every booked fact has source type/ID/source event, accounting policy version, effective/recorded time, correlation and evidence. Duplicate fill/source evidence cannot create a second journal entry. Correction is a new approved balancing entry; original history is never rewritten.

## Owner decisions required before approval/activation

This ADR cannot become an effective Phase 1 policy until Account Owner approves the following annex values for the relevant scope: chart-of-accounts taxonomy/mapping, commodity/asset scale, rounding mode/location, fee/rebate treatment, transfer/adjustment authority, cost-basis method, valuation source/timestamp/stale behavior, locked/reserved balance representation and tolerance/reconciliation rules. No asset, currency, tax treatment or value is invented here.

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| Venue balance as ledger truth | lacks canonical source/event/decision causality and can be revised externally |
| Mutable balances only | cannot audit/rebuild/deduplicate correction history |
| Single base-currency float ledger | loses asset precision and introduces rounding/valuation ambiguity |
| Application-only balance check | runtime bug/partial path can bypass accounting invariant |
| Tax engine in MVP | tax jurisdiction/account requirements are out of scope and unprovided |

## Consequences

Ledger implementation needs chart/policy versioning, immutable grant protection, unique posting lines, source dedupe, database balance enforcement and property/rebuild/reconciliation tests. `NUMERIC(38,18)` limit applies; unsupported scale blocks capability pending ADR/migration. Fee/rebate/transfer/funding/interest require explicit policy rather than silent netting or unsupported behavior.

## Migration, rollout and rollback/forward-fix

Task 0.3 creates no ledger table. Phase 1 implementation occurs only after policy annex approval, test fixtures and write-path enforcement design. Policy evolution creates new effective version; it does not mutate old accounting meaning. Accounting defect recovery is append adjustment/forward-fix or tested restore, then projection rebuild/reconciliation.

## Approval criteria

- [ ] Account Owner approves every owner-decision annex item for initial scope.
- [ ] DOM-004, dictionary/ERD, balance-enforcement design and role grants are reviewed.
- [ ] Tests prove per-commodity balance, duplicate fill single booking, immutable correction, rebuild and reconciliation.

