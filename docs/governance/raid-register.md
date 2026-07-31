# RAID Register — rủi ro, giả định, issue và dependency

| Thuộc tính | Giá trị |
|---|---|
| Document ID | GOV-RAID-001 |
| Phiên bản | 0.2.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §0.3, §1.5, §12, §14, §15 |
| Related requirements | NFR-SAFE-001, NFR-OPS-001, NFR-SEC-001, NFR-AI-001, SEC-CRED-001, SEC-AUTH-001, SEC-AI-002, SEC-AI-003 |
| Related ADR | ADR-0001 đến ADR-0016 theo deadline trong Master §15.1 |

> RAID register là log vận hành của rủi ro và blocker, không phải nơi phê duyệt exception. Chỉ ADR/owner decision/gate record hợp lệ mới có thể đóng mục hoặc thay đổi phase.

## 1. Quy ước trạng thái và mức độ

| Field | Giá trị dùng |
|---|---|
| Status | OPEN, MITIGATING, BLOCKED, ACCEPTED, RESOLVED, SUPERSEDED |
| Impact | Critical, High, Medium, Low |
| Likelihood | High, Medium, Low |
| Owner | Role chịu trách nhiệm cập nhật/điều phối, không mặc nhiên là approver. |
| Evidence | Path/URI + hash hoặc record approval khi đóng mục. |

Không được chuyển mục sang RESOLVED chỉ vì có kế hoạch. Cần evidence kiểm chứng hoặc quyết định ghi rõ phạm vi.

## 2. Risks

| ID | Rủi ro | Impact / Likelihood | Trigger | Mitigation / contingency | Owner | Status | Liên kết |
|---|---|---|---|---|---|---|---|
| R-001 | Code hoặc schema bắt đầu trước khi ADR/contract/traceability Phase 0.0 hoàn tất. | Critical / Medium | Task không có card hoặc artifact required chưa APPROVED. | Block task; hoàn tất artifact pack, ADR và gate record trước Phase 0. | Technical Operator | OPEN | Master §14.2, §14 Phase 0.0 |
| R-002 | AI hoặc contributor suy diễn requirement/contract chưa tồn tại. | High / High | Thay đổi ngoài allowed path, thiếu requirement/ADR/schema. | Task YAML allowlist, review, contract-first, báo BLOCKED. | Technical Operator | OPEN | Master §16; GOV-TRACE-001 |
| R-003 | Duplicate order hoặc exposure không rõ sau timeout/disconnect. | Critical / Medium | Submission outcome unknown, mất lease, venue gap. | ClientOrderId duy nhất, durable queue, không blind retry, reconciliation. | Technical Operator | OPEN | FR-EXEC-001, FR-REC-001, ADR-0005/0012 |
| R-004 | Risk bypass, stale snapshot hoặc reservation không nhất quán. | Critical / Medium | Missing/stale health/reference/portfolio state; concurrent intent. | Fail closed, fresh risk check, reservation, concurrency policy và state-machine/property test. | Risk Approver | OPEN | FR-RSK-001, NFR-SAFE-001, ADR-0007/0012 |
| R-005 | Ledger/audit không thể rebuild hoặc không cân bằng. | Critical / Low | Duplicate fill, mutable posting, adjustment không evidence. | Append-only journal/posting, deferred balance enforcement, property/rebuild test. | Risk Approver | OPEN | FR-LED-001, NFR-AUD-001, ADR-0011 |
| R-006 | Venue/account/instrument hoặc pháp lý chưa được chốt trước external integration. | High / High | OD-001/002/003 còn OPEN. | Không kết nối venue/testnet scope; giữ Phase 3 BLOCKED. | Account Owner | OPEN | Master §0.3, ADR-0009 |
| R-007 | Credential leak hoặc authorization không đủ trước external venue. | Critical / Medium | Secret in repo/log, shared identity, auth provider chưa chốt. | Separate key/environment, secret policy, ADR-0015, least privilege, scan/review. | Security/Backup Owner | OPEN | SEC-CRED-001, SEC-AUTH-001, OD-006 |
| R-008 | Data retention/licensing/backup obligation chưa rõ. | High / Medium | OD-007 chưa RESOLVED trước Phase 2. | Legal assessment, retention matrix, restore responsibility; block data catalog release if unresolved. | Account Owner | OPEN | Master §0.3, §15.2, ADR-0013 |
| R-009 | Scope creep sang multi-venue, derivatives, microservice hoặc AI execution. | High / Medium | Dependency/language/runtime mới không có ADR. | Enforce MVP boundary and dependency review; create ADR before expansion. | Account Owner | OPEN | Product Charter; ADR-0001/0008 |
| R-010 | Một actor vừa xây, vừa review, vừa phê duyệt canary/live safety change. | Critical / Medium | Không có reviewer human độc lập trước canary/live. | Record separate roles in earlier phases; require independent human reviewer before canary/live. | Account Owner | OPEN | GOV-RACI-001; Master §1.6 |
| R-011 | BYOK key/egress/provider boundary làm lộ credential, dữ liệu hoặc tạo billing abuse/cross-owner use. | High / Medium | User nhập key/URL/policy tùy ý, enrollment bị log/hash, DNS/redirect bypass, candidate rotation/revoke xử lý sai hoặc fallback bị suy diễn. | Provider/policy profile catalog + isolated no-store enrollment + owner-scope RBAC/dual approval + egress gateway + binding lease/budget/no-fallback policy; ADR-0016/RB-009; block Phase 6 while OD-008 OPEN. | Security/Backup Owner | OPEN | SEC-AI-POL-001; ADR-0016; Master §10.6 |

## 3. Assumptions cần được xác nhận

| ID | Giả định | Rationale / boundary | Validation deadline | Owner | Status |
|---|---|---|---|---|---|
| A-001 | MVP chỉ hỗ trợ một venue crypto spot, một account và instrument đã được owner phê duyệt. | Giảm scope và phù hợp modular monolith. | Trước Phase 3; OD-001/003 | Account Owner | OPEN |
| A-002 | Không có live trade credential, database schema, application code hoặc endpoint trong Phase 0.0. | Documentation closure phải hoàn tất trước code. | Phase 0.0 gate | Technical Operator | OPEN |
| A-003 | Python 3.12.x là ngôn ngữ runtime duy nhất cho MVP; PostgreSQL 16.x là OLTP system of record. | Quyết định chuẩn nhưng cần ADR-0014/0003 APPROVED. | Phase 0.0 gate | Account Owner | OPEN |
| A-004 | Risk, OMS, ledger và canonical domain vẫn thuộc hệ thống này; NautilusTrader không là dependency Phase 0–4. | Tránh framework chiếm domain ownership. | Phase 0.0 gate / ADR-0006 later | Technical Operator | OPEN |
| A-005 | Paper/testnet/shadow phải chứng minh safety trước canary; PnL không là success criterion đầu tiên. | Ưu tiên determinism, audit và recovery. | Mọi gate trước canary | Risk Approver | OPEN |
| A-006 | AI worker, nếu có ở Phase 6, proposal-only và không có execution/trade credential. | Safety invariant. | Trước Phase 6 | Security/Backup Owner | OPEN |
| A-007 | MVP AI BYOK owner scope là Account Owner/account environment; multi-user/tenant sharing không được suy diễn. | Giữ boundary rõ trước khi có tenant/auth design riêng. | Trước Phase 6 | Account Owner | OPEN |

## 4. Issues đã biết

| ID | Issue | Impact | Hành động kế tiếp | Owner | Status | Evidence cần có |
|---|---|---|---|---|---|---|
| I-001 | Current phase là Phase 0.0 `IN_REVIEW`; artifact pack chưa thể được coi là APPROVED. | Phase 0 bị chặn. | Review và phê duyệt toàn bộ artifact required; ghi gate record. | Technical Operator | OPEN | DOCS_INDEX + Phase 0.0 gate record |
| I-002 | ADR required by Phase 0.0 chưa có trạng thái APPROVED trong master hiện tại. | Phase 0 bị chặn. | Soạn/review/approve ADR-0001–0005, 0007, 0011, 0012, 0014. | Account Owner | OPEN | ADR files + approval evidence |
| I-003 | Venue, jurisdiction, account/instrument, auth provider, retention obligation chưa có quyết định cuối. | Phase 2/3/4 bị chặn theo từng item. | Duy trì Open Decision Register và không triển khai phase bị chặn. | Account Owner | OPEN | OD evidence theo Master §0.3 |
| I-004 | AI BYOK provider catalog, secret ingress, owner scope, data-egress/budget/fallback policy chưa được phê duyệt. | Phase 6 bị chặn. | Review/approve ADR-0016, resolve OD-008 và hoàn tất catalog/security/runbook evidence. | Account Owner + Security/Backup Owner | OPEN | ADR-0016, ARC-AI-001, SEC-AI-POL-001 |

## 5. Dependencies

| ID | Dependency | Cần cho | Owner | Deadline | Status |
|---|---|---|---|---|---|
| D-001 | DOCS_INDEX và toàn bộ artifact path tại Master §1.5. | Phase 0.0 gate. | Technical Operator | Trước Phase 0.0 gate | OPEN |
| D-002 | ADR-0001–0005, 0007, 0011, 0012, 0014 APPROVED. | Bắt đầu Phase 0. | Account Owner | Trước Phase 0 | OPEN |
| D-003 | Task-card schema, task 0.0.x cards và CI binding design. | Controlled implementation from Task 0.1. | Technical Operator | Trước Phase 0.0 gate | OPEN |
| D-004 | Data lifecycle/legal/backup decision. | Phase 2 data catalog. | Account Owner + Security/Backup Owner | Trước Phase 2 | OPEN |
| D-005 | Venue capability, jurisdiction, account/instrument và authentication decision. | Phase 3 external venue. | Account Owner | Trước Phase 3 | OPEN |
| D-006 | Canary topology, capital cap, risk hard limits, independent reviewer. | Phase 4 canary. | Account Owner + Risk Approver + Security/Backup Owner | Trước Phase 4 | OPEN |
| D-007 | Provider catalog/capability, secret provider topology, BYOK owner scope/egress/budget/fallback policy và AI machine identity. | Phase 6 AI/BYOK. | Account Owner + Security/Backup Owner | Trước Phase 6 | OPEN |

## 6. Cadence và escalation

- Review RAID ít nhất khi bắt đầu/kết thúc mỗi task, trước phase gate, sau security/critical incident và khi Open Decision Register thay đổi.
- Critical hoặc High risk ảnh hưởng safety/security/execution phải được thông báo cho Account Owner, Risk Approver hoặc Security/Backup Owner đúng phạm vi trước khi tiếp tục.
- Mọi risk accepted cần ADR hoặc explicit owner decision trong phạm vi Master §1.5 cho phép; safety invariant không được accept bằng waiver.
- Lịch sử mục RESOLVED/SUPERSEDED được giữ kèm evidence path và không xóa.

## 7. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | Tạo RAID baseline từ blocker và gate của master. | Technical Operator | Pending |
| 0.2.0 | 2026-07-31 | Thêm BYOK đa provider risk, assumption, issue và dependency trước Phase 6. | Technical Operator | Pending |
