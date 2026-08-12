# Task 1.3 — Owner/Risk decision register

| Trường | Giá trị |
|---|---|
| Document ID | GOV-TASK-1.3-DECISIONS-001 |
| Phiên bản | 0.5.0 |
| Trạng thái | APPROVED WITH SAFETY BOUNDARIES; authority sync and runtime evidence pending |
| Owner | Technical Operator |
| Required reviewers | Account Owner; Risk Approver khi quyết định ảnh hưởng risk; Security/Backup Owner cho access, logging, runbook, DB và threat controls |
| Parent package | [Task 1.3 preflight](task-1.3-preflight.md) |
| Ngày lập | 2026-08-12 |

> Bảng này chỉ ghi nhận quyết định cần được con người phê duyệt. Việc điền giá trị không tự chuyển tài liệu liên quan sang `APPROVED` và không mở quyền code.

## 1. Quy tắc ghi nhận

- Mỗi quyết định phải có giá trị cụ thể hoặc ghi rõ `DEFERRED` cùng phase/task đích.
- Không dùng giá trị ngầm định trong code để thay cho ô còn trống.
- Giá trị tiền, giá, quantity, fee và exposure phải ghi rõ đơn vị, Decimal precision/scale và rounding rule.
- Quyết định risk phải có Risk Approver; canary/live scope còn cần Account Owner theo RACI.
- Quyết định database phải liên kết data dictionary, ERD, ADR và migration/rollback plan.
- Quyết định contract phải liên kết version, fixture, compatibility rule và reviewer.
- Mọi approval phải có actor, role, UTC timestamp, reason, expiry/supersession nếu áp dụng.

## 2. Decision register

| ID | Nhóm | Câu hỏi cần quyết định | Giá trị/định dạng bắt buộc | Owner | Reviewer | Trạng thái |
|---|---|---|---|---|---|---|
| OD-1.3-01 | Scope | Task 1.3 có chỉ chạy local simulator/no external venue không? | `LOCAL_ONLY` hoặc scope được phê duyệt; không credential/network | Account Owner | Account Owner | ACCOUNT_OWNER_APPROVED |
| OD-1.3-02 | Fake venue | Protocol request/response và version là gì? | Envelope, correlation ID, client order ID, idempotency, protocol version | Technical Operator | Account Owner | ACCOUNT_OWNER_APPROVED |
| OD-1.3-03 | Scenario | Script deterministic biểu diễn delay/fault như thế nào? | Versioned scenario schema; sequence, clock, seed, duplicate, out-of-order, timeout, crash | Technical Operator | Account Owner | ACCOUNT_OWNER_APPROVED |
| OD-1.3-04 | UNKNOWN | Sau timeout/unknown outcome, trạng thái và operator action nào? | Persisted state, reconciliation/query path, no blind retry, evidence requirement | Risk Approver | Account Owner | APPROVED_BY_RISK_AND_OWNER |
| OD-1.3-05 | Idempotency | Phạm vi khóa idempotency là gì? | Unique key, request hash conflict, replay response, terminal replay behavior | Technical Operator | Account Owner | ACCOUNT_OWNER_APPROVED |
| OD-1.3-06 | Identity | Internal/external identity nào được dùng? | UUIDv7 internal IDs; opaque venue IDs; client ID uniqueness scope | Technical Operator | Account Owner | ACCOUNT_OWNER_APPROVED |
| OD-1.3-07 | Fill | Fill/fee/rebate semantics nào là canonical? | Required fields, nullable rules, Decimal scale, fee asset, liquidity flag, source fingerprint, ordering | Technical Operator | Account Owner | APPROVED_BY_RISK_AND_OWNER |
| OD-1.3-08 | Risk | Risk policy parameters cho local simulator là gì? | Exposure/notional/rate/loss/drawdown caps, freshness, expiry, reservation and kill-switch defaults | Risk Approver | Account Owner | APPROVED_BY_RISK_AND_OWNER |
| OD-1.3-09 | Concurrency | Transaction/isolation/CAS/lease boundary nào áp dụng? | UoW map, lock order, isolation, CAS version, fencing token, lease TTL/expiry | Technical Operator | Account Owner | APPROVED; ADR_AMENDMENT_REQUIRED |
| OD-1.3-10 | Persistence | Bảng/column/constraint/index/retention nào được mở? | Approved dictionary and ERD rows; schema role; migration and forward-fix plan | Technical Operator | Account Owner | APPROVED; DICTIONARY_ERD_SYNC_REQUIRED |
| OD-1.3-11 | Contracts | Command/event/fake-venue artifacts nào được implement? | Registry ID, version, fixture, compatibility and approval evidence | Technical Operator | Account Owner | APPROVED; REGISTRY_SYNC_REQUIRED |
| OD-1.3-12 | Ledger | Ledger runtime có được mở trong Task 1.3 không? | Recommended value: `DEFERRED`; accounting annex remains a prerequisite | Account Owner | Risk Approver | APPROVED; DEFERRED |

## 2.1. Baseline đối chiếu — provenance trước approval

Phần này ghi lại provenance của candidate baseline trước approval. Sau approval record v0.3.0, chỉ các giá trị nằm trong phạm vi P-01..P-68 và task card mới được dùng; mọi DDL/runtime vẫn cần authority sync và evidence riêng.

| ID | Candidate baseline có thể kế thừa | Nguồn đối chiếu | Phần còn phải chốt |
|---|---|---|---|
| OD-1.3-01 | `LOCAL_ONLY`; không external network/credential | Master §0, AGENTS.md, OD-001 OPEN | Account Owner xác nhận scope và môi trường |
| OD-1.3-02 | Envelope nội bộ versioned, có correlation/attempt/client ID/request hash | Submit command và order-event schema hiện có; registry vẫn IN_REVIEW | Tên field, version, fake-venue schema và compatibility |
| OD-1.3-03 | Scenario pin revision + UTC clock + seed + ordered response sequence | ENG-TEST-001 fixture rules; Task 1.1 deterministic primitives | Format script, fault enum, delay model và replay policy |
| OD-1.3-04 | `UNKNOWN`/reconciliation; không blind retry; lease loss dừng submit mới | DATA-TXN-001 §unknown; ADR-0012 | Query/reconcile command, operator action và evidence SLA |
| OD-1.3-05 | Dedupe bằng stable client ID/request hash; conflict không overwrite | DOM-MODEL-001; submit-order schema | Exact uniqueness scope, replay response và conflict error |
| OD-1.3-06 | UUIDv7 internal; venue IDs opaque; client ID không reuse trong venue/account | DOM-MODEL-001 §identity; DATA-TXN-001 | Exact database constraints và external reference retention |
| OD-1.3-07 | Fill immutable; Decimal/string; fee asset/liquidity flag; venue ID hoặc source fingerprint dedupe | DOM-MODEL-001 §7.5; DOM-OMS-001 | Precision/scale, rounding, rebate, missing-fee quality flag |
| OD-1.3-08 | Không tự chọn cap; chỉ dùng signed immutable policy snapshot | DOM-RISK-001 vẫn DRAFT | Tất cả cap, freshness, expiry, reservation và kill-switch values |
| OD-1.3-09 | Pre-submit `SERIALIZABLE`; fixed lock order; fill/reconcile `READ COMMITTED` + dedupe + CAS; lease/fencing | DATA-TXN-001 v0.2.1 approved; ADR-0012 wording conflict | ADR-0012 amendment và TTL/fencing numeric values |
| OD-1.3-10 | Chỉ mở entity có dictionary/ERD/ADR/task approval; chưa tạo DDL | DATA-DICT-001, DATA-ERD-001 đều DRAFT | Columns, constraints, indexes, roles, retention, migration plan |
| OD-1.3-11 | Chỉ implement C-CMD-002/C-EVT-002 sau registry approval; fake venue contract mới cần tạo | REG-001 IN_REVIEW; 14 schemas validate | Contract status, fixtures, version và conformance owner |
| OD-1.3-12 | `DEFERRED`; ledger activation vẫn gated bởi accounting annex | DOM-ACC-001 approved baseline nhưng annex chưa đủ | Account Owner/Risk Approver ghi nhận boundary |

Không có mục nào ở bảng này được đánh dấu `APPROVED` chỉ bằng cách đọc candidate baseline.

## 3. Approval record template

Mỗi decision đã chốt phải được ghi bằng format sau trong review record hoặc commit evidence:

```text
Decision ID: OD-1.3-XX
Decision value:
Scope/environment:
Rationale:
Affected artifacts:
Safety/rollback impact:
Approver name:
Approver role:
UTC timestamp:
Expiry or supersession:
Evidence path:
```

## 4. Readiness rule

Task 1.3 implementation chỉ có thể đề xuất `READY` khi:

1. Tất cả `OPEN` decision ảnh hưởng trực tiếp đến code đã chuyển sang `APPROVED` hoặc có `DEFERRED` rõ ràng ngoài scope.
2. Risk decisions có Risk Approver sign-off; Account Owner sign-off có mặt khi scope yêu cầu.
3. Artifact status trong DOCS_INDEX/registry được đồng bộ, không còn mâu thuẫn authority.
4. Task card implementation có allowlist/forbidden globs, exact commands, evidence path, expiry và reviewer.
5. Không có blocker database/integration nào bị che bằng mock hoặc skip không có waiver.

## 5. Current status

- Account Owner đã xác nhận baseline packet v0.1.0 lúc `2026-08-12T08:56:11Z`; approval record mới v0.3.0 lúc `2026-08-12T09:19:16Z` bao phủ P-01..P-68.
- Risk-sensitive và security/backup controls đã có dual-role record; các mục ADR/registry/dictionary vẫn cần đồng bộ authority vật lý.
- Task 1.3 implementation card đã tồn tại nhưng đang `BLOCKED`, chưa `READY`.
- Không được chuyển trạng thái bằng cách sửa riêng file này.

| Vai trò | Hành động tiếp theo | Trạng thái |
|---|---|---|
| Technical Operator | Chuẩn bị draft, cross-reference và evidence | IN_PROGRESS |
| Risk Approver | Quyết định OD-1.3-04, 07, 08, 09 và các mục risk liên quan | APPROVED — dual-role record `2026-08-12T09:19:16Z` |
| Security/Backup Owner | Review P-50..P-56, P-60 và các control security/backup/runbook liên quan | APPROVED — dual-role record `2026-08-12T09:19:16Z` |
| Account Owner | Đã phê duyệt packet v0.3.0 và candidate baseline | APPROVED `2026-08-12T09:19:16Z` |

## 6. Account Owner acknowledgement

| Trường | Giá trị |
|---|---|
| Actor | Account Owner — theo xác nhận trong phiên làm việc |
| UTC timestamp | 2026-08-12T08:33:58Z |
| Phạm vi xác nhận | Đồng ý tiếp tục xử lý candidate baseline của cả 12 decision theo thứ tự ưu tiên |
| Giới hạn | Không thay thế giá trị cụ thể, Risk Approver sign-off, contract approval, ADR approval, database evidence hoặc task card `READY` |
| Kết quả | Candidate baseline được Account Owner chấp nhận tại thời điểm acknowledgement; approval record v0.3.0 hiện là record hiệu lực cho P-01..P-68 |

## 7. Enterprise-control addendum approval status

Các decision P-49 đến P-68 được thêm vào packet sau approval record cũ và hiện được ghi nhận theo approval record v0.3.0:

| Nhóm | IDs | Trạng thái |
|---|---|---|
| Audit/correlation/access | P-49, P-50 | APPROVED — role record `2026-08-12T09:19:16Z` |
| Logging/metrics/runbook | P-51, P-52, P-53 | APPROVED — OPS numeric thresholds remain deferred |
| Database/migration/backup | P-54, P-55, P-56 | APPROVED design boundary; execution evidence required when DDL opens |
| Contract/architecture/test/fault | P-57, P-58, P-59 | APPROVED design/evidence plan; runtime evidence pending |
| Threat/rollback/deferred boundary | P-60, P-61, P-62 | APPROVED; later-phase items explicitly deferred |
| Fixture/dictionary/traceability/drill/hygiene | P-63, P-64, P-65, P-66, P-67, P-68 | APPROVED — role record `2026-08-12T09:19:16Z` |

**Current final state:** packet v0.3.0 và P-01..P-68 đã được approval record ghi nhận; ADR-0003 PostgreSQL 17 amendment đã được Account Owner phê duyệt `2026-08-12T11:15:53Z`; Supabase Local/PostgreSQL no-skip evidence đã pass. Task-scoped authority references và branch đã đồng bộ; card readiness vẫn cần Account Owner chuyển canonical card sang `READY`.
