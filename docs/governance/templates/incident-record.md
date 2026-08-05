# Template — Incident Record / Post-mortem

| Thuộc tính | Giá trị |
|---|---|
| Document ID | GOV-TPL-INC-001 |
| Phiên bản | 0.1.1 |
| Trạng thái | DRAFT |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-08-02 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §12, §14 Phase 4, Phụ lục C.7; docs/backend/security-ops/slo-sli-alert-policy.md §4 (severity); docs/backend/security-ops/runbook-index.md |
| Related requirements | NFR-OPS-001, NFR-AUD-001, SEC-AUD-001 |
| Change summary | 0.1.1 (2026-08-02): bổ sung 4 trường header còn thiếu theo GOV-DOC-001 §3 (Ngày hiệu lực, Rà soát gần nhất, Related requirements, Change summary) và bảng Nhật ký thay đổi — audit toàn diện. |

> Copy template này thành `docs/governance/evidence/incidents/<YYYY-MM-DD>-<INC_ID>.md` khi có sự cố hoặc drill. Mọi runbook drill và sự cố thật (từ Phase 0 trở đi) phải sinh một record theo mẫu này — evidence dạng tự do không được chấp nhận cho gate. Không ghi secret, credential, payload thô chưa redaction.

---

## INC-<NNNN> — <tiêu đề ngắn>

### 1. Định danh

| Trường | Giá trị |
|---|---|
| Incident ID | INC-<NNNN> (tuần tự, không tái sử dụng) |
| Loại | INCIDENT / DRILL |
| Severity | SEV-1 / SEV-2 / SEV-3 (theo OPS-001 §4) |
| Trigger / phát hiện bởi | <alert/manual/drill schedule> |
| Runbook áp dụng | RB-<NNN> hoặc "không có — cần runbook mới" |
| Incident commander (role) | <role> |
| Environment / deployment manifest hash | <env + hash, hoặc N/A docs-only> |
| Bắt đầu (UTC) | <ISO-8601> |
| Safe state đạt lúc (UTC) | <ISO-8601> |
| Kết thúc (UTC) | <ISO-8601> |

### 2. Timeline (append-only, UTC)

| Thời điểm | Sự kiện / hành động | Actor (role) | Evidence path/hash |
|---|---|---|---|
| | | | |

### 3. Safe-state proof

Bằng chứng hệ thống đã về trạng thái an toàn trước khi xử lý tiếp (kill switch state, reconciliation kết quả, exposure = 0, lease state...). Liệt kê command/query đã chạy và kết quả.

### 4. Ảnh hưởng

- Phạm vi: <order/ledger/data/service bị ảnh hưởng, số lượng>
- Ảnh hưởng tài chính (nếu có): <số liệu từ ledger, không ước đoán>
- Ảnh hưởng dữ liệu/audit: <mất mát/chậm trễ/không>

### 5. Nguyên nhân gốc

Phân tích nguyên nhân (5-whys hoặc tương đương). Phân biệt nguyên nhân kỹ thuật, quy trình và con người. Không đổ lỗi cá nhân — mục tiêu là sửa hệ thống.

### 6. Hành động khắc phục

| # | Hành động | Loại (fix/prevent/detect) | Owner (role) | Task/ADR liên kết | Hạn | Trạng thái |
|---|---|---|---|---|---|---|
| | | | | | | |

### 7. Kết luận và phê duyệt

| Trường | Giá trị |
|---|---|
| Runbook có cần cập nhật? | Có/Không — link change |
| Bài học chính | <1-3 dòng> |
| Người review (role + identity) | |
| Thời điểm review (UTC) | |
| Trạng thái record | DRAFT / REVIEWED / CLOSED |

---

## Nhật ký thay đổi (của file template này — không copy vào incident record)

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.1 | 2026-08-02 | Bổ sung header chuẩn GOV-DOC-001 §3 (Ngày hiệu lực, Rà soát, Related requirements, Change summary) và bảng nhật ký này — audit toàn diện. | Technical Operator | Pending |
| 0.1.0 | 2026-07-31 | Khởi tạo template incident record / post-mortem. | Technical Operator | Pending |
