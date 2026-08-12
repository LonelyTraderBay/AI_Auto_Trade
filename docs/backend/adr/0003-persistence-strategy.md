# ADR-0003 — PostgreSQL/Parquet persistence strategy and physical types

| Thuộc tính | Giá trị |
|---|---|
| ADR ID | ADR-0003 |
| Phiên bản | 0.3.0 |
| Status | APPROVED — Account Owner approved PostgreSQL 17 amendment 2026-08-12T11:15:53Z |
| Date | 2026-07-31 |
| Owner | Technical Operator |
| Approver | Account Owner |
| Effective date | 2026-08-06 |
| Decision deadline | Phase 0.0 gate |
| Rà soát gần nhất | 2026-08-12 |
| Related | FR-MKT-001, FR-EXEC-001, FR-LED-001, FR-REC-001, NFR-AUD-001, NFR-DET-001; [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §3, §5, §7, §9; DATA-001–DATA-007 |
| Supersedes / superseded by | None / None |
| Change summary | 0.3.0 (2026-08-12): Account Owner approved PostgreSQL 17.x as the system-of-record major version for Supabase Local compatibility; all persistence/type/safety boundaries remain unchanged. |

## Context and decision drivers

The system needs transactional persistence for OMS/risk/ledger/audit and economical immutable storage for large market history/datasets. Float, timestamp ambiguity, shared-environment database and opaque JSON state would prevent replay/reconciliation. The architecture must be simple enough for a solo operator to back up and restore.

## Decision

- PostgreSQL 17.x is system of record for control, execution, risk, ledger, audit and platform delivery metadata.
- Partitioned Parquet plus manifest/checksum is the historical market/dataset store; DuckDB/research reader is read-side tooling, not OLTP truth.
- Database ownership follows bounded context schemas; no cross-context FK/ORM/direct SQL.
- Internal IDs are application-generated UUIDv7 stored as `UUID`; venue identifiers are separate fields.
- Finance uses Decimal domain / `NUMERIC(38,18)` database; API is string; scale above 18 is unsupported without ADR/migration.
- Timestamps are UTC `TIMESTAMPTZ`; JSONB is limited to vendor/redacted evidence/versioned extension.
- SQLAlchemy 2 + Alembic supply versioned migrations; applied revisions are immutable.

TimescaleDB, pgvector and any additional database are deferred. Each environment has its own DB/credential/backup boundary.

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| SQLite/files as trading system of record | insufficient concurrency/audit/recovery operating baseline for target lifecycle |
| Parquet-only | lacks transactional conflict, audit/query and reconciliation behavior for OMS/ledger |
| TimescaleDB first | extension/operations complexity before measured time-series need |
| Float or vendor numeric strings internally | deterministic/accounting errors and ambiguous scale |
| One table/JSONB event store for all state | erases ownership/constraint/query semantics |

## Consequences

Every table needs dictionary, owner, access, retention, integrity and migration plan. PostgreSQL availability becomes a safety dependency; database failure fails closed for new exposure. Parquet publication needs temporary path, checksum, validation and commit marker. A backup consistency set includes PostgreSQL/WAL, catalog/manifests, effective config/deployment and evidence required for replay.

## Migration, rollout and rollback/forward-fix

Task 0.3 physical scope is limited to approved platform outbox/inbox delivery baseline. Future DDL follows expand -> compatible code -> checkpointed backfill -> contract. Financial/audit schema defaults to forward-fix or tested restore, not destructive downgrade. Retention/partition/purge needs ADR-0013 before Phase 2.

## Approval criteria

- [x] Account Owner accepts PostgreSQL/Parquet division and physical type rules.
- [x] DATA-001 through DATA-007 are reviewed with no unowned/cross-context object.
- [x] Task 0.3 dictionary/migration scope is approved separately; approval of this ADR alone creates no table.

## Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.3.0 | 2026-08-12 | Approved PostgreSQL 17.x major-version amendment for Supabase Local compatibility; no change to ownership, transaction, type, audit or recovery invariants. | Technical Operator | Account Owner approval `2026-08-12T11:15:53Z` |
| 0.2.0 | 2026-08-06 | Status → APPROVED; Account Owner decision 2026-08-06T00:00:00Z. | Account Owner | Account Owner |
