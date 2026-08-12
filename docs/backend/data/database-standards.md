# DATA-004 — PostgreSQL database standards

| Thuộc tính | Giá trị |
|---|---|
| Document ID | DATA-STD-001 (registry DOCS_INDEX; title giữ alias ngắn) |
| Phiên bản | 0.2.0 |
| Trạng thái | DRAFT — chờ Account Owner phê duyệt |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày soạn | 2026-07-31 |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-08-02 |
| Liên quan | FR-EXEC-001, FR-LED-001, FR-REC-001, NFR-AUD-001, NFR-SAFE-001, NFR-OPS-001; ADR-0003, ADR-0011, ADR-0012, ADR-0013 |
| Nguồn policy | [Master specification](../../../AI_AUTO_TRADE_MASTER_SPEC.md), §3.2, §5.1, §7.4–§7.12, §12 |
| Change summary | 0.2.0 (2026-08-02): §3 ghi ngoại lệ tường minh cho quy tắc table-plural (outbox/inbox/…, master §7.6) và cho logical name identity dạng TEXT (`consumer_id`); chuẩn hóa header theo GOV-DOC-001 §3 (audit toàn diện). |

## 1. Scope and authority

These are mandatory physical-database conventions for PostgreSQL 17.x. They do not authorize DDL. An applied immutable Alembic migration plus schema snapshot is physical authority; this policy, the [dictionary](data-dictionary.md), task card and ADRs are prerequisites for that migration.

## 2. Database and schema boundaries

- One environment equals one database, credential set, backup scope and deployment identity. Do not represent environment using a data column.
- Schemas match bounded-context ownership: `reference`, `market_data`, `strategy`, `risk`, `execution`, `portfolio_ledger`, `operations`, `platform`, `research`, and `ai_memory` only at Phase 6.
- A context writes only its own schema through its public owner repository/port. No cross-context ORM model, FK, cascade, SQL update or table trigger is permitted.
- Same-context FK is allowed only when it expresses a durable invariant and its deletion behavior is documented. `CASCADE` is forbidden for financial, audit, event, fill, journal, posting, approval, outbox/inbox and evidence history.
- No generic `common`, `utility`, catch-all JSONB table or unowned schema is permitted.

## 3. Naming and type standard

| Object | Mandatory convention |
|---|---|
| Schema/table/column/index/constraint | lowercase `snake_case`; table plural theo mặc định — ngoại lệ hợp lệ: tên tập hợp/cơ chế dạng số ít đã chốt trong inventory master §7.6 (`outbox`, `inbox`, `outbox_delivery_state`, `limit_state`, `feed_health`, `audit_log`); constraint name expresses scope/purpose |
| Internal identity | `<thing>_id` of type `UUID`; UUIDv7 created by application, never venue ID/serial identity — ngoại lệ: logical name identity dạng TEXT được dictionary khai rõ (ví dụ `consumer_id` của inbox, DATA-003 §3) |
| External identity | explicit `venue_order_id`, `venue_fill_id`, `source_event_id`, etc.; not internal PK |
| Money/price/quantity/fee/PnL | `NUMERIC(38,18)` with non-negative/positive CHECK as domain requires |
| Time | `TIMESTAMPTZ`; UTC only; `*_at` semantic vocabulary from Master §5.1 |
| Version | `SMALLINT` for schema version > 0; `BIGINT` for aggregate/delivery sequence/version >= 0 |
| Boolean | PostgreSQL `BOOLEAN`, not integer/string surrogate |
| Status | `TEXT` with named CHECK or owned reference/version table; no magic free text |
| Hash | `CHAR(64)` SHA-256 hex only when a canonical hash is required |
| Large/vendor extension | `JSONB` strictly for validated/redacted payload or registered extension; never quantity/price/OMS/risk state |

`TIMESTAMP WITHOUT TIME ZONE`, `FLOAT`/`REAL`/`DOUBLE PRECISION` for domain finance, unbounded status semantics and database-generated UUIDv4 are forbidden in new tables.

## 4. Immutable, mutable and audit data

| Class | Examples | Required protection |
|---|---|---|
| Immutable domain/accounting/audit | fills, order events, journal entries, postings, approvals, audit log, integration events, outbox/inbox receipts, DLQ | runtime grants deny UPDATE/DELETE; append new fact/correction only |
| Mutable aggregate/projection | order current state, risk limit state, deployment, lease, delivery state, projections | `aggregate_version`/CAS or documented lease; update actor/time/audit path |
| Reference history | instrument rule/policy/capability versions | valid/effective ranges; no overwrite of prior effective truth |
| Technical cache | only specifically authorized rebuildable cache | must have owner/TTL/rebuild source; cannot become safety boundary |

Financial/audit immutability must be enforced by grants and approved database mechanism; an application convention alone is insufficient. Corrections use a new append-only record with original/evidence/approval links.

## 5. Constraints and integrity

- Primary keys are explicit; business uniqueness is stated in the dictionary and enforced where database scope allows.
- Required execution constraints include client order uniqueness per venue/account, venue order/fill dedupe where known, positive fill/order quantity, non-negative reservation, sequence uniqueness and posting line uniqueness.
- `CHECK` constraints protect local field invariants; application/domain validates richer policy and cross-context rules.
- FK only protects same-context relationship. Cross-context IDs are immutable references validated through contract, owner application/reconciliation.
- A nullable external ID must use partial uniqueness only when non-null.
- No trigger or stored procedure may hide risk/OMS policy. Database balance enforcement is the narrow exception only after ADR-0011 approves it.

## 6. Index and query-budget policy

Every new index requires a named owner, query shape, expected cardinality, write cost and test/plan evidence in the dictionary. Minimum approved query classes include: open orders by account/venue/state; order timeline; fill dedupe; active reconciliation; unpublished outbox; inbox dedupe; journal/postings by source/account; audit by actor/correlation; projection watermark.

Rules:

1. No index “just in case”.
2. Hot-path query without documented index/query budget is blocked.
3. Composite index column order follows equality filters, range/order, then selected support fields where justified.
4. Partial index predicate must mirror stable contract state and be tested.
5. Migration must consider lock/time/write amplification and use an approved safe technique when needed.

## 7. Roles, least privilege and connectivity

| Role | Allowed scope |
|---|---|
| `db_migrator` | DDL/migration only; not runtime |
| `db_control_api` | operations/config owner writes and projection reads through application scope |
| `db_trading_node` | required risk/execution/ledger writes; no DDL or historic audit delete |
| `db_data_worker` | market/reference writes only; no execution/ledger |
| `db_research_worker` | catalog/research writes and approved snapshots; no OLTP write model |
| `db_ai_worker` | sanitized projection read and Phase 6 AI-memory write only |

Credentials are environment-specific, secret-managed and never shared as a convenience. Dashboard/UI has no direct production database role. Role/GRANT statements belong to reviewed migration/operations material, not this narrative doc.

## 8. Time, lineage and retention

Every record uses only applicable canonical time fields. `recorded_at` is not a substitute for `occurred_at`; mutable projections use `updated_at`, while append-only facts do not. Business/reference policy needs `effective_at`/valid range. Rows that affect decisions/audit carry source/version/hash/correlation sufficient to replay why they exist.

Retention/purge, partition, archive and backup policy remain blocked on ADR-0013/OD-007. No hard delete is permitted for financial/audit/event history; platform cleanup needs explicit dedupe/replay-window proof.

## 9. DDL and migration discipline

- No database object without approved dictionary entry, task card and related ADR/requirement links.
- Alembic revision is immutable after apply; message includes Task ID and intent.
- Expand -> compatible code -> checkpointed backfill -> reader migration -> later contract/drop is mandatory for breaking change.
- Every migration has expected duration/lock assessment, rollback or forward-fix decision, old-snapshot upgrade test and evidence path.
- Financial/audit schema recovery defaults to forward-fix or tested restore, not destructive downgrade.

The detailed procedure is [migration and backfill playbook](migration-backfill-playbook.md).

## 10. Verification gate

- [ ] Schema has no cross-context FK/ORM leak or unowned table.
- [ ] Types/constraints match this policy and dictionary.
- [ ] Runtime role cannot mutate/delete immutable facts.
- [ ] Query/index plan and concurrent-write impact are documented.
- [ ] Migration, schema snapshot, docs and contract registry have one approved change set.

