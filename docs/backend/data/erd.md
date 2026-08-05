# DATA-002 — Conceptual ERD and relationship contract

| Thuộc tính | Giá trị |
|---|---|
| Document ID | DATA-ERD-001 (registry DOCS_INDEX; title giữ alias ngắn) |
| Phiên bản | 0.4.0 |
| Trạng thái | DRAFT — chờ Account Owner phê duyệt |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày soạn | 2026-07-31 |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-08-02 |
| Liên quan | FR-MKT-001, FR-EXEC-001, FR-LED-001, FR-REC-001, FR-AI-001, NFR-AUD-001, NFR-AI-001; ADR-0003, ADR-0004, ADR-0005, ADR-0011, ADR-0012, ADR-0016 |
| Nguồn policy | [Master specification](../../../AI_AUTO_TRADE_MASTER_SPEC.md), §4.2, §7.4–§7.8, §8, §10.6 |
| Change summary | 0.4.0 (2026-08-02): §2 bổ sung `data_quality_issues` vào context map (khớp §4.1/master §7.6); chuẩn hóa header theo GOV-DOC-001 §3 (audit toàn diện). |

## 1. Reading rules

This is a conceptual ERD. A line across contexts means immutable ID/event/read-contract association, **not** a physical foreign key. Only relationships inside one schema/context may become foreign keys, subject to the approved dictionary and migration. Table names are logical until their task card and migration exist.

All internal keys are UUIDv7/`UUID`. Financial values are `NUMERIC(38,18)`, time values are UTC `TIMESTAMPTZ`, and no core state is modeled as opaque JSONB.

## 2. Context-level map

```text
reference: venues --- accounts --- assets --- instruments --- instrument_rule_versions
                 \                         \
                  \--> capability_profiles  \--> market_data catalog/checkpoints/feed_health/data_quality_issues

strategy: definitions --- versions --- instances --- checkpoints
                                      |
                                      | ProposedOrderIntent / immutable IDs
                                      v
risk: policies --- decisions --- reservations --- pending_approvals --- limit_state
                                      |
                                      | approved intent / decision event
                                      v
execution: orders --- order_events
              |  \--- submission_attempts
              |  \--- fills
              \--- reconciliation_cases --- reconciliation_evidence
                         |
                         | verified fill / approved adjustment command
                         v
portfolio_ledger: chart_of_accounts --- journal_entries --- postings
                                        |                    |
                                        +--> balance/position projections/checkpoints

research (Phase 2, inventory-only): dataset_versions --- feature_definitions --- backtest_runs --- evaluation_reports

operations: deployments, runtime_leases, kill_switches, commands --- command_events
                                      \ approvals / audit_log / incidents
                                      \ ai_provider_connections --- ai_connection_events

ai_memory (Phase 6 only): inference_runs --- proposals / memory_items / retrieval_runs / post_mortems
       ^
       | immutable connection revision and sanitized provenance only; no raw key
operations.ai_provider_connections

platform: outbox --- outbox_delivery_state; inbox; dead_letters; idempotency_keys
```

## 3. Task 0.3 physical ERD: platform delivery baseline

Only the following platform tables are proposed for the first migration. They form one owner schema and may use physical FK only where noted.

```text
platform.outbox (1) ---- (1) platform.outbox_delivery_state
       |
       | message/event is consumed by many consumers; no FK to consumer context
       v
platform.inbox (dedupe receipt per consumer + event)

platform.outbox (0..1) ---- (0..N) platform.dead_letters
```

| Relationship | Cardinality | Physical integrity | Meaning |
|---|---|---|---|
| outbox -> outbox_delivery_state | 1:1 | same-schema FK / unique key, proposed | one immutable message has one mutable publisher delivery state |
| outbox -> dead_letters | 0..1:N | nullable same-schema FK (`dead_letters.outbox_id`), proposed | each terminal/repeated failure is immutable evidence; `outbox_id` null when the dead letter originates from consumer/inbox side; no payload secret |
| inbox -> source event | N:1 conceptual | no cross-context FK | each consumer records at most one successful/committed handling of an event |
| outbox -> domain aggregate | N:1 conceptual | no cross-context FK | `source_context`/`subject_id` are trace/audit references only |

## 4. Logical v1 entity relationships

### 4.1 Reference and market data

| Parent | Child | Relationship rule |
|---|---|---|
| `reference.venues` | `accounts`, `instruments`, `capability_profiles` | same-context FK permissible; version/snapshot identity preserved |
| `reference.instruments` | `instrument_rule_versions` | 1:N, valid/effective ranges cannot overlap for same rule type unless explicit version semantics approve it |
| `reference.instruments` | `market_data.catalog_partitions` | cross-context immutable `instrument_id`, no FK |
| `catalog_partitions` | `ingestion_checkpoints`, `data_quality_issues` | same context link allowed; raw events live in Parquet and manifest/checksum are required |

### 4.2 Strategy, risk and execution

| Parent | Child | Relationship rule |
|---|---|---|
| `strategy.definitions` | `versions` | 1:N; version immutable after activation |
| `strategy.versions` | `instances` | 1:N; instance pins a version/config/deployment hash |
| `strategy.instances` | `checkpoints` | 1:N immutable checkpoint history or latest pointer per approved design |
| `risk.policies` | `decisions` | 1:N; decision preserves policy version/hash |
| `risk.decisions` | `reservations` | conceptual/direct same-context link where applicable; order intent ID remains immutable cross-context reference |
| `execution.orders` | `order_events`, `submission_attempts`, `fills` | 1:N inside execution schema; all histories append-only |
| `execution.orders` | `reconciliation_cases` | 0:N; one case can cover broader account scope with optional order reference |
| `reconciliation_cases` | `reconciliation_evidence` | 1:N append-only evidence |

`OrderIntentId`, strategy/risk/reference IDs on `execution.orders` are cross-context references and must not create foreign keys to their owner tables.

### 4.3 Ledger and operations

| Parent | Child | Relationship rule |
|---|---|---|
| `chart_of_accounts` | `postings` | 1:N inside ledger schema; account effectiveness/version rules enforced by approved policy |
| `journal_entries` | `postings` | 1:N; `UNIQUE(journal_entry_id, line_no)`; entry balance enforced in DB write path |
| ledger source event | journal entry | conceptual immutable source ID/type/event reference, no FK to execution |
| `operations.commands` | `command_events` | 1:N; `UNIQUE(command_id, sequence)`; events append-only |
| command / risk subject | `operations.approvals` | conceptual ID link only; approvals do not mutate risk state directly |
| operations action | `audit_log` | 1:N append-only evidence with actor/machine/correlation fields |
| `operations.ai_provider_connections` | `ai_connection_events` | 1:N append-only lifecycle metadata; same-schema FK only after Phase 6 dictionary/migration approval; no raw key/binding-to-secret mapping |

### 4.4 Deferred AI/BYOK relationships

| Parent | Child | Relationship rule |
|---|---|---|
| `operations.ai_provider_connections` | `ai_connection_events` | 1:N append-only metadata for create/validate/activate/suspend/rotate/revoke; owner scope/version is retained; no secret body/value. |
| connection revision | `ai_memory.inference_runs` | cross-context immutable ID/version reference, no FK; run records selected provider/model/catalog/adapter/policy provenance only. |
| `ai_memory.inference_runs` | `proposals`, `memory_items`, `retrieval_runs` | same-context links permitted only after approved Phase 6 data dictionary; structured output/provenance/retention checks apply. |

The secret provider is intentionally absent from this ERD. Internal active/candidate binding IDs are opaque metadata; mapping to raw key is outside PostgreSQL and never a public API/database relationship. Candidate binding exists only for validation/rotation and does not permit inference.

## 5. Key and uniqueness contract

| Entity | Primary key | Mandatory business uniqueness / constraint |
|---|---|---|
| execution order | `order_id` | `(venue_id, account_id, client_order_id)`; venue order uniqueness when non-null; positive quantity; non-negative aggregate version |
| execution fill | `fill_id` | venue fill ID when present, otherwise source event/fingerprint in venue/account; positive quantity |
| order event | event ID | `(order_id, sequence)` unique |
| submission attempt | attempt ID | `(order_id, attempt_no)` unique and `attempt_no > 0` |
| risk reservation | reservation ID | `(order_intent_id, reservation_kind)` unique; reserved amount non-negative |
| platform inbox | receipt ID | `(consumer_id, event_id)` unique |
| platform idempotency key | idempotency ID | `(actor_id, route_scope, idempotency_key)` unique |
| operations command event | event ID | `(command_id, sequence)` unique |
| ledger posting | posting ID | `(journal_entry_id, line_no)` unique |

## 6. Deferred entity policy

An entity may be shown in §2 but remains deferred until all conditions are true: (1) phase/task authorizes it, (2) dictionary row contains full columns/constraints/access/retention, (3) relevant ADR is APPROVED, (4) contract/fixture and migration/forward-fix plan are reviewed, and (5) no existing owner table can meet the requirement without violating boundaries.

Examples explicitly deferred now: all AI/BYOK entities until ADR-0008 + ADR-0016 and Phase 6 task/gate; venue-specific private data; authentication/session tables; all research/Parquet metadata until Phase 2; trading/risk/ledger tables until Phase 1. An implementation must not turn this ERD into speculative DDL.

## 7. Review checklist

- [ ] Relationship crossing a context has no FK/ORM cascade/direct table write.
- [ ] All mutable aggregate state has `aggregate_version`/concurrency rule where required.
- [ ] All append-only facts retain event/source/effective/recorded timestamps and evidence lineage.
- [ ] Every same-schema FK has a documented delete rule; financial/audit history never uses cascade delete.
- [ ] Exact physical columns are sourced from [data dictionary](data-dictionary.md), not inferred from this diagram.

## 8. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.3.0 | 2026-07-31 | Sửa mâu thuẫn FK `dead_letters`: quan hệ đúng là `platform.outbox (0..1) ---- (0..N) platform.dead_letters` qua `dead_letters.outbox_id` nullable (theo data dictionary, authoritative); bổ sung entity còn thiếu theo inventory: `assets` (reference), `feed_health` (market_data), context `research` (dataset_versions/feature_definitions/backtest_runs/evaluation_reports — Phase 2, inventory-only) và `post_mortems` (ai_memory). | Technical Operator | Pending |
