# ADR register

| Thuộc tính | Giá trị |
|---|---|
| Document ID | GOV-ADR-INDEX-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner |
| Master authority | §15.1 of `AI_AUTO_TRADE_MASTER_SPEC.md` |

All ADR files in this directory are `DRAFT` until an Account Owner decision is recorded in the individual file. Existence of a draft is not approval.

| ADR | Decision | Required by | Status |
|---|---|---|---|
| [0001](0001-modular-monolith.md) | Modular monolith | Phase 0.0 gate | DRAFT |
| [0002](0002-hexagonal-architecture.md) | Hexagonal architecture and composition root | Phase 0.0 gate | DRAFT |
| [0003](0003-persistence-strategy.md) | PostgreSQL/Parquet persistence | Phase 0.0 gate | DRAFT |
| [0004](0004-outbox-inbox-delivery.md) | Outbox/inbox delivery | Phase 0.0 gate | DRAFT |
| [0005](0005-canonical-oms.md) | Canonical OMS/reconciliation | Phase 0.0 gate | DRAFT |
| [0006](0006-nautilus-boundary.md) | NautilusTrader boundary | Before runtime use | DRAFT |
| [0007](0007-risk-kill-switch-reconciliation.md) | Risk, kill switch and reconciliation | Phase 0.0 gate | DRAFT |
| [0008](0008-llm-off-hot-path.md) | LLM hot-path/credentials | Before Phase 6 | DRAFT |
| [0009](0009-first-venue-account-instrument.md) | First venue/account/instrument | Before Phase 3 | DRAFT |
| [0010](0010-canary-topology-backup-deployment.md) | Canary topology, backup and deploy | Before Phase 4 | DRAFT |
| [0011](0011-accounting-policy.md) | Accounting policy and ledger invariants | Phase 0.0 gate | DRAFT |
| [0012](0012-transaction-concurrency.md) | Transaction/concurrency/fencing | Phase 0.0 gate | DRAFT |
| [0013](0013-data-lifecycle-retention.md) | Lifecycle, retention and backup set | Before Phase 2 | DRAFT |
| [0014](0014-toolchain-repo-contract-authority.md) | Toolchain/repository/contract authority | Phase 0.0 gate | DRAFT |
| [0015](0015-authentication-session-machine-identity.md) | Authentication/session/machine identity | Before Phase 3 | DRAFT |

Approval procedure: review Context, Decision, Alternatives, Consequences, related requirements/contracts, rollout/forward-fix and explicit non-goals. Record the Account Owner’s decision and UTC timestamp in each ADR, then update this register and the Phase 0.0 gate record in the same change.
