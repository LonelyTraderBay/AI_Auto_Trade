# Task 1.3 — Data và persistence closure draft

| Trường | Giá trị |
|---|---|
| Document ID | GOV-TASK-1.3-CLOSURE-DATA-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | APPROVED FOR TASK 1.3 DESIGN — không phải DDL hoặc migration authority |
| Parent | [Task 1.3 preflight](task-1.3-preflight.md) |
| Decision register | [OD-1.3 decisions](owner-decision-register.md) |
| Ngày lập | 2026-08-12 |

> Approval record `2026-08-12T09:19:16Z` chấp thuận phạm vi thiết kế. Tài liệu này vẫn không được dùng để tạo bảng/index/migration khi authority sync, task card `READY` và PostgreSQL evidence chưa hoàn tất.

## 1. Existing baseline

Các migration hiện có chỉ phục vụ platform delivery baseline và idempotency. Task 1.3 không được coi các migration đó là bằng chứng đã có execution/risk persistence.

## 2. Proposed logical entities — review only

| Context/entity | Mục đích | Tối thiểu cần chốt trước DDL |
|---|---|---|
| `execution.orders` | Canonical order aggregate và lifecycle version | Internal ID, client ID uniqueness, state/version, timestamps, intent/risk references, terminal reason |
| `execution.submission_attempts` | Mỗi external submission attempt/evidence | Attempt ID, order ID, request hash, attempt ordinal, outcome, unknown marker, sent/received timestamps, lease/fencing |
| `execution.order_events` | Append-only lifecycle/evidence event | Event ID, order partition, sequence, event type/version, payload reference, recorded timestamp, dedupe key |
| `execution.fills` | Immutable verified fill evidence | Fill identity/dedupe, order association, Decimal fields, fee fields, source fingerprint, sequence |
| `execution.reconciliation_cases` | Unknown/mismatch recovery evidence | Case ID, order/attempt reference, classification, evidence, resolution command, immutable history |
| `risk.policies` | Versioned immutable risk policy | Scope, version/hash, parameters, effective/expiry, status, approval evidence |
| `risk.decisions` | Deterministic risk verdict snapshot | Decision ID, intent/order reference, verdict, policy snapshot, input hash, expiry, reason |
| `risk.reservations` | Logical exposure/balance lock | Reservation identity, scope, amount/asset, lifecycle, policy snapshot, expiry, uniqueness |
| `risk.limit_state` | Mutable scoped counters/state | Scope key, version/CAS, counters, timestamps, reset window, fencing semantics |

Đây là inventory; table name/column name chỉ trở thành physical authority sau khi dictionary/ERD review.

## 3. Required dictionary fields

Mỗi row trước khi mở migration phải ghi:

- Schema/context và owner.
- Column name, PostgreSQL type, nullability và default.
- Financial precision/scale; không float.
- Primary/unique/foreign/reference key semantics.
- CAS/version, lease owner, fencing token nếu có.
- Index và query/access path.
- Append-only/immutability rule.
- Retention, purge/legal hold và audit requirement.
- Role read/write boundary.
- Contract/domain mapping.
- Seed/fixture and deterministic test requirements.
- Migration expand/contract, rollback/forward-fix và compatibility plan.

## 4. Constraint and transaction mapping

| Invariant | Proposed verification | Approval dependency |
|---|---|---|
| `(venue_id, account_id, client_order_id)` không reuse | Unique constraint + replay test | Canonical model/ERD |
| Một reservation kind cho order intent | Unique `(order_intent_id, reservation_kind)` | Risk policy |
| Fill immutable và dedupe | Unique venue identity/source fingerprint + conflict evidence | Fill contract |
| Order/event ordering | Aggregate version/CAS + sequence rule | OMS/event contract |
| Submit idempotency | Request hash + attempt uniqueness + replay behavior | Submit command registry |
| Lease fencing | Monotonic fencing token + stale-owner rejection | ADR-0012/data dictionary |
| Unknown không retry mù | State constraint + recovery workflow test | ADR-0012/risk policy |

## 5. Migration readiness gate

Không được tạo migration cho entity nào nếu thiếu một trong các mục sau:

1. Approved dictionary row cho toàn bộ columns/constraints/access/retention.
2. Approved ERD mapping và context ownership.
3. Approved ADR/requirement/contract links.
4. Migration expand/contract, rollback/forward-fix và immutable-history policy.
5. Database role/grant and secret boundary review.
6. Integration test chạy PostgreSQL thật với pinned UTC/seed/Decimal context.
7. Task card implementation `READY` cho đúng migration paths.

## 6. Required PostgreSQL evidence

Evidence tối thiểu cần thu thập sau khi có test environment:

- Migration upgrade từ baseline và downgrade/forward-fix policy.
- Unique/CAS/lease/fencing conflict tests.
- Serialization/deadlock retry trước external call.
- Crash/restart giữa persist intent, commit, claim và external response.
- Duplicate event/fill and replay tests.
- Role/permission denial tests.
- `DATABASE_URL` redaction check trong logs/evidence.

## 7. Current status

- Data dictionary/ERD: task-scoped design approved; normative files vẫn cần đồng bộ status/nội dung.
- Execution/risk migrations: chưa tồn tại.
- PostgreSQL integration evidence: chưa có; test hiện skip khi thiếu `DATABASE_URL`.
- Task 1.3 implementation: `BLOCKED`, chưa được tạo migration.
