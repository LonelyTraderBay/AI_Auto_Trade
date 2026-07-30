# Ma trận RACI và quyền quyết định

| Thuộc tính | Giá trị |
|---|---|
| Document ID | GOV-RACI-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §1.6, §11.3, §11.4, §14 và §15 |
| Related requirements | FR-OPS-001, NFR-AUD-001, NFR-SEC-001, SEC-AUTH-001, SEC-AUD-001 |
| Related ADR | ADR-0014, ADR-0015 (DRAFT/required by phase) |

> Ma trận này diễn giải trách nhiệm thành role. Nó không tự cấp quyền runtime, không thay thế permission matrix tại Master §11.3 và chưa có hiệu lực khi còn DRAFT hoặc IN_REVIEW.

## 1. Quy ước

| Ký hiệu | Nghĩa |
|---|---|
| R | Responsible: thực hiện/soạn/chạy công việc. |
| A | Accountable: chịu trách nhiệm cuối và bảo đảm quyết định được ghi nhận. Một hoạt động chỉ có một A. |
| C | Consulted: được tham vấn trước khi hoàn tất quyết định. |
| I | Informed: nhận thông tin hoặc evidence sau quyết định. |

Nếu một người giữ nhiều role ở Phase 0 đến paper/testnet, record phải nêu rõ role đang hành động. Điều đó không được dùng để tự phê duyệt thay đổi safety/security/live trước canary/live.

## 2. Danh mục role

| Role | Trách nhiệm chính | Không được làm |
|---|---|---|
| Account Owner | Sở hữu account/capital; phê duyệt scope, venue, legal/terms, canary cap và ADR/gate thuộc thẩm quyền. | Override regulatory constraint, immutable audit hoặc safety invariant. |
| Technical Operator | Thiết kế/triển khai, chạy CI, vận hành runtime, đề nghị reconciliation và kích hoạt kill switch. | Tự cấp approval risk/canary khi role độc lập là bắt buộc. |
| Risk Approver | Sở hữu risk policy, pending-risk approval, kill-switch release và canary risk cap. | Bypass risk evaluation hoặc audit. |
| Security/Backup Owner | Secrets, machine identity, topology, access, backup/restore và escalation. | Chia sẻ credential hoặc đặt trade key cho AI/UI. |
| Viewer | Đọc sanitized projection/audit trong quyền được cấp. | Gửi command nguy hiểm hoặc truy cập secret. |
| Worker | Machine identity với quyền tối thiểu cho một process. | Dùng shared human token hoặc vượt process scope. |
| AI Coding Agent | Sửa artifact/code đúng task, contract và allowed path. | Phê duyệt, deploy, dùng production credential hoặc tự mở rộng scope. |

## 3. RACI cho Phase 0.0 artifact pack

| Hoạt động / artifact | Technical Operator | Account Owner | Risk Approver | Security/Backup Owner | AI Coding Agent |
|---|---:|---:|---:|---:|---:|
| DOCS_INDEX, document control, glossary, product charter, FR/NFR | R | A | C | C | R trong task được cấp |
| RACI, RAID, traceability | R | A | C | C | R trong task được cấp |
| C4, runtime sequence, language/repository policy | R | A | C | C | R trong task được cấp |
| ADR-0001, 0002, 0003, 0004, 0005, 0014 | R | A | C theo tác động | C theo tác động | R trong task được cấp |
| ADR-0007, risk policy, OMS/risk review | R | A | R/C | C | R trong task được cấp |
| ADR-0011, accounting policy | R | A | R/C | I | R trong task được cấp |
| ADR-0012, concurrency/execution-leader policy | R | A | C | C | R trong task được cấp |
| Data architecture, ERD, dictionary, DB operations | R | A | C | C | R trong task được cấp |
| OpenAPI/schema/error catalog/fixtures | R | A | C | C | R trong task được cấp |
| Threat model, access matrix, auth-session, secrets, SLO/runbooks | R | A | C | R | R trong task được cấp |
| Task-card schema, task cards, CI binding design | R | A | C | C | R trong task được cấp |
| Phase 0.0 gate record | R | A | C | C | I |

R trong cột AI Coding Agent chỉ có nghĩa là agent có thể soạn file trong allowlist của task. Account Owner vẫn chịu trách nhiệm cuối; agent không có authority để chuyển artifact sang APPROVED.

## 4. RACI cho thay đổi sau baseline

| Hoạt động | R | A | C | I |
|---|---|---|---|---|
| Migration/schema | Technical Operator | Technical Operator | Context owner, Security/Backup Owner khi sensitive | Account Owner |
| Public HTTP/command/event/config contract | Technical Operator | Technical Operator | Consumer/context owner, Security/Backup Owner khi sensitive | Account Owner |
| Risk policy hoặc manual approval | Risk Approver | Risk Approver | Technical Operator | Account Owner |
| OMS/ledger semantic | Technical Operator | Account Owner | Risk Approver | Security/Backup Owner |
| Credential/topology/backup | Security/Backup Owner | Security/Backup Owner | Technical Operator | Account Owner, Risk Approver khi ảnh hưởng canary |
| Deployment manifest | Technical Operator | Technical Operator | Risk Approver, Security/Backup Owner | Account Owner |
| Kill switch activation | Technical Operator | Technical Operator | Risk Approver nếu scope/policy yêu cầu | Account Owner |
| Kill switch release | Risk Approver | Account Owner | Technical Operator | Security/Backup Owner |
| Canary approval | Risk Approver | Account Owner | Technical Operator, Security/Backup Owner | Viewer |
| Incident closure sau critical event | Technical Operator | Account Owner | Risk Approver, Security/Backup Owner | Affected roles |

## 5. Quyền runtime tối thiểu

RACI là governance; runtime authorization phải thực thi permission matrix của Master §11.3. Tóm tắt:

| Action | Role tối thiểu | Re-auth | Bằng chứng audit |
|---|---|---|---|
| Đọc health/projection | Viewer | Không | Theo access log policy |
| Request reconciliation | Technical Operator | Không | Actor, reason, correlation ID |
| Activate kill switch | Technical Operator | Actor xác thực | Actor, scope, reason, before/after hash |
| Release kill switch | Risk Approver + Account Owner | Có | Approval và reconciliation sạch |
| Approve pending risk intent | Risk Approver | Có | Fresh risk evaluation, actor, reason |
| Thay risk policy/deployment | Risk Approver + Account Owner theo scope | Có | Version/hash, approval, reason |
| Rotate credential/topology | Security/Backup Owner | Có | Rotation/audit verification |

Không có UI confirmation, shared token hoặc dashboard session nào tự thay cho authorization, re-auth và audit record.

## 6. Quy tắc xung đột và escalation

1. Nếu R/A/C không thống nhất về safety, security, data, execution hoặc live scope, task phải BLOCKED.
2. Technical Operator ghi mô tả, impact, requirement/ADR liên quan và đề xuất trong task/RAID record.
3. Account Owner quyết định scope hoặc yêu cầu ADR; Risk Approver/Security Owner có quyền chặn phần thuộc risk/security.
4. Chỉ acceptance record có actor/role/time/version mới đóng blocker.

## 7. Rà soát

RACI phải được rà soát khi thay đổi role owner, thêm venue/account, mở canary/live, thay auth provider hoặc đổi đường approval. Bất kỳ thay đổi nào làm suy yếu separation-of-duties trước canary/live cần ADR và Account Owner approval.

## 8. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | Tạo RACI baseline cho Phase 0.0 và các action trọng yếu. | Technical Operator | Pending |
