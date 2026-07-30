# Template — Architecture Decision Record

| Thuộc tính | Giá trị |
|---|---|
| Document ID | TMP-ADR-001 |
| Artifact type | Reusable ADR template |
| Phiên bản | 0.1.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §1.5, §1.6, §15.1 và Phụ lục C.2 |
| Related requirements | Theo ADR được tạo |
| Related ADR | ADR-0014 (template/governance policy) |

> Copy template này thành docs/adr/ADR-NNNN-<slug>.md. Không giữ placeholder trong ADR gửi review. Chỉ ADR có status APPROVED mới là authority để mở gate hoặc implementation task.

---

# ADR-NNNN — <Tiêu đề quyết định ngắn, mệnh đề rõ>

| Thuộc tính | Giá trị |
|---|---|
| ADR ID | ADR-NNNN |
| Phiên bản | 0.1.0 |
| Status | DRAFT / IN_REVIEW / APPROVED / REJECTED / SUPERSEDED |
| Date | YYYY-MM-DD |
| Owner | <role/actor chịu trách nhiệm soạn và duy trì> |
| Approver | <role/actor có thẩm quyền; pending nếu chưa duyệt> |
| Effective date | Chỉ điền khi APPROVED |
| Decision deadline | <phase/gate/date> |
| Related FR/NFR/SEC | <ID list> |
| Related contracts | <canonical path/version hoặc TBD có blocker> |
| Related tasks/gates | <TASK/GATE ID hoặc TBD> |
| Supersedes / superseded by | <ADR ID hoặc none> |

## 1. Context và decision drivers

Mô tả vấn đề, phạm vi, trigger, business/safety/security/data/operations drivers và điều gì sẽ hỏng nếu không quyết định. Ghi assumptions/open decision rõ ràng; không che chúng trong prose.

## 2. Decision

Nêu normative decision bằng MUST/SHOULD/MAY khi phù hợp.

- Quyết định được chấp nhận:
- Quyết định không được phép / boundary:
- Phạm vi áp dụng:
- Ngày/điều kiện hiệu lực:

## 3. Alternatives considered

| Alternative | Ưu điểm | Nhược điểm / risk | Lý do chọn hoặc loại |
|---|---|---|---|
| <A> |  |  |  |
| <B> |  |  |  |

Không ghi “không có alternative” với quyết định architecture, data, risk, security, credential, execution hoặc live topology trừ khi có regulatory constraint được dẫn nguồn.

## 4. Consequences

| Area | Positive consequence | Cost / negative consequence | Control/evidence cần có |
|---|---|---|---|
| Architecture |  |  |  |
| Domain / data |  |  |  |
| Risk / safety |  |  |  |
| Security / privacy |  |  |  |
| Operations / observability |  |  |  |
| Delivery / dependency |  |  |  |

## 5. Contract, migration và rollout impact

- Contract/schema/API/event/config affected:
- Database/migration/backfill/retention impact:
- Runtime/deployment/credential impact:
- Compatibility/consumer impact:
- Required test, drill, CI or gate evidence:

Nếu không có impact, nêu lý do đã kiểm tra thay vì để trống.

## 6. Rollback hoặc forward-fix

Nêu safe rollback/forward-fix path, dữ liệu/evidence cần giữ, condition dừng rollout và actor có quyền thực hiện. Với immutable migration, ledger, audit hoặc external effect, mô tả forward-fix/reconciliation thay vì đề xuất sửa lịch sử.

## 7. Approval record

| Field | Value |
|---|---|
| Reviewer(s) | <role/actor> |
| Review date (UTC) | <timestamp> |
| Approver role/actor | <role/actor> |
| Decision | APPROVED / REJECTED / returned for review |
| Version/hash reviewed | <version/hash> |
| Scope/conditions/expiry | <text> |
| Evidence path | <path/URI> |

## 8. Change log

| Version | Date | Change | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | YYYY-MM-DD | Initial draft. | <owner> | Pending |
