# ADR-0009 — First venue, account and instrument scope

| Thuộc tính | Giá trị |
|---|---|
| ADR ID | ADR-0009 |
| Phiên bản | 0.1.0 |
| Status | DRAFT — required before Phase 3; no venue/account/instrument selected |
| Date | 2026-07-31 |
| Owner | Account Owner |
| Approver | Account Owner (pending) |
| Effective date | Chưa hiệu lực (chỉ điền khi APPROVED) |
| Decision deadline | Before Phase 3 |
| Rà soát gần nhất | 2026-08-02 |
| Related | FR-MKT-001, FR-EXEC-001, FR-REC-001, NFR-SEC-001; [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §0.3 OD-001–OD-003, §2, §10, §14 Phase 3 |
| Supersedes / superseded by | None / None |
| Change summary | 0.1.0 (2026-08-02): chuẩn hóa header theo TMP-ADR-001/GOV-DOC-001 §3 — thêm ADR ID/Phiên bản/Effective date/Decision deadline/Rà soát/Change summary (audit toàn diện); nội dung quyết định không đổi (soạn 2026-07-31). |

## Context and decision drivers

Venue capabilities, legal terms, testnet availability, client order ID/query/recovery behavior, account permissions and instrument filters directly affect OMS/risk/reconciliation. No provider/account/instrument detail has been supplied or may be invented.

## Proposed decision

This ADR deliberately makes **no selection** today. Before Phase 3, Account Owner must approve a single spot-only venue, a single account/sub-account scope and a named limited instrument universe after OD-001, OD-002 and OD-003 are RESOLVED. The approval record must include capability profile checksum, testnet/public/private-read availability, terms/jurisdiction assessment, credential class, withdrawal disabled status, supported order/cancel/query/recovery behavior, rate limits, instrument filters and support/escalation evidence.

Only capabilities explicitly present in the approved profile are enabled. Unsupported capability is rejected clearly. This ADR does not authorize live trade credential, direct replace, withdrawal, derivatives, multi-venue or multi-account.

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| Pick a popular venue by assumption | legal/terms/capability/account risk cannot be inferred |
| Support several venues first | multiplies adapter/reconciliation/risk matrix before one vertical slice works |
| Select instrument dynamically from market data | bypasses owner-approved scope/risk/reference rules |

## Consequences

Phase 3 remains BLOCKED until named evidence exists. Adapter must implement capability contract suite and recovery queries before testnet/canary. Reference data carries effective/valid history, source checksum and adapter version. Account identity/credential/withdrawal details stay outside this repository’s public docs and fixtures.

## Migration, rollout and rollback/forward-fix

No migration or integration now. Future selection begins read-only public data/capability discovery, then approved testnet/private read/reconciliation, then testnet execution. Removing a venue disables its manifest/capability without deleting audit/history; it triggers reconciliation and credential revocation procedure.

## Approval criteria

- [ ] OD-001 through OD-003 have evidence URI/path and Account Owner decision.
- [ ] Legal/terms/testnet/capability/account scope and withdrawal-disable evidence are recorded.
- [ ] Venue adapter contract/recovery/reconciliation suite passes before any execution credential is wired.

