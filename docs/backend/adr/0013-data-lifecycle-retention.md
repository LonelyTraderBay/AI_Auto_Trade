# ADR-0013 — Data lifecycle, retention, Parquet atomicity and backup consistency

| Thuộc tính | Giá trị |
|---|---|
| ADR ID | ADR-0013 |
| Phiên bản | 0.1.0 |
| Status | DRAFT — required before Phase 2; no retention/purge authorization |
| Date | 2026-07-31 |
| Owner | Security/Backup Owner |
| Approver | Account Owner (pending) |
| Effective date | Chưa hiệu lực (chỉ điền khi APPROVED) |
| Decision deadline | Before Phase 2 |
| Rà soát gần nhất | 2026-08-02 |
| Consulted | Technical Operator |
| Related | FR-MKT-001, FR-OPS-001, NFR-AUD-001, NFR-DET-001, NFR-OPS-001; [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §7.11–§7.12, §9, §12; DATA-001, DATA-006 |
| Supersedes / superseded by | None / None |
| Change summary | 0.1.0 (2026-08-02): chuẩn hóa header theo TMP-ADR-001/GOV-DOC-001 §3 — thêm ADR ID/Phiên bản/Effective date/Decision deadline/Rà soát/Change summary (audit toàn diện); nội dung quyết định không đổi (soạn 2026-07-31). |

## Context and decision drivers

Phase 2 writes market/catalog/dataset history, and later replay/audit/backups depend on knowing what is retained, immutable, encrypted, recoverable and legally permitted. Legal/compliance, data licensing, location, retention duration and backup owner are unresolved under OD-007; retaining or purging by assumption is unsafe.

## Proposed decision

No retention duration, storage location or purge is approved by this DRAFT. Before Phase 2, an approved retention matrix must classify bronze raw market, silver/gold dataset, order/fill/journal/audit, outbox/inbox/DLQ, logs/traces and evidence/config/manifest; name owner, hot/archive store, legal/license basis, encryption/access, retention/hold/archive/purge rule, restore requirement and evidence.

Non-negotiable proposed invariants: financial/audit/order/fill/journal history is immutable and never hard-deleted; Parquet writes use temporary path + checksum + validation + commit marker and catalog publishes only completed partition/version; late/revised data creates a new version/partition rather than silent bronze rewrite; backup consistency set includes PostgreSQL/WAL, Parquet/catalog manifests, evidence and effective config/deployment/ADR/gate records needed for replay.

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| Decide retention only before live | Phase 2 already creates data needing licensing/replay policy |
| Keep everything forever | may violate legal/cost/security requirements and lacks storage/restore design |
| Delete old data manually | destroys audit/replay and cannot prove scope |
| Publish Parquet directly to final path | readers can observe partial/corrupt data |

## Consequences

Phase 2 is BLOCKED until OD-007, legal/licensing assessment, retention matrix and backup ownership are approved. Catalog metadata needs checksums/version/quarantine/atomicity fields. Any purge needs documented dedupe/replay/hold check, immutable evidence and authorization; it is not a cleanup script.

## Migration, rollout and rollback/forward-fix

No lifecycle job now. Future retention rollout begins with inventory/classification and restore test, then archive/purge only in bounded approved scope. Failed/unsafe lifecycle operation stops and preserves data/evidence; recovery uses forward-fix/restore, not silent overwrite.

## Approval criteria

- [ ] OD-007 and applicable legal/license assessment resolved by Account Owner.
- [ ] Retention/backup matrix names every class, owner, storage, encryption, duration/hold/purge and restore test.
- [ ] Parquet/catalog atomicity and backup consistency/restore drill evidence are reviewed.

