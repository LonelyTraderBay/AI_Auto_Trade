# ENG-VER-001 — Versioning và release policy

| Thuộc tính | Giá trị |
|---|---|
| Document ID | ENG-VER-001 |
| Phiên bản | 0.1.1 |
| Trạng thái | DRAFT |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực; chỉ có hiệu lực khi trạng thái APPROVED |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §1.3, §6.6, §13.2, §13.7; docs/backend/engineering/ci-cd-design.md §2/§6; docs/governance/document-control.md §5 |
| Related requirements | NFR-OPS-001, NFR-DET-001 |
| Related ADR | ADR-0010 (deployment), ADR-0014 (toolchain) |

> Tài liệu này lấp khoảng trống giữa *document versioning* (document-control §5), *contract versioning* (contract registry) và *release evidence* (ENG-CI-001): nó định nghĩa cách **bản thân application** được đánh version và release. Đây là policy DRAFT; giá trị cụ thể có thể được Account Owner điều chỉnh khi review.

## 1. Application version — SemVer

- Application dùng **Semantic Versioning** `MAJOR.MINOR.PATCH`, khai báo một nơi duy nhất trong `pyproject.toml` (`project.version`).
- Trước canary đầu tiên, version giữ `0.y.z`: MINOR cho mỗi phase gate pass, PATCH cho fix trong phase. `1.0.0` chỉ được đặt khi Phase 4 canary gate PASS.
- MAJOR tăng khi có breaking change ở public contract (OpenAPI/schema major mới) hoặc thay đổi kiến trúc qua ADR supersession.
- Version application **độc lập** với version của master spec, tài liệu và contract — mỗi loại theo quy tắc riêng của nó; deployment manifest là nơi ghim tổ hợp cụ thể (§6.6).

## 2. Tag và release identity

- Release tag dạng `v<MAJOR>.<MINOR>.<PATCH>` trên commit đã qua CI xanh ở `main`; tag là immutable — không di chuyển, không xóa; sai thì tạo tag mới.
- Định danh triển khai thực tế **không phải tag** mà là **immutable deployment manifest** (§6.6): commit + image digest + dependency lock checksum + config hash + approval. Tag chỉ là mốc đọc-cho-người.
- Mọi release artifact phải có evidence theo ENG-CI-001 §6 (SHA, SBOM, digest) gắn với manifest.

## 3. Release note / CHANGELOG

- Không duy trì CHANGELOG viết tay. Release note sinh từ lịch sử **Conventional Commits** (đã bắt buộc theo §13.2/CONTRIBUTING.md) tại thời điểm gắn tag, nhóm theo type (`feat`/`fix`/`refactor`/...), kèm Task ID.
- Generated release note đặt tại `generated/release-notes/` (theo quy tắc generated artifact — có banner, không sửa tay) hoặc đính vào tag annotation.

## 4. Cadence và điều kiện release

- Không có cadence cố định trong giai đoạn pre-live; release theo phase gate và task card DONE.
- Một release chỉ hợp lệ khi: CI profile hiện hành xanh, không waiver hết hạn trong [waiver register](../../governance/waiver-register.md), gate record phase tương ứng còn hiệu lực, và diff nằm trong các task card đã DONE.
- Rollback tuân theo §6.6 (`rollback_target_manifest_id`) và RB-008; không rollback bằng cách sửa tag hay force-push.

## 5. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.1 | 2026-07-31 | Đổi title ID ENG-006 -> ENG-VER-001 khớp Document ID và DOCS_INDEX; nội dung không đổi. | Technical Operator | Pending |
| 0.1.0 | 2026-07-31 | Khởi tạo policy SemVer/tag/release-note/cadence cho application, tách khỏi document/contract versioning. | Technical Operator | Pending |
