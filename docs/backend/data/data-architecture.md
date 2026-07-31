# DATA-001 — Data architecture and ownership

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 0.2.0 |
| Trạng thái | DRAFT — chờ Account Owner phê duyệt |
| Owner | Technical Operator |
| Approver | Account Owner |
| Ngày soạn | 2026-07-31 |
| Liên quan | FR-MKT-001, FR-EXEC-001, FR-LED-001, FR-REC-001, FR-AI-001, NFR-DET-001, NFR-AUD-001, NFR-SAFE-001, NFR-OPS-001, NFR-AI-001; ADR-0003, ADR-0004, ADR-0011, ADR-0012, ADR-0013, ADR-0016 |
| Nguồn policy | [Master specification](../../../AI_AUTO_TRADE_MASTER_SPEC.md), §3, §5, §7, §8, §9, §10.6, §12 |

## 1. Mục tiêu

Kiến trúc dữ liệu phải cho phép replay, audit, recovery và reconciliation mà không biến MVP thành nhiều database hoặc microservice. PostgreSQL 16.x là system of record cho control/execution/ledger/audit/delivery metadata. Parquet catalog là store append-only cho market historical data/dataset; nó không thay PostgreSQL trong giao dịch hoặc accounting.

Tài liệu này là logical/physical design baseline, không phải migration. Chỉ [data dictionary](data-dictionary.md) đã được phê duyệt cùng task card mới có thể mở đường cho DDL.

## 2. System of record và boundary

| Data class | Source of truth | Owner | Cách đọc/ghi | Không được dùng làm |
|---|---|---|---|---|
| Control, OMS, risk, ledger, audit, outbox/inbox | PostgreSQL 16.x | bounded context tương ứng | owner repository/port, transaction có policy | file cache hoặc JSONB state tự do |
| Market raw bronze / normalized historical | Parquet catalog + manifest/checksum | `market_data` | atomic publish qua catalog metadata | OLTP order/risk store |
| Silver/gold dataset, research result | Parquet + dataset/backtest manifest | `market_data` / `research` | snapshot/reproducible reader | live execution write model |
| Effective runtime config/deployment | validated immutable manifest + config hash | `operations` | control/operations contract | env override business policy |
| Public command/event/config shape | versioned OpenAPI/JSON Schema | contract owner context | `contracts/` + registry | inferred ORM model |
| Gate/evidence/ADR | version-controlled docs/artifact store | operations/governance | append/retain evidence | runtime source without validation |

## 3. Environment isolation and tenancy

Mỗi local, CI, paper, testnet và canary environment phải dùng PostgreSQL database, credential, backup scope và deployment manifest riêng. Environment không được là một cột trong shared database. MVP là single tenant/single account scope, nhưng record execution/risk/ledger/reconciliation vẫn mang `account_id` và `venue_id` khi áp dụng để trace/audit.

Không xử lý credential raw, secret hoặc withdrawal authority trong business tables/JSONB/logs. Reference account record chỉ chứa canonical identity/scope/classification cần cho logic; secret metadata thuộc security/secret system. AI BYOK connection có owner scope (MVP là Account Owner/account environment) nhưng không biến database trading thành multi-tenant; connection metadata chỉ lưu opaque active/candidate binding, resolved policy-profile/endpoint/egress/usage/version metadata, không lưu key, encrypted key blob hay secret reference public. Candidate binding is validation-only; public API/event never returns either binding.

## 4. Schema ownership model

| PostgreSQL schema | Context owner | Logical v1 tables | Notes |
|---|---|---|---|
| `reference` | reference | venues, accounts, assets, instruments, instrument_rule_versions, capability_profiles | reference/rule history versioned; no overwrite |
| `market_data` | market_data | catalog_partitions, ingestion_checkpoints, feed_health, data_quality_issues | raw large data lives in Parquet |
| `strategy` | strategy | definitions, versions, instances, checkpoints | no direct venue/database access from strategy domain |
| `risk` | risk | policies, decisions, reservations, pending_approvals, limit_state | policy version immutable after activation |
| `execution` | execution | orders, order_events, submission_attempts, fills, reconciliation_cases, reconciliation_evidence | OMS/venue evidence only |
| `portfolio_ledger` | portfolio_ledger | chart_of_accounts, journal_entries, postings, balance_projections, position_projections, projection_checkpoints | journal/posting is accounting truth |
| `operations` | operations | deployments, runtime_leases, kill_switches, commands, command_events, approvals, audit_log, incidents, ai_provider_connections, ai_connection_events | control/audit/lease + owner-scoped AI connection metadata; no raw key |
| `platform` | platform | outbox, outbox_delivery_state, inbox, dead_letters, idempotency_keys | delivery infrastructure, not hidden business context |
| `research` | research | dataset_versions, feature_definitions, backtest_runs, evaluation_reports | no direct OLTP write model |
| `ai_memory` | ai_memory | memory_items, retrieval_runs, inference_runs, proposals, post_mortems | Phase 6 only; inference provenance/usage but no raw credential |

The complete conceptual relationships are in [ERD](erd.md). A context owns its schema/table and public repository/port. Cross-context FK, ORM relationship and direct SQL are forbidden. Cross-context integrity uses immutable IDs, contracts/events, read projections and reconciliation.

## 5. Physical scope by delivery phase

| Scope | Permitted physical tables | Gate / rationale |
|---|---|---|
| Phase 0.0 | none | documentation only; no migration/DDL |
| Task 0.3 | `platform.outbox`, `platform.outbox_delivery_state`, `platform.inbox`, `platform.dead_letters` | establishes at-least-once delivery/dedupe; exact proposal in dictionary remains DRAFT until task approval |
| Task 0.5 | `operations` control tables and `platform.idempotency_keys` only when OpenAPI/config/authorization design is approved | API command lifecycle needs named contract |
| Phase 1 | only tables proven necessary for fake venue OMS/risk/ledger/recovery and listed in approved dictionary/migration | ADR-0005/0007/0011/0012 required |
| Phase 2 | market/reference/research catalog tables and Parquet manifest/control rows | ADR-0013 + retention matrix required |
| Phase 3+ | venue/private data, auth/session, canary additions only in separately approved tasks | OD/ADR/gate dependent |
| Phase 6 | approved `operations` AI connection metadata and `ai_memory` tables only after ADR-0008 + ADR-0016 | proposal-only; no raw key, trade credential path or unapproved data egress |

“Logical v1 inventory” is a design inventory, not authorization to create every listed table. Any table not in an approved task dictionary is deferred, even if listed above.

## 6. Common physical conventions

| Concern | Mandatory convention |
|---|---|
| Internal primary/foreign identity | PostgreSQL `UUID`, UUIDv7 generated by application; venue IDs stored separately |
| Financial fields | `NUMERIC(38,18)`, non-float; scale > 18 unsupported without ADR/migration |
| Times | `TIMESTAMPTZ` UTC; semantic suffix `_at`; use the canonical timestamp vocabulary |
| Text/enums | `TEXT`/`VARCHAR` with named CHECK or reference table where evolution/audit requires; no unbounded magic status |
| JSONB | vendor payload, redacted evidence metadata or versioned extension only; never core money/lifecycle/risk state |
| Versioning | `schema_version`, aggregate/policy version and `aggregate_version` where applicable |
| Hashes | canonical JSON SHA-256 written as fixed semantic hash field; raw payload retention/redaction follows policy |
| Deletes | financial/audit/event/fill history never hard-delete; archival is immutable |
| Time history | reference/rule data uses `effective_at`, `valid_from`, `valid_to`; no overwrite of previous effective fact |

## 7. Data flows and transaction boundaries

```text
owner-context aggregate change
  + domain/integration event + platform.outbox message
        -- one PostgreSQL transaction --> commit
  -> outbox publisher (lease/claim) -> at-least-once delivery
  -> consumer owner transaction + platform.inbox dedupe marker
  -> own state/event/outbox commit
```

The in-process bus dispatches only committed events. It is not a substitute for outbox when a different worker/process consumes the event. External venue I/O is always after database commit. Detailed isolation, locks and retry rules are in [transaction and concurrency](transaction-and-concurrency.md).

## 8. Data classification and lineage

| Classification | Examples | Control |
|---|---|---|
| Public market/reference | public venue data, instrument rules | source checksum, license/retention review |
| Operational confidential | account IDs, order metadata, deployment/incident facts | least privilege, redact log/evidence copies |
| Financial/audit critical | fill, journal, posting, approval, audit event | append-only, immutable archive, restore/reconciliation validation |
| Secret | credential, token, private key | never in these tables/docs/contracts/fixtures; secret manager only |
| Controlled AI egress | sanitized prompt/input, structured AI output, usage metadata | provider/model/endpoint allowlist, owner scope, egress policy, redaction/hash and explicit retention policy |

Every derived result must be traceable to source/version: market/catalog manifest, reference/rule version, strategy/config/deployment hash, policy version, source event, accounting policy, adapter version and code/image version where relevant.

## 9. Read/write policy

Runtime roles follow least privilege. `db_migrator` is the only DDL role; `db_control_api`, `db_trading_node`, `db_data_worker`, `db_research_worker`, `db_ai_worker` receive only owner-scope access described by Master §7.9. `db_ai_worker` may read only active, policy-filtered connection metadata through an owned port and write AI provenance/proposal/memory records; it never reads raw credential or secret-store mapping. Dashboard has no production DB role. Query/index budgets are part of each dictionary entry; no unapproved query enters a hot path.

## 10. Lifecycle, retention and backup

Data lifecycle stays DRAFT until ADR-0013, OD-007 and retention matrix are approved before Phase 2. Minimum non-negotiable policy is no hard delete of financial/audit history. Parquet publish uses temporary path, checksum, validation and commit marker; catalog publishes only completed partitions. PostgreSQL backup consistency includes WAL, Parquet/catalog manifests, evidence and config/deployment/ADR/gate artifacts required for replay/audit.

## 11. Approval and change gates

- [ ] Table has data dictionary entry, owner, classification, retention and query/index evidence.
- [ ] DDL/migration has approved task card and ADR/requirement links.
- [ ] Cross-context dependency is contract/ID/event, not direct FK/ORM.
- [ ] New mutable state has concurrency/transaction ownership documented.
- [ ] New financial/audit data has append-only, balance/audit and forward-fix plan.
- [ ] Phase 6 AI table stores only safe metadata/provenance; owner-scope, retention, egress and secret-boundary tests are linked to ADR-0016.
- [ ] Schema, dictionary, contract registry and migration remain in sync or deployment is BLOCKED.
