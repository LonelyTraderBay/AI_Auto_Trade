# ADR-0012 — Amendment proposal for Task 1.3

| Trường | Giá trị |
|---|---|
| Document ID | ADR-0012-AMENDMENT-PROPOSAL-T1.3 |
| Phiên bản | 0.2.0 |
| Trạng thái | SUPERSEDED — applied to ADR-0012 v0.3.0 |
| Parent | [One-time approval packet](ONE-TIME-APPROVAL-PACKET.md) |
| Required approver | Account Owner; Risk Approver khi ảnh hưởng risk boundary |

> Proposal này được giữ lại để truy vết. Nội dung đã được áp dụng vào `docs/backend/adr/0012-transaction-concurrency.md` v0.3.0 theo approval record `2026-08-12T09:19:16Z`.

## 1. Vấn đề cần sửa

ADR-0012 đang có trạng thái `APPROVED`, nhưng phần decision vẫn chứa câu `If approved` và mô tả isolation cho fill/reconciliation là `DRAFT`. Nội dung này mâu thuẫn với `DATA-TXN-001 v0.2.1`, đã được Account Owner phê duyệt cho local simulator/Phase 1.

## 2. Nội dung amendment đề xuất

Thay đoạn decision tương ứng bằng:

> `TradingSubmissionUnitOfWork` dùng `SERIALIZABLE`, bao phủ risk decision/reservation, execution order/submission attempt và platform outbox; lock order cố định là risk limit/reservation → execution order → platform outbox. Không gọi venue/network trong unit of work. Serialization/deadlock retry chỉ bounded trước external action và phải chạy lại toàn bộ validation/risk/CAS. External submit không bao giờ blind-retry.
>
> `FillLedgerUnitOfWork` và `ReconciliationResolutionUnitOfWork` dùng baseline `READ COMMITTED` + unique-constraint dedupe + compare-and-swap trên aggregate version. Fill dedupe dùng `(order_id, sequence)` cho ordering và venue fill ID hoặc source fingerprint cho identity; journal dedupe dùng `source_event_id`. Các fact append-only immutable. Unknown external outcome chuyển recovery/reconciliation, không tạo submit attempt mới tự động.
>
> Execution leader dùng lease TTL và monotonic fencing token; mất lease dừng claim/submit mới. Numeric TTL/heartbeat phải được ghi trong approved task card hoặc policy profile, không suy đoán trong code.`

## 3. Không thay đổi

- Không giữ DB transaction trong lúc gọi venue.
- Không retry external submission khi outcome `UNKNOWN`.
- Không dùng fencing để giả định venue API đã atomic.
- Không mở external venue, ledger runtime hoặc live scope.

## 4. Approval record đã ghi nhận

```text
ADR: ADR-0012
Amendment: Task 1.3 concurrency clarification
Decision: APPROVE
Approver: User confirmation in approval record
Role: Account Owner + Risk Approver (dual-role pre-canary)
Rationale: Resolve `If approved`/DRAFT contradiction and pin Task 1.3 concurrency boundary.
UTC timestamp: 2026-08-12T09:19:16Z
Supersedes: Proposal status only; ADR-0012 v0.3.0 is authority.
Evidence: `docs/governance/evidence/tasks/1.3/approval-record-2026-08-12.md`
```

## 5. Readiness impact

ADR-0012 wording blocker is closed. Task 1.3 remains `BLOCKED` for PostgreSQL no-skip, branch and remaining authority synchronization.
