# Task 1.3 — Execution/Risk data dictionary addendum

| Trường | Giá trị |
|---|---|
| Document ID | DATA-DICT-T1.3-ADDENDUM-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | APPROVED FOR TASK 1.3 DESIGN — không phải DDL authority |
| Parent | [One-time approval packet](ONE-TIME-APPROVAL-PACKET.md) |
| Related | DATA-DICT-001, DATA-ERD-001, DATA-TXN-001, ADR-0003, ADR-0012 |

> Approval record `2026-08-12T09:19:16Z` chấp thuận các row ở mức thiết kế. Chưa được tạo migration và không được coi là physical schema cho đến khi dictionary/ERD sync và task card `READY`.

## 1. Common physical rules

- PostgreSQL 16.x policy baseline; UTC `TIMESTAMPTZ`.
- Internal identifiers là UUIDv7 lưu `UUID`.
- Financial/quantity values là `NUMERIC(38,18)`; API representation là string.
- Runtime role không được `DELETE`/`UPDATE` append-only facts hoặc chạy DDL.
- Mọi mutable aggregate có `version BIGINT NOT NULL CHECK (version >= 0)` cho CAS.
- Mọi external-looking request có `request_hash CHAR(64)` hoặc approved equivalent và correlation IDs.
- Cross-context references là immutable UUID, không tạo FK xuyên context nếu boundary cấm.

## 2. Proposed rows

### 2.1. `execution.orders`

| Column | Type/nullability | Constraint/meaning |
|---|---|---|
| `order_id` | UUID NOT NULL | PK; UUIDv7 internal ID |
| `order_intent_id` | UUID NOT NULL | Immutable cross-context reference |
| `client_order_id` | TEXT NOT NULL | Unique with `(venue_id, account_id)`; never reuse |
| `venue_id` | TEXT NOT NULL | Synthetic fake venue scope in Task 1.3 |
| `account_id` | UUID NOT NULL | Scope reference; no raw credential |
| `instrument_id` | UUID NOT NULL | Immutable instrument reference |
| `state` | TEXT NOT NULL | Canonical OMS state enum; CHECK/contract mapping |
| `terminal_reason` | TEXT NULL | Required when terminal; immutable after terminal except correction contract |
| `aggregate_version` | BIGINT NOT NULL | CAS; non-negative |
| `request_hash` | CHAR(64) NOT NULL | Canonical submit request hash |
| `created_at`/`expires_at` | TIMESTAMPTZ NOT NULL | UTC; expiry checked before submit |
| `recorded_at` | TIMESTAMPTZ NOT NULL | Audit timestamp |
| `correlation_id` | UUID NOT NULL | Trace/audit correlation |

### 2.2. `execution.submission_attempts`

| Column | Type/nullability | Constraint/meaning |
|---|---|---|
| `attempt_id` | UUID NOT NULL | PK; UUIDv7 |
| `order_id` | UUID NOT NULL | Same-context FK candidate after ERD approval |
| `attempt_ordinal` | INTEGER NOT NULL | Unique `(order_id, attempt_ordinal)`; positive |
| `request_hash` | CHAR(64) NOT NULL | Must match approved request identity |
| `outcome` | TEXT NOT NULL | Accepted/rejected/timeout/unknown enum |
| `venue_order_id` | TEXT NULL | Opaque external ID; nullable before ack |
| `lease_owner` | TEXT NULL | Machine identity/claim owner |
| `fencing_token` | BIGINT NULL | Monotonic; stale owner rejected |
| `sent_at`/`received_at` | TIMESTAMPTZ NULL | UTC; no fake precision claims |
| `recorded_at` | TIMESTAMPTZ NOT NULL | Append-only audit timestamp |
| `evidence_json` | JSONB NOT NULL | Redacted, schema-bound, no secret/raw credential |

### 2.3. `execution.order_events`

| Column | Type/nullability | Constraint/meaning |
|---|---|---|
| `event_id` | UUID NOT NULL | PK; UUIDv7 |
| `order_id` | UUID NOT NULL | Partition/order reference |
| `sequence` | BIGINT NOT NULL | Unique `(order_id, sequence)`; positive ordering |
| `event_type`/`schema_version` | TEXT NOT NULL | Registry-bound event type/version |
| `payload_json` | JSONB NOT NULL | Contract-validated, redacted |
| `recorded_at` | TIMESTAMPTZ NOT NULL | Immutable UTC record |
| `correlation_id`/`causation_id` | UUID NOT NULL/NULL | Trace lineage |

### 2.4. `execution.fills`

| Column | Type/nullability | Constraint/meaning |
|---|---|---|
| `fill_id` | UUID NOT NULL | PK; UUIDv7 |
| `order_id` | UUID NOT NULL | Same-context association |
| `venue_fill_id` | TEXT NULL | Dedupe within venue/account when present |
| `source_fingerprint` | CHAR(64) NOT NULL | Required when venue fill ID absent; deterministic |
| `price`/`quantity`/`fee_amount` | NUMERIC(38,18) NOT NULL | Positive price/quantity; non-negative fee |
| `fee_asset` | TEXT NULL | Required when fee non-zero |
| `liquidity_flag` | TEXT NOT NULL | `MAKER|TAKER|UNKNOWN` |
| `sequence` | BIGINT NOT NULL | Ordering only; unique `(order_id, sequence)` |
| `occurred_at`/`received_at`/`processed_at`/`recorded_at` | TIMESTAMPTZ NOT NULL | UTC lifecycle timestamps |
| `quality_flags` | JSONB NOT NULL | Explicit missing-fee/source quality; no implicit guess |

### 2.5. `execution.reconciliation_cases`

| Column | Type/nullability | Constraint/meaning |
|---|---|---|
| `case_id` | UUID NOT NULL | PK; UUIDv7 |
| `order_id`/`attempt_id` | UUID NOT NULL | Immutable association |
| `classification` | TEXT NOT NULL | UNKNOWN/duplicate/out-of-order/mismatch enum |
| `status` | TEXT NOT NULL | OPEN/IN_PROGRESS/RESOLVED/BLOCKED |
| `evidence_json` | JSONB NOT NULL | Redacted append-only evidence |
| `resolution_command_id` | UUID NULL | Owner-approved resolution reference |
| `opened_at`/`resolved_at` | TIMESTAMPTZ NULL | UTC; resolution cannot erase history |

### 2.6. `risk.policies`, `risk.decisions`, `risk.reservations`, `risk.limit_state`

Các entity này chỉ được mở sau risk fixture approval. Tối thiểu phải có:

- Policy: scope, version, policy hash, parameters JSON Schema, effective/expiry, approval evidence, immutable status.
- Decision: decision ID, order intent, verdict, policy version/hash, input snapshot hash, reservation ID, reason, expiry, recorded timestamps.
- Reservation: reservation ID, order intent, kind, asset, amount NUMERIC(38,18), lifecycle, expiry/release/consume timestamps, unique `(order_intent_id, reservation_kind)`.
- Limit state: scope key, counters, reset window/timezone, aggregate version/CAS, updated timestamp, fencing/lease metadata.

## 3. Required review decisions

Account Owner/Risk Approver must confirm:

1. Exact CHECK/UNIQUE rules and whether candidate same-context FKs are allowed.
2. Role grants for runtime, migrator, test and read-only audit projection.
3. JSONB payload allowlist/redaction and maximum size.
4. Retention/hold rule or explicit `DEFERRED` to ADR-0013/Phase 2.
5. Index/partition strategy or explicit no-partition baseline for local simulator.
6. Migration expand/contract and forward-fix/rollback behavior.

## 4. Gate

No DDL/migration can be created from this addendum until the dictionary, ERD, ADR links, task card, roles/grants, retention and PostgreSQL integration plan are approved.
