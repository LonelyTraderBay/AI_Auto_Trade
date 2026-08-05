# Compliance & Data-Privacy Register

| Thuộc tính | Giá trị |
|---|---|
| Document ID | GOV-COMPL-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | DRAFT |
| Owner | Account Owner |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực; chỉ có hiệu lực khi trạng thái APPROVED |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §0.3 OD-007, §7.11–§7.12, §12.2; ADR-0013; docs/backend/data/data-architecture.md; docs/backend/security-ops/threat-model.md |
| Related requirements | SEC-DATA-001, NFR-AUD-001 |
| Related ADR | ADR-0013 (data lifecycle/retention — DRAFT) |
| Blocking input | **OD-007** — legal/compliance applicability và data-retention obligations, hạn trước Phase 2, Owner: Account Owner |

> Register này gom về một chỗ ánh xạ *loại dữ liệu → phân loại → retention → nghĩa vụ pháp lý* hiện đang nằm rải rác trong data-architecture, threat-model, NFR và ADR-0013. Nó là **khung chờ sẵn** để nhận kết quả đánh giá OD-007; các ô "Nghĩa vụ pháp lý" giữ `PENDING OD-007` cho đến khi Account Owner ghi nhận đánh giá. Register không tự tạo nghĩa vụ mới và không thay thế các tài liệu nguồn.

## 1. Ánh xạ dữ liệu (baseline từ tài liệu hiện có)

| Loại dữ liệu | Phân loại | Retention (nguồn: ADR-0013/data-architecture) | Nghĩa vụ pháp lý | Ghi chú |
|---|---|---|---|---|
| Order/fill/ledger/audit history | Financial, append-only | Không hard-delete; retention theo ADR-0013 | PENDING OD-007 | Nền tảng audit/tax |
| Market data (bronze/silver/gold) | Internal | Partition/retention theo data policy | PENDING OD-007 | Không chứa PII |
| Venue credential/secret reference | Secret | Không lưu giá trị, chỉ reference; rotation theo runbook | PENDING OD-007 | SEC-CRED-001 |
| Account/balance snapshot từ venue | Sensitive financial | Theo reconciliation/audit policy | PENDING OD-007 | Redaction khi ra log/evidence |
| AI BYOK connection metadata | Sensitive config | Theo ADR-0016; không raw key | PENDING OD-007 | Phase 6 |
| AI prompt/response | Restricted egress | RAW_PROMPT_RESPONSE_DISABLED (C-CFG-006) | PENDING OD-007 | Không lưu raw theo contract |
| Log/telemetry vận hành | Internal, redacted | Theo operations policy | PENDING OD-007 | Không secret/PII trong log |
| Backup (PostgreSQL/WAL/Parquet) | Theo dữ liệu gốc | Consistency set + cadence theo RB-008 | PENDING OD-007 | Encrypt theo secrets policy |
| Tài liệu governance/evidence | Internal | Append-only cho evidence đã ký | PENDING OD-007 | Immutable evidence rule |

## 2. Quy trình cập nhật

1. Khi OD-007 được RESOLVED: Account Owner ghi kết quả đánh giá (jurisdiction, nghĩa vụ thuế/lưu trữ, thời hạn bắt buộc) kèm evidence path; điền cột "Nghĩa vụ pháp lý" từng dòng.
2. Mỗi loại dữ liệu mới (feature mới, contract mới) phải thêm dòng vào register **trong cùng change** tạo ra nó — reviewer kiểm tra khi review contract/ERD.
3. Mâu thuẫn giữa register và ADR-0013/data-architecture xử lý theo hierarchy §1.5 — register là view tổng hợp, không phải authority gốc.
4. Register này là điều kiện review của Phase 2 gate (master §14: OD-007 resolved trước Phase 2).

## 3. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.1 | 2026-08-02 | Làm rõ attribution: Technical Operator là role soạn thảo khung register; Account Owner là owner nội dung/nghĩa vụ (header). Không đổi nội dung mapping. | Technical Operator (soạn thảo; owner tài liệu: Account Owner) | Pending |
| 0.1.0 | 2026-07-31 | Khởi tạo khung register với baseline mapping từ tài liệu hiện có; mọi nghĩa vụ pháp lý PENDING OD-007. | Technical Operator (soạn thảo; owner tài liệu: Account Owner) | Pending |
