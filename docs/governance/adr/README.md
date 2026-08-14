# ADR register

| Thuộc tính | Giá trị |
|---|---|
| Document ID | GOV-ADR-INDEX-001 |
| Phiên bản | 0.3.2 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực — registry mirror; từng ADR có ngày hiệu lực riêng |
| Rà soát gần nhất | 2026-08-15 |
| Master authority | §15.1 of `AI_AUTO_TRADE_MASTER_SPEC.md` |
| Change summary | 0.3.2 (2026-08-15): Đồng bộ trạng thái registry với các ADR content files; không tạo approval mới, không mở phase/gate. 0.3.1 (2026-08-02): ADR-0006 ghi đầy đủ deadline "Before runtime use, no later than Phase 5" theo master §15.1; cột Decision của 0016 khớp đúng thứ tự tiêu đề file; header bổ sung các trường thiếu theo GOV-DOC-001 §3. |

Status in each linked ADR content file under `docs/backend/adr/` is the authority for that ADR; this registry mirrors that status. A linked ADR marked `DRAFT` is not effective and cannot open a gate.

> Registry (this index) lives at `docs/governance/adr/` (Governance-Process layer); ADR content files live at `docs/backend/adr/` (Backend layer, since every current decision is a backend/architecture decision) — see `docs/governance/documentation-layer-classification.md`.

| ADR | Decision | Required by | Status |
|---|---|---|---|
| [0001](../../backend/adr/0001-modular-monolith.md) | Modular monolith | Phase 0.0 gate | APPROVED |
| [0002](../../backend/adr/0002-hexagonal-architecture.md) | Hexagonal architecture and composition root | Phase 0.0 gate | APPROVED |
| [0003](../../backend/adr/0003-persistence-strategy.md) | PostgreSQL/Parquet persistence | Phase 0.0 gate | APPROVED |
| [0004](../../backend/adr/0004-outbox-inbox-delivery.md) | Outbox/inbox delivery | Phase 0.0 gate | APPROVED |
| [0005](../../backend/adr/0005-canonical-oms.md) | Canonical OMS/reconciliation | Phase 0.0 gate | APPROVED |
| [0006](../../backend/adr/0006-nautilus-boundary.md) | NautilusTrader boundary | Before runtime use, no later than Phase 5 (master §15.1) | DRAFT |
| [0007](../../backend/adr/0007-risk-kill-switch-reconciliation.md) | Risk, kill switch and reconciliation | Phase 0.0 gate | APPROVED |
| [0008](../../backend/adr/0008-llm-off-hot-path.md) | LLM hot-path/credentials | Before Phase 6 | DRAFT |
| [0009](../../backend/adr/0009-first-venue-account-instrument.md) | First venue/account/instrument | Before Phase 3 | DRAFT |
| [0010](../../backend/adr/0010-canary-topology-backup-deployment.md) | Canary topology, backup and deploy | Before Phase 4 | DRAFT |
| [0011](../../backend/adr/0011-accounting-policy.md) | Accounting policy and ledger invariants | Phase 0.0 gate | APPROVED |
| [0012](../../backend/adr/0012-transaction-concurrency.md) | Transaction/concurrency/fencing | Phase 0.0 gate | APPROVED |
| [0013](../../backend/adr/0013-data-lifecycle-retention.md) | Lifecycle, retention and backup set | Before Phase 2 | DRAFT |
| [0014](../../backend/adr/0014-toolchain-repo-contract-authority.md) | Toolchain/repository/contract authority | Phase 0.0 gate | APPROVED |
| [0015](../../backend/adr/0015-authentication-session-machine-identity.md) | Authentication/session/machine identity | Before Phase 3 | DRAFT |
| [0016](../../backend/adr/0016-provider-neutral-byok-ai-connections.md) | Provider-neutral AI/BYOK connection, catalog and credential boundary | Before Phase 6 | DRAFT |

Approval procedure: review Context, Decision, Alternatives, Consequences, related requirements/contracts, rollout/forward-fix and explicit non-goals. Record the Account Owner’s decision and UTC timestamp in each ADR, then update this register and the gate record applicable to that ADR's phase in the same change.

## Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.3.2 | 2026-08-15 | Đồng bộ registry status với ADR content files; ghi rõ registry là mirror, không tạo approval mới và không mở gate. | Technical Operator | Technical validation; Account Owner packet review pending |
| 0.3.1 | 2026-08-02 | Audit toàn diện: ADR-0006 deadline đầy đủ theo master §15.1; Decision 0016 khớp thứ tự tiêu đề file; header bổ sung (pending)/Ngày hiệu lực/Rà soát/Change summary. | Technical Operator | Pending |
| 0.3.0 | 2026-07-31 | Cập nhật link sau khi tái cấu trúc docs/ theo lớp Backend/Frontend/Shared/Governance (GOV-CLASS-001): registry chuyển sang docs/governance/adr/, nội dung ADR chuyển sang docs/backend/adr/. | Technical Operator | Pending |
| 0.2.0 | 2026-07-31 | Đăng ký ADR-0016 cho AI đa provider/BYOK, required trước Phase 6; không phê duyệt runtime/provider/key. | Technical Operator | Pending |
| 0.1.0 | 2026-07-31 | Tạo ADR register baseline. | Technical Operator | Pending |
