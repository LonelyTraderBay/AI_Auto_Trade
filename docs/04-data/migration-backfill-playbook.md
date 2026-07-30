# DATA-007 — Migration, backfill and schema-evolution playbook

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 0.1.0 |
| Trạng thái | DRAFT — chờ Account Owner phê duyệt |
| Owner | Technical Operator |
| Approver | Account Owner |
| Ngày soạn | 2026-07-31 |
| Liên quan | FR-EXEC-001, FR-LED-001, FR-REC-001, NFR-AUD-001, NFR-SAFE-001, NFR-OPS-001; ADR-0003, ADR-0011, ADR-0012, ADR-0013 |
| Nguồn policy | [Master specification](../../AI_AUTO_TRADE_MASTER_SPEC.md), §1.3, §7.5, §7.10–§7.12, §13, §15 |

## 1. Purpose and safety rule

This playbook governs any persistent schema/data change after Phase 0.0. It does not itself authorize a migration. Applied Alembic revisions are immutable; a migration is never edited, renamed or silently rerun after application. The default recovery for financial/audit data is forward-fix or tested restore, never destructive downgrade.

## 2. Required inputs before authoring a migration

- Approved task card with allowed path, owner/reviewer, exact acceptance commands and evidence path.
- Approved data dictionary entry, ERD impact, requirement/ADR/contract registry links.
- Explicit compatibility classification: editorial, compatible, breaking/domain/data or safety/security/live.
- Schema/current revision snapshot, expected duration/lock/write impact and dependent readers/producers.
- Backfill plan (or explicit “none”), checkpoint/resume token, rate/lag limits, validation and stop criteria.
- Rollback/forward-fix/restore assessment, especially for financial/audit/event tables.

Missing input means BLOCKED; no “empty base migration” is created to make later work easier.

## 3. Standard expand -> migrate -> contract sequence

1. **Expand:** add backward-compatible table/column/index/constraint surface. Existing code continues to read/write old representation.
2. **Dual-compatible release:** deploy code that can read old/new representation; write behavior is explicitly versioned and audited.
3. **Backfill:** process bounded batches with durable checkpoints/resume, rate/lock/lag metrics and idempotent semantics.
4. **Verify:** compare count/checksum/invariant/query results; retain evidence and show no stale reader remains.
5. **Contract:** switch readers/writers only after gate; drop/rename only in a later approved release after compatibility window.

Breaking public event/API/config changes need new major schema/version and compatibility/upcaster plan; a DB migration does not make a wire change safe by itself.

## 4. Backfill contract

| Requirement | Rule |
|---|---|
| Scope | named source/target columns/tables, invariant and selection predicate in task/dictionary |
| Idempotency | repeated batch/resume cannot create duplicate business/financial/audit fact |
| Checkpoint | durable opaque checkpoint and processed range/count/hash; restart uses it |
| Ordering | preserve aggregate/partition order where contract requires it |
| Load control | approved batch size/rate, timeout, lock/replication/WAL monitoring; pause safely |
| Validation | before/after count, checksum/sample, constraint/property/integration test and error/quarantine report |
| Failure | stop criteria, alert, evidence, rollback/forward-fix/restore decision; never manual silent patch |
| Audit | actor/machine, code/image/config hash, UTC start/end and outcome recorded |

For append-only financial/audit facts, a backfill adds a new approved fact/correction or rebuildable projection; it never updates historical source rows to “clean” them.

## 5. Migration execution stages

### 5.1 Preflight

Verify environment identity, approved revision chain, backup/restore point, role (`db_migrator` only), task expiry/approval, current schema fingerprint, free capacity and dependent runtime state. Stop trading/exposure only when the approved plan/runbook says needed; do not assume a migration can run while execution is active.

### 5.2 Execute

Run the exact reviewed migration procedure once. Capture UTC start/end, revision, image/code hash, effective config hash, runner, database target identity, output/exit code and performance/lock metrics. A failure is an incident/evidence item, not a prompt to edit an applied revision.

### 5.3 Validate

Check revision/schema snapshot, dictionary conformance, role grants, new constraints/indexes, compatibility reads, migration-specific fixture/property/integration tests, outbox/inbox behavior if affected, ledger balance/reconciliation if financial data is touched. Record actual versus expected duration and any exception.

### 5.4 Roll forward or restore

Choose the preapproved path: a new forward-fix revision for reversible logical defect, or restore a tested consistency set for corruption/unsafe data loss. Do not use destructive schema downgrade for financial/audit history. After restore, rebuild projections and reconcile before enabling strategy.

## 6. Special protections

| Affected area | Additional mandatory review |
|---|---|
| OMS/risk/reservation | state machine, concurrency/lease/idempotency and unknown-outcome impacts |
| Ledger/posting/audit | accounting policy, database balance enforcement, append-only grants, rebuild/reconcile evidence |
| Outbox/inbox/DLQ | at-least-once/consumer compatibility, dedupe window, payload redaction and crash recovery |
| Market/Parquet catalog | atomic publish/manifest/checksum/retention and no-look-ahead/reproducibility |
| Security/auth/secret metadata | access-control matrix, sensitive-data classification and security approver |
| Index/partition/retention | query budget, lock/WAL impact, archive/restore and ADR-0013 policy |

## 7. Required evidence record

Every migration/backfill evidence record must include Task ID, migration revision, source/target schema fingerprint, requirements/ADRs/contracts, environment, runner/time, exact command/procedure reference, input/output row counts, checkpoint and validation hashes, test results, lock/lag metrics, incident/waiver, recovery decision and reviewer/approver. Evidence missing means the deployment/gate is FAIL.

## 8. Completion checklist

- [ ] The migration is immutable and name/message carry Task ID/intent.
- [ ] Schema, dictionary, ERD and contract registry agree.
- [ ] Compatibility window and old-reader retirement are explicit.
- [ ] Backfill is idempotent/checkpointed/observable or not required with justification.
- [ ] Restore/forward-fix has been assessed and relevant tests/evidence pass.
- [ ] No unapproved migration, direct data patch or history rewrite occurred.

