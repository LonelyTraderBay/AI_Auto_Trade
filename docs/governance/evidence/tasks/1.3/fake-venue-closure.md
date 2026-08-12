# Task 1.3 — Local fake venue contract và conformance closure draft

| Trường | Giá trị |
|---|---|
| Document ID | GOV-TASK-1.3-CLOSURE-VENUE-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | APPROVED FOR TASK 1.3 DESIGN — chưa phải runtime contract |
| Parent | [Task 1.3 preflight](task-1.3-preflight.md) |
| Decision register | [OD-1.3 decisions](owner-decision-register.md) |
| Ngày lập | 2026-08-12 |

> Fake venue trong tài liệu này là simulator nội bộ, deterministic và không network. Tài liệu không cấp quyền kết nối exchange, venue SDK, credential hoặc testnet.

## 1. Boundary

Fake venue chỉ được nhận một request đã có:

- Internal order/attempt identity.
- Stable `client_order_id`.
- Request hash và idempotency context.
- Approved risk decision/reservation reference.
- Deterministic scenario ID/version.

Fake venue không được:

- Tự quyết định risk approval.
- Tạo internal order identity.
- Gọi network hoặc vendor SDK.
- Đọc secret/credential.
- Tự retry một external-looking submission.
- Sửa/xóa audit hoặc lifecycle history.

## 2. Proposed protocol envelope — review only

```text
FakeVenueSubmitRequest
  protocol_version
  scenario_id
  scenario_revision
  order_id
  client_order_id
  attempt_id
  request_hash
  submitted_at_utc
  order payload (Decimal values represented as strings)

FakeVenueSubmitResponse
  protocol_version
  scenario_id
  attempt_id
  outcome: ACCEPTED | REJECTED | PARTIAL_FILL | FILLED | CANCELLED | TIMEOUT | UNKNOWN
  venue_order_id (opaque, nullable)
  fills (immutable evidence, nullable)
  response_sequence
  response_timestamp_utc
  fault_code (safe enum, nullable)
```

Field names, enum version, error catalog mapping và nullability phải được duyệt trước khi tạo runtime contract/schema.

## 3. Scenario behavior matrix

| Scenario | Expected purpose | Required invariant |
|---|---|---|
| Immediate accept | Basic successful submit | Exactly one accepted side effect per client ID |
| Explicit reject | Venue validation failure | No fill; deterministic rejection reason |
| Partial then fill | Multiple lifecycle evidence | Ordering and aggregate quantity invariant |
| Duplicate response | Transport replay | Dedupe, no duplicate fill/order side effect |
| Out-of-order event | Broken delivery order | Reject/quarantine/reconcile according to contract |
| Timeout before response | No response | Persist unknown/timeout evidence; no blind retry |
| Ambiguous response | Request may have been received | `UNKNOWN` and reconciliation path only |
| Crash after apply | Process restarts after side effect | Replay produces same outcome without duplicate side effect |
| Lease loss | Execution leader fencing | Stale owner cannot submit or mutate current state |
| Invalid request | Contract/identity mismatch | Deterministic rejection before venue side effect |

Scenario scripts must pin clock, seed, revision and response sequence. They must not contain credentials or real venue/account data.

## 4. Conformance harness requirements

The harness must verify every adapter/simulator implementation against:

1. Protocol version and required field validation.
2. Decimal/string serialization without float conversion.
3. Stable client-order identity and request hash.
4. Idempotent duplicate submission behavior.
5. Deterministic scenario replay.
6. Partial-fill, fee and sequence semantics.
7. Timeout/UNKNOWN classification and no blind retry.
8. Out-of-order and duplicate evidence handling.
9. Clock/seed isolation and no network invocation.
10. No secret/credential access or logging.

The harness itself must be a test/evidence artifact with named owner before the first adapter task.

## 5. Contract and evidence dependencies

| Dependency | Status | Required before implementation |
|---|---|---|
| Fake venue protocol contract | Not created as runtime contract | Owner review and version |
| Scenario schema/fixture | Not created | Deterministic schema and fixture review |
| Order event contract | JSON Schema validates; task-scoped approval recorded; registry `IN_REVIEW` | Registry sync/implementation permission |
| Submit command contract | JSON Schema validates; task-scoped approval recorded; registry `IN_REVIEW` | Registry sync/implementation permission |
| Conformance harness | Design approved for Task 1.3; no runtime harness yet | Test owner and acceptance commands |
| Network/credential boundary | Policy exists | Negative test evidence |

## 6. Current status

- Local simulator scope is permitted in principle; external venue remains blocked by OD-001.
- No fake venue runtime adapter exists.
- No fake venue runtime schema or conformance harness exists.
- This draft does not authorize implementation.
