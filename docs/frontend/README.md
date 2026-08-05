# docs/frontend/ — Bộ tài liệu Frontend (Flutter dashboard)

| Thuộc tính | Giá trị |
|---|---|
| Document ID | FE-INDEX-001 |
| Phiên bản | 0.2.1 |
| Trạng thái | DRAFT |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-08-02 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §11.5, §14 Phase 5/6; docs/governance/DOCS_INDEX.md; contracts/api/openapi.yaml |
| Phase hiệu lực | Phase 5 (dashboard core), Phase 6 (BYOK screens) |
| Change summary | 0.2.1 (2026-08-02): bổ sung Ngày hiệu lực + Tham chiếu chuẩn theo GOV-DOC-001 §3 (audit toàn diện); nội dung chỉ mục không đổi. |

> **Bộ tài liệu này là input thiết kế cho Phase 5/6 — không cho phép bắt đầu code frontend** trước khi gate các phase trước PASS và task card Phase 5 chuyển READY (master §14, §2.3). Mọi nội dung được trích xuất/neo trực tiếp vào contract backend (`contracts/api/openapi.yaml` là canonical duy nhất cho HTTP); khi mâu thuẫn, backend contract thắng. Mọi lựa chọn công nghệ trong pack đánh dấu DRAFT chờ Account Owner phê duyệt.

## Thứ tự đọc

1. **[product/frontend-charter.md](product/frontend-charter.md)** (FE-CHARTER-001) — dashboard là gì/không là gì, 5 role và capability gating, FR-FE-001..007, phase gating.
2. **[product/screen-inventory.md](product/screen-inventory.md)** (FE-SCREEN-001) — kiến trúc thông tin + từng màn hình map chính xác vào route API, kèm **GAP register** các route OpenAPI còn thiếu phải bổ sung trước Phase 5.
3. **[architecture/api-integration-contract.md](architecture/api-integration-contract.md)** (FE-API-001) — hợp đồng tích hợp bắt buộc: wire types, async command 202+polling, idempotency, If-Match, re-auth, bảng 26 error code → hành vi UI.
4. **[architecture/flutter-app-architecture.md](architecture/flutter-app-architecture.md)** (FE-ARC-001) — thin client, layer structure, state management, generated API client, session placeholder (ADR-0015).
5. **[design/design-system.md](design/design-system.md)** (FE-DS-001) — semantic color cho 16 OMS states/severity/safe_state, quy tắc hiển thị Decimal/timestamp, terminology theo glossary.
6. **[security/frontend-security-policy.md](security/frontend-security-policy.md)** (FE-SEC-001) — không secret ở client, session/CSRF, dangerous-action UX, BYOK UI rules, threat mapping.
7. **[engineering/frontend-testing-strategy.md](engineering/frontend-testing-strategy.md)** (FE-TEST-001) — test pyramid, contract test với OpenAPI, error-path coverage, authorization/re-auth tests (evidence gate Phase 5).

## Ràng buộc bất biến (từ backend, không thương lượng)

- Flutter **chỉ là client của Control API** (master §11.5) — không business/risk/execution logic, không secret, không gọi venue/DB trực tiếp.
- Authorization **luôn** đánh giá server-side; "a dashboard/client claim never grants access by itself" (SEC-002 §1).
- Mất kết nối dashboard không được ảnh hưởng trading node; dữ liệu cũ phải có nhãn stale, không che giấu trạng thái xấu.
- BYOK: key chỉ nhập một lần qua enrollment UI write-only, không read-back, không lưu, mất response → đọc status, không resubmit.

## Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.2.0 | 2026-07-31 | Thay placeholder rỗng bằng chỉ mục bộ tài liệu frontend 7 artifact (FE-CHARTER/SCREEN/API/ARC/DS/SEC/TEST-001), soạn từ audit trích xuất contract backend. | Technical Operator | Pending |
| 0.1.0 | 2026-07-31 | Placeholder có chủ đích — thư mục rỗng chờ Phase 5. | Technical Operator | Pending |
