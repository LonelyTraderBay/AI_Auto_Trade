# Waiver Register — sổ đăng ký waiver chính thức

| Thuộc tính | Giá trị |
|---|---|
| Document ID | GOV-WAIVER-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | DRAFT |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực; chỉ có hiệu lực khi trạng thái APPROVED |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §13.7, §15.3; docs/governance/document-control.md §5 |
| Related requirements | NFR-OPS-001, SEC-AUD-001 |
| Related ADR | Không có; CI enforcement thuộc thiết kế ENG-CI-001 (Task 0.2) |

> Đây là **vị trí chuẩn duy nhất** cho mọi waiver của dự án. Master §13.7/§15.3 quy định waiver phải có ID, phạm vi, compensating control, approver và expiry, và CI phải fail khi waiver hết hạn — nhưng trước tài liệu này chưa có nơi lưu chuẩn để CI kiểm tra. Mọi tham chiếu `waiver_id` trong task card, test skip/xfail reason hoặc gate record phải trỏ về một dòng trong register này.

## 1. Quy tắc bắt buộc

1. **Safety invariant không bao giờ được waiver** (master §6.3, §15.3): duplicate-order, risk bypass, ledger imbalance, credential rule, audit append-only. Một yêu cầu waiver đụng các mục này bị từ chối ngay, không đưa vào register.
2. Waiver ID theo định dạng `WAIVER-NNNN` (khớp pattern trong `contracts/config/task-card.v1.schema.json`), cấp tuần tự, không tái sử dụng.
3. Mỗi waiver phải có đủ: phạm vi chính xác (file/test/rule), lý do, compensating control, approver đúng RACI, ngày cấp và **expiry bắt buộc** (UTC). Không có waiver vô thời hạn.
4. Waiver hết hạn = vi phạm đang mở: CI (từ Task 0.2) phải fail; trước đó, validator thủ công của gate phải kiểm register này.
5. Gia hạn waiver là một dòng mới (ID mới hoặc bản ghi supersede), không sửa dòng cũ.

## 2. Register

| Waiver ID | Phạm vi (file/rule/test) | Lý do | Compensating control | Approver (role) | Cấp (UTC) | Expiry (UTC) | Trạng thái |
|---|---|---|---|---|---|---|---|
| — | *Chưa có waiver nào được cấp.* | — | — | — | — | — | — |

## 3. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | Khởi tạo waiver register rỗng làm vị trí chuẩn cho §13.7/§15.3; chưa cấp waiver nào. | Technical Operator | Pending |
