# Kiểm soát tài liệu và nguồn sự thật

| Thuộc tính | Giá trị |
|---|---|
| Document ID | GOV-DOC-001 |
| Phiên bản | 0.3.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực; chỉ có hiệu lực khi trạng thái APPROVED |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §1, §14.2, §15.4 và Phụ lục C |
| Related requirements | NFR-AUD-001, NFR-OPS-001, NFR-AI-001, SEC-AUD-001, SEC-AI-002, SEC-AI-003 |
| Related ADR | ADR-0014; ADR-0016 (DRAFT/required for Phase 6) |

> Tài liệu này quy định cách quản lý artifact của dự án. Nó không phê duyệt kiến trúc, risk policy, contract hoặc thay đổi runtime nào. Khi còn trạng thái DRAFT hoặc IN_REVIEW, tài liệu chỉ là đề xuất để review.

## 1. Mục đích và phạm vi

Mục đích là ngăn nguồn sự thật bị phân tán, giảm suy diễn khi triển khai và tạo bằng chứng có thể kiểm tra cho mỗi gate. Quy tắc áp dụng cho mọi tài liệu, ADR, contract, task card, gate record, evidence, cấu hình phát hành và artifact sinh ra bởi CI.

Tài liệu này không thay thế master specification. Nếu có mâu thuẫn, xử lý theo hierarchy tại Master §1.5 và ghi lại kết quả trong thay đổi hoặc ADR phù hợp.

## 2. Hierarchy nguồn sự thật

Thứ tự authority bắt buộc là:

1. Regulatory/legal constraint áp dụng.
2. Master specification và ADR ở trạng thái APPROVED, gồm safety invariant không thể waiver.
3. Explicit owner decision trong phạm vi (1) và (2) cho phép.
4. DDL, OpenAPI, JSON Schema, config schema và contract registry đã version hóa.
5. Task card/gate record đã được phê duyệt.
6. Code và generated artifact.
7. Fixture, log, report và evidence.

Artifact ở cấp thấp hơn không được diễn giải lại hoặc override artifact ở cấp cao hơn. Khi phát hiện mâu thuẫn, người phát hiện phải:

1. Dừng task liên quan và đánh dấu BLOCKED.
2. Ghi ID artifact, phiên bản, nội dung mâu thuẫn và phạm vi ảnh hưởng.
3. Đề xuất sửa artifact cấp cao hơn hoặc ADR; không sửa code để che mâu thuẫn.
4. Chỉ tiếp tục sau khi review/approval được ghi nhận theo RACI.

## 3. Metadata bắt buộc

Mỗi artifact được kiểm soát phải có header với tối thiểu các trường:

| Trường | Quy tắc |
|---|---|
| Document ID / tiêu đề | Ổn định trong toàn bộ vòng đời; tiêu đề mô tả phạm vi. |
| Version | Semantic version cho tài liệu/contract; revision immutable cho migration. |
| Status | DRAFT, IN_REVIEW, APPROVED, REJECTED hoặc SUPERSEDED theo loại artifact. |
| Owner | Role chịu trách nhiệm duy trì nội dung. |
| Approver | Role/actor được RACI chỉ định; dùng pending khi chưa phê duyệt. |
| Effective date | Chỉ ghi ngày khi artifact APPROVED. |
| Review date | UTC date của lần tự rà soát gần nhất. |
| References | Master section, FR/NFR/SEC, ADR, contract, task và gate evidence liên quan. |
| Change summary | Tóm tắt thay đổi có ý nghĩa của phiên bản hiện tại. |

Không ghi secret, token, credential, private account payload, dữ liệu PII không cần thiết hoặc log chưa redaction vào metadata/evidence.

## 4. Vòng đời và hiệu lực

| Trạng thái | Ý nghĩa | Có thể làm input implementation/gate? | Chuyển trạng thái bởi |
|---|---|---|---|
| DRAFT | Tác giả đang soạn; nội dung có thể thay đổi. | Không. | Owner |
| IN_REVIEW | Đã đủ để reviewer đánh giá; feedback còn mở. | Không. | Owner sau khi nêu reviewer/scope |
| APPROVED | Được role có thẩm quyền chấp nhận cho phạm vi/phiên bản ghi rõ. | Có, trong phạm vi hiệu lực. | Approver theo RACI |
| REJECTED | Không được dùng; giữ lịch sử và lý do. | Không. | Approver |
| SUPERSEDED | Được thay thế bởi artifact mới; giữ read-only kèm link thay thế. | Chỉ dùng để hiểu lịch sử. | Owner + approver theo scope |

Approval phải chỉ rõ actor, role, thời điểm UTC, phiên bản/hash, phạm vi, điều kiện hết hiệu lực và evidence path. Một câu trong chat, commit message hoặc lời xác nhận không có record không đủ làm approval.

## 5. Quy tắc version và thay đổi

| Loại thay đổi | Ví dụ | Hành động tối thiểu |
|---|---|---|
| Editorial | Sửa lỗi chính tả không đổi nghĩa. | Patch version; review thường. |
| Compatible | Thêm field optional có default; bổ sung hướng dẫn không đổi contract. | Minor version; compatibility evidence. |
| Breaking/domain/data | Đổi semantic field, state machine, DDL, public wire contract. | Major version hoặc artifact mới; ADR, migration/forward-fix và contract test. |
| Safety/security/live | Ảnh hưởng execution, credential, risk, ledger, authorization hoặc canary. | ADR, đúng approver role, evidence/gate mới; không tự waiver. |

Không sửa lịch sử approval để phản ánh quyết định mới. Tạo version mới hoặc artifact thay thế và liên kết hai chiều. Migration đã áp dụng, evidence đã ký và journal/audit append-only không được chỉnh sửa.

## 6. Đặt tên, lưu trữ và liên kết

| Artifact | Vị trí chuẩn | Quy ước |
|---|---|---|
| Governance (control/RACI/RAID/traceability/index/layer classification) | docs/governance/ | Tên kebab-case, Markdown, header bắt buộc. |
| Shared/cross-cutting (glossary, NFR áp dụng cả backend/frontend) | docs/shared/ | Tên kebab-case, Markdown, header bắt buộc. |
| Backend product/architecture/domain/data/engineering/security-ops | docs/backend/{product,architecture,domain,data,engineering,security-ops}/ | Tên kebab-case, Markdown, header bắt buộc. |
| Frontend (chưa có nội dung; khởi tạo khi Phase 5 bắt đầu) | docs/frontend/ | Tên kebab-case, Markdown, header bắt buộc. |
| ADR — registry/index | docs/governance/adr/ | README.md là registry; xem GOV-CLASS-001 cho lý do tách khỏi nội dung ADR. |
| ADR — nội dung quyết định | docs/backend/adr/ | ADR-NNNN-<slug>.md; số không tái sử dụng. |
| Contract | contracts/ (không di chuyển theo tái cấu trúc docs/); registry tại docs/backend/contracts/contract-registry.md | File versioned; canonical path ghi trong contract registry. |
| Task card authority | tasks/active hoặc tasks/completed | YAML validate bằng task-card schema; Markdown chỉ là readable render. |
| Gate/task evidence | docs/governance/evidence/gates hoặc docs/governance/evidence/tasks | Có hash/path, runner, UTC time và liên kết Task/Gate ID. |
| Generated artifact | generated/ hoặc đường dẫn task nêu rõ | Có banner/source link; không sửa tay. |

Vị trí chuẩn trên có hiệu lực kể từ v0.3.0 (tái cấu trúc theo lớp Backend/Frontend/Shared/Governance, xem `documentation-layer-classification.md` — GOV-CLASS-001). Cấu trúc cũ (`docs/00-governance` … `docs/06-security-ops`, `docs/adr`, `docs/templates`, `docs/evidence`) không còn là vị trí chuẩn; mọi tham chiếu cũ trong artifact khác phải được cập nhật khi phát hiện.

`docs/governance/DOCS_INDEX.md` là registry điều hướng của artifact pack và phải được cập nhật trước gate Phase 0.0. Registry không thay thế metadata trong từng artifact.

## 7. Kiểm soát review và phê duyệt

1. Owner tạo hoặc sửa artifact trong scope task card.
2. Owner tự kiểm header, link, requirement mapping, trạng thái và nội dung nhạy cảm.
3. Reviewer kiểm tính nhất quán với master, ADR, contract và RACI.
4. Approver xác nhận scope/phiên bản hoặc trả về review với lý do.
5. Owner ghi approval/evidence và cập nhật DOCS_INDEX, traceability, task/gate khi áp dụng.

Đối với thay đổi safety/security/live, người phê duyệt phải độc lập theo Master §1.6. Trong Phase 0 đến paper/testnet một người có thể thực hiện nhiều role, nhưng mỗi hành động role phải được ghi riêng; điều đó không thỏa điều kiện reviewer human thứ hai trước canary/live.

## 8. Kiểm tra bắt buộc trước Phase 0.0 gate

- [ ] Mọi path required tại Master §1.5 tồn tại và được DOCS_INDEX liệt kê.
- [ ] Mỗi artifact có ID, version, status, owner, approver và references.
- [ ] Requirement traceability liên kết ít nhất baseline FR/NFR/SEC đến ADR, contract, module/test dự kiến và gate.
- [ ] Artifact DRAFT/IN_REVIEW không được dùng để mở code gate.
- [ ] Tất cả ADR required bởi Master §15.1 ở trạng thái APPROVED trước Phase 0.
- [ ] Gate record có actor, thời gian UTC, evidence hash/path và decision rõ ràng.
- [ ] Không có secret hoặc dữ liệu nhạy cảm không cần thiết trong docs, fixture hoặc evidence.

## 9. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.3.0 | 2026-07-31 | Cập nhật bảng "Vị trí chuẩn" (§6) theo tái cấu trúc docs/ sang lớp Backend/Frontend/Shared/Governance (GOV-CLASS-001); không đổi quy tắc lifecycle/version/RACI nào khác. | Technical Operator | Pending |
| 0.2.0 | 2026-07-31 | Cập nhật register/control references cho hồ sơ DRAFT AI đa provider/BYOK; không phê duyệt runtime hay key. | Technical Operator | Pending |
| 0.1.0 | 2026-07-31 | Tạo baseline kiểm soát tài liệu cho Phase 0.0. | Technical Operator | Pending |
