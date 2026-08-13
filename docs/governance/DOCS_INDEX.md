# DOCS_INDEX — AI Auto Trade Phase 0.0

| Thuộc tính | Giá trị |
|---|---|
| Document ID | GOV-INDEX-001 |
| Phiên bản | 0.14.23 |
| Trạng thái | IN_REVIEW (0.9.0 APPROVED 2026-08-06; 0.10.0 revalidated by Account Owner 2026-08-10T20:07:02Z; remaining artifact rows retain their own status) |
| Owner | Technical Operator |
| Approver | Account Owner |
| Ngày tạo | 2026-07-31 |
| Ngày hiệu lực | 2026-08-06 |
| Rà soát gần nhất | 2026-08-13 |
| Master authority | [AI_AUTO_TRADE_MASTER_SPEC.md](../../AI_AUTO_TRADE_MASTER_SPEC.md) v2.4.1 |
| Change summary | 0.14.23 (2026-08-13): hoàn tất implementation/evidence Task 1.3 durable submit/fake venue; Docker/Supabase/PostgreSQL no-skip self-check đạt PASS=23, INFO=2, BLOCKED=0, FAIL=0; card chuyển sang `REVIEW`, chờ Account Owner nghiệm thu DONE. 0.14.22 (2026-08-13): hoàn tất redaction đúng scope Task 1.3.1, ghi nhận before/after hash, secret scan và quality evidence; card ở `REVIEW`, chờ Account Owner nghiệm thu DONE. 0.14.21 (2026-08-13): ghi nhận Security/Backup Owner role action riêng cho Task 1.3.1, chuyển cleanup card sang `READY` trên branch riêng; target redaction chưa chạy. 0.14.20 (2026-08-13): ghi nhận Account Owner approval cho Task 1.3.1 evidence redaction cleanup; tạo canonical cleanup card ở `BLOCKED`, giữ target file nguyên trạng và ghi nhận blocker Security/Backup Owner role action/branch sạch. 0.14.19 (2026-08-12): ghi nhận Account Owner approval ADR-0003 PostgreSQL 17, đồng bộ authority và cài Supabase Local `AI_Auto_Trade`; migration/concurrency database evidence no-skip đã pass; canonical Task 1.3 card vẫn `BLOCKED` chờ transition `READY`. 0.14.18: ghi nhận one-time approval record, reconcile card 0.0.7 sang `tasks/completed/`, tạo canonical Task 1.3 card ở `BLOCKED` và đồng bộ control panel. |

## Mục đích và trạng thái

Đây là chỉ mục chính thức của artifact pack Phase 0.0. Các tài liệu trong pack đã được tạo để review; **không tài liệu nào trong trạng thái `DRAFT` hoặc `IN_REVIEW` được phép mở Phase 0 hay cho phép code application, migration, endpoint hoặc venue integration**.

Khi có mâu thuẫn, áp dụng hierarchy ở §1.5 của master. Physical schema, wire contract và runtime config chỉ trở thành authority thực thi sau khi artifact tương ứng được review/approved theo master.

Kể từ v0.3.0, cây thư mục `docs/` được tổ chức theo lớp **Backend / Frontend / Shared / Governance** — xem `governance/documentation-layer-classification.md` (GOV-CLASS-001) để biết lý do phân loại từng artifact. Không artifact nào bị đổi status/nội dung bởi lần tái cấu trúc này; chỉ vị trí file thay đổi.

## Trình tự review bắt buộc

1. Governance, scope, requirements và RACI.
2. ADR 0001–0005, 0007, 0011, 0012, 0014 và các ADR theo phase (gồm 0016 trước Phase 6).
3. Architecture/domain/data policy và data dictionary cho Task 0.3.
4. Contract registry, OpenAPI, JSON Schema và task-card control.
5. Engineering/CI/security/operations policy.
6. Task 0.1 card, validation record và gate record Phase 0.0.

## Document register

### Governance — `docs/governance/`

| ID | Artifact | Status |
|---|---|---|
| GOV-DOC-001 | [Document control](document-control.md) | IN_REVIEW |
| GOV-RACI-001 | [RACI](raci.md) | IN_REVIEW |
| GOV-RAID-001 | [RAID register](raid-register.md) | IN_REVIEW |
| GOV-TRACE-001 | [Requirements traceability](requirements-traceability.md) | IN_REVIEW |
| GOV-CLASS-001 | [Documentation layer classification (Backend/Frontend/Shared/Governance)](documentation-layer-classification.md) | DRAFT |
| GOV-WAIVER-001 | [Waiver register](waiver-register.md) | DRAFT |
| GOV-COMPL-001 | [Compliance & data-privacy register](compliance-register.md) | DRAFT — chờ OD-007 |
| GOV-TPL-INC-001 | [Incident record / post-mortem template](templates/incident-record.md) | DRAFT |

### Shared (cross-cutting) — `docs/shared/`

| ID | Artifact | Status |
|---|---|---|
| PRD-NFR-001 | [Non-functional and security requirements](../shared/product/non-functional-requirements.md) | IN_REVIEW |
| PRD-GLOSSARY-001 | [Glossary](../shared/glossary.md) | IN_REVIEW |

### Backend — Product — `docs/backend/product/`

| ID | Artifact | Status |
|---|---|---|
| PRD-CHARTER-001 | [Product charter](../backend/product/product-charter.md) | IN_REVIEW |
| PRD-FR-001 | [Functional requirements](../backend/product/functional-requirements.md) | IN_REVIEW |

### Backend — Architecture and domain — `docs/backend/architecture/`, `docs/backend/domain/`

| ID | Artifact | Status |
|---|---|---|
| ARC-C4-001 | [C4 context](../backend/architecture/c4-context.md) | IN_REVIEW |
| ARC-C4-002 | [C4 container](../backend/architecture/c4-container.md) | IN_REVIEW |
| ARC-SEQ-001 | [Runtime sequences](../backend/architecture/runtime-sequences.md) | IN_REVIEW |
| ARC-TECH-001 | [Language and technology policy](../backend/architecture/language-and-technology-policy.md) | IN_REVIEW |
| ARC-AI-001 | [AI provider-neutral/BYOK architecture](../backend/architecture/ai-provider-byok-architecture.md) | DRAFT |
| DOM-MODEL-001 (title: DOM-001) | [Canonical domain model](../backend/domain/canonical-domain-model.md) | DRAFT |
| DOM-OMS-001 (title: DOM-002) | [OMS state machine](../backend/domain/oms-state-machine.md) | APPROVED baseline — local simulator/Phase 1; §3a transitions remain invalid |
| DOM-RISK-001 (title: DOM-003) | [Risk policy](../backend/domain/risk-policy.md) | DRAFT |
| DOM-ACC-001 (title: DOM-004) | [Accounting policy](../backend/domain/accounting-policy.md) | APPROVED baseline — ledger activation gated by annex |

### Backend — Data — `docs/backend/data/`

| ID | Artifact | Status |
|---|---|---|
| DATA-ARC-001 (title: DATA-001) | [Data architecture](../backend/data/data-architecture.md) | DRAFT |
| DATA-ERD-001 (title: DATA-002) | [ERD](../backend/data/erd.md) | DRAFT |
| DATA-DICT-001 (title: DATA-003) | [Data dictionary](../backend/data/data-dictionary.md) | DRAFT |
| DATA-STD-001 (title: DATA-004) | [Database standards](../backend/data/database-standards.md) | DRAFT |
| DATA-TXN-001 (title: DATA-005) | [Transaction and concurrency](../backend/data/transaction-and-concurrency.md) | APPROVED baseline — local simulator/Phase 1 |
| DATA-OPS-001 (title: DATA-006) | [Database operations](../backend/data/db-operations.md) | DRAFT |
| DATA-MIG-001 (title: DATA-007) | [Migration and backfill playbook](../backend/data/migration-backfill-playbook.md) | DRAFT |

### Backend — Engineering and security/operations — `docs/backend/engineering/`, `docs/backend/security-ops/`

| ID | Artifact | Status |
|---|---|---|
| ENG-REPO-001 | [Repository conventions](../backend/engineering/repository-conventions.md) | IN_REVIEW |
| ENG-PY-001 | [Python coding standards](../backend/engineering/coding-standards-python.md) | IN_REVIEW |
| ENG-TEST-001 | [Test strategy](../backend/engineering/test-strategy.md) | IN_REVIEW |
| ENG-CI-001 | [CI/CD design](../backend/engineering/ci-cd-design.md) | IN_REVIEW |
| ENG-AI-001 | [AI coding protocol](../backend/engineering/ai-coding-protocol.md) | IN_REVIEW |
| ENG-VER-001 | [Versioning và release policy](../backend/engineering/versioning-release-policy.md) | DRAFT |
| ENG-LOG-001 | [Logging standard](../backend/engineering/logging-standard.md) | DRAFT |
| SEC-THREAT-001 (title: SEC-001) | [Threat model](../backend/security-ops/threat-model.md) | IN_REVIEW |
| SEC-ACCESS-001 (title: SEC-002) | [Access-control matrix](../backend/security-ops/access-control-matrix.md) | IN_REVIEW |
| SEC-AUTH-POL-001 (title: SEC-003) | [Auth/session policy](../backend/security-ops/auth-session-policy.md) — doc-ID đổi từ "SEC-AUTH-001" (v0.8.0) để hết va chạm với requirement ID SEC-AUTH-001 trong PRD-NFR-001 §8.1 | DRAFT |
| SEC-SECRETS-001 (title: SEC-004) | [Secrets/key management](../backend/security-ops/secrets-and-key-management.md) | IN_REVIEW |
| SEC-AI-POL-001 | [AI BYOK security and data-egress policy](../backend/security-ops/ai-byok-security-policy.md) | DRAFT |
| OPS-SLO-001 (title: OPS-001) | [SLO/SLI/alert policy](../backend/security-ops/slo-sli-alert-policy.md) | DRAFT |
| OPS-RUN-001 (title: OPS-002) | [Runbook index](../backend/security-ops/runbook-index.md) | IN_REVIEW — catalog RB-001..RB-012 (12 runbook, mỗi file version/status riêng, hiện đều DRAFT), gồm 3 runbook mới: [rate-limit](../backend/security-ops/runbooks/venue-rate-limit.md) · [outbox/DLQ](../backend/security-ops/runbooks/outbox-dlq-backlog.md) · [clock-drift](../backend/security-ops/runbooks/clock-drift.md) |

### Frontend — `docs/frontend/` (input Phase 5/6; không cho phép code trước gate)

| ID | Artifact | Status |
|---|---|---|
| FE-INDEX-001 | [Frontend pack index](../frontend/README.md) | DRAFT |
| FE-CHARTER-001 | [Frontend charter — scope, roles, FR-FE-001..007, phase gating](../frontend/product/frontend-charter.md) | DRAFT |
| FE-SCREEN-001 | [Screen inventory + GAP register route OpenAPI còn thiếu](../frontend/product/screen-inventory.md) | DRAFT |
| FE-API-001 | [API integration contract — wire types, async command, idempotency, 26 error codes](../frontend/architecture/api-integration-contract.md) | DRAFT |
| FE-ARC-001 | [Flutter app architecture — thin client, layers, state, generated client](../frontend/architecture/flutter-app-architecture.md) | DRAFT |
| FE-DS-001 | [Design system — semantic colors 16 OMS states, data display, terminology](../frontend/design/design-system.md) | DRAFT |
| FE-SEC-001 | [Frontend security policy — client secret rules, session/CSRF, BYOK UI](../frontend/security/frontend-security-policy.md) | DRAFT |
| FE-TEST-001 | [Frontend testing strategy — contract/authorization/re-auth tests](../frontend/engineering/frontend-testing-strategy.md) | DRAFT |

### Contracts, ADRs, controls and evidence

| Artifact | Canonical location | Status |
|---|---|---|
| Contract registry — REG-001 | [docs/backend/contracts/contract-registry.md](../backend/contracts/contract-registry.md) | IN_REVIEW |
| HTTP contract | [contracts/api/openapi.yaml](../../contracts/api/openapi.yaml) | IN_REVIEW |
| Command/event/config schemas | [contracts/](../../contracts/) | IN_REVIEW |
| AI BYOK provider/policy/connection schemas | [catalog](../../contracts/config/ai-provider-catalog.v1.schema.json) · [endpoint](../../contracts/config/ai-endpoint-profile.v1.schema.json) · [egress](../../contracts/config/ai-data-egress-policy.v1.schema.json) · [usage](../../contracts/config/ai-usage-policy.v1.schema.json) · [profile](../../contracts/config/ai-policy-profile.v1.schema.json) · [connection](../../contracts/config/ai-provider-connection.v1.schema.json) · [lifecycle command](../../contracts/commands/ai/provider-connection-command.v1.schema.json) · [lifecycle event](../../contracts/events/ai/provider-connection-event.v1.schema.json) | IN_REVIEW — Phase 6 DRAFT |
| Error catalog | [contracts/errors/error-catalog.md](../../contracts/errors/error-catalog.md) | IN_REVIEW |
| ADR set (registry) | [ADR register](adr/README.md) | IN_REVIEW — individual ADRs remain DRAFT until Account Owner approval |
| ADR set (content, 0001–0016) | [docs/backend/adr/](../backend/adr/) | ADR 0001–0005, 0007, 0011, 0012, 0014 APPROVED (2026-08-06); ADR 0006, 0008–0010, 0013, 0015–0016 DRAFT (deadline later phases) |
| Templates — TMP-ADR-001 · TMP-TASK-001 · TMP-GATE-001 | [adr](templates/adr.md) · [task-card](templates/task-card.md) · [gate-record](templates/gate-record.md) | IN_REVIEW |
| Template — GOV-TPL-INC-001 | [incident-record](templates/incident-record.md) | DRAFT |
| Task controls | [tasks/active/](../../tasks/active/) · [tasks/completed/](../../tasks/completed/) | 0.0.0–0.0.7 DONE; 0.5.1/0.5.2/0.6/1.1/1.2 DONE; [Task 1.3 card](../../tasks/active/1.3-durable-submit-fake-venue.yaml) REVIEW on `task/1.3-durable-submit-fake-venue-after-redaction`, awaiting Account Owner; [Task 1.3.1 evidence redaction cleanup](../../tasks/active/1.3.1-evidence-secret-redaction.yaml) REVIEW on dedicated branch after separate Security/Backup Owner action; OD-001 external venue OPEN |
| Repo-root controls | [README](../../README.md) · [AGENTS.md](../../AGENTS.md) · [SECURITY.md](../../SECURITY.md) · [CONTRIBUTING.md](../../CONTRIBUTING.md) · [CODEOWNERS](../../CODEOWNERS) | IN_REVIEW — COMMIT_NOTES.md đã xóa 2026-08-10 theo quyết định Account Owner (nội dung trong git history) |
| Gate evidence | [gate record](evidence/gates/phase-0.0/gate-record.md) · [review checklist](evidence/gates/phase-0.0/review-checklist.md) · [validation 2026-08-02](evidence/gates/phase-0.0/validation-2026-08-02.md) · [validation 2026-08-02 lần 2](evidence/gates/phase-0.0/validation-2026-08-02-02.md) | APPROVED / REVALIDATED 2026-08-10T20:07:02Z — Account Owner ký lại sau Task 0.0.7 |
| Task evidence | [docs/governance/evidence/tasks/](evidence/tasks/) | IN_REVIEW — gồm evidence 0.1–0.6, Task 1.1 deterministic primitives, Task 1.2 OMS state machine và [Task 1.3 one-time approval packet v0.3.0](evidence/tasks/1.3/ONE-TIME-APPROVAL-PACKET.md), [one-time approval record](evidence/tasks/1.3/approval-record-2026-08-12.md), [ADR-0003 PostgreSQL 17 approval](evidence/tasks/1.3/postgresql-17-approval-2026-08-12.md), [Supabase Local installation evidence](evidence/tasks/1.3/supabase-local-install-evidence-2026-08-12.md), [Enterprise-Grade readiness audit](evidence/tasks/1.3/enterprise-readiness-audit.md), [control closure matrix](evidence/tasks/1.3/enterprise-control-closure-matrix.md), [approved risk fixture](evidence/tasks/1.3/risk-profile.local-simulator.v1.approved.json), [fake venue scenario schema](evidence/tasks/1.3/fake-venue-scenario.v1.schema.json), [dictionary addendum](evidence/tasks/1.3/execution-risk-dictionary-addendum.md), [traceability matrix](evidence/tasks/1.3/task-1.3-traceability-matrix.md) và [runbook drill plan](evidence/tasks/1.3/task-1.3-runbook-drill-plan.md) cùng các phụ lục [Account Owner approval record](evidence/tasks/1.3/account-owner-approval-2026-08-12.md), [decision register](evidence/tasks/1.3/owner-decision-register.md), [risk/Fill/concurrency closure](evidence/tasks/1.3/risk-fill-concurrency-closure.md), [data/persistence closure](evidence/tasks/1.3/data-persistence-closure.md), [fake venue closure](evidence/tasks/1.3/fake-venue-closure.md), [ADR amendment proposal](evidence/tasks/1.3/adr-0012-amendment-proposal.md), [implementation card proposal](evidence/tasks/1.3/implementation-task-card-proposal.yaml), [validation evidence](evidence/tasks/1.3/preflight-validation-2026-08-12.md), [automated self-check](evidence/tasks/1.3/task-1.3-self-check-2026-08-13.md), [implementation review](evidence/tasks/1.3/task-1.3-implementation-review-2026-08-13.md), [evidence redaction cleanup proposal](evidence/tasks/1.3/evidence-secret-redaction-cleanup-task-proposal.yaml) và [cleanup approval](evidence/tasks/1.3/evidence-secret-redaction-cleanup-approval.md); approval record `2026-08-13T14:06:43Z`; Task 1.3 REVIEW, Task 1.3.1 REVIEW |

## Approval rule

Update this register and `docs/governance/document-control.md` in the same review change. A file changing to `APPROVED` must record approver identity, UTC timestamp, decision evidence and any supersession link. Never mark an ADR or gate `APPROVED` merely because its draft exists.

## Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.14.23 | 2026-08-13 | Hoàn tất implementation/evidence Task 1.3 durable submit/fake venue; self-check Docker/Supabase/PostgreSQL no-skip đạt PASS=23, INFO=2, BLOCKED=0, FAIL=0; chuyển card `IN_PROGRESS → REVIEW`, chờ Account Owner nghiệm thu. | Technical Operator | Account Owner review pending `2026-08-13T14:19:42Z` |
| 0.14.19 | 2026-08-12 | Ghi nhận ADR-0003 PostgreSQL 17 approval, đồng bộ authority, khởi động Supabase Local `AI_Auto_Trade`, áp dụng Alembic baseline và lưu no-skip test evidence; canonical Task 1.3 card vẫn `BLOCKED` chờ `READY`. | Technical Operator | Account Owner approval `2026-08-12T11:15:53Z`; runtime implementation remains gated |
| 0.14.18 | 2026-08-12 | Ghi nhận one-time approval record; chuyển card 0.0.7 về `tasks/completed/`; tạo canonical Task 1.3 card ở `BLOCKED`, tạo branch `task/1.3-durable-submit-fake-venue`, commit docs và đồng bộ control panel; chưa mở code vì thiếu PostgreSQL no-skip. | Technical Operator | Account Owner approval `2026-08-12T09:19:16Z`; execution blocker remains |
| 0.14.17 | 2026-08-12 | Bổ sung P-68 về task-directory hygiene; đồng bộ audit/preflight/register để ghi rõ card `DONE` còn nằm trong `tasks/active/`, và thêm Security/Backup Owner review cho control security/backup; giữ packet v0.2.1 pending approval và implementation BLOCKED. | Technical Operator | Pending Account Owner/Risk Approver/Security/Backup Owner review |
| 0.14.16 | 2026-08-12 | Bổ sung risk fixture, fake-venue scenario schema/fixture, column-level dictionary addendum, traceability matrix và runbook drill plan; giữ packet v0.2.0 pending approval và implementation BLOCKED. | Technical Operator | Pending Account Owner/Risk Approver review |
| 0.14.15 | 2026-08-12 | Bổ sung Enterprise-Grade readiness audit/control closure matrix và mở rộng one-time packet với cross-cutting controls; implementation vẫn BLOCKED. | Technical Operator | Pending Account Owner/Risk Approver review |
| 0.14.14 | 2026-08-12 | Ghi nhận Account Owner approval baseline packet v0.1.0; risk-sensitive items vẫn cần Risk Approver và implementation vẫn BLOCKED. | Technical Operator | Account Owner `2026-08-12T08:56:11Z`; Risk Approver pending |
| 0.14.13 | 2026-08-12 | Tạo gói phê duyệt một lần và phụ lục ADR/task-card proposal cho Task 1.3; giữ toàn bộ artifact ở DRAFT/BLOCKED. | Technical Operator | Pending Account Owner/Risk Approver review |
| 0.14.12 | 2026-08-12 | Ghi nhận Account Owner acknowledgement cho candidate baseline Task 1.3; 12 decision vẫn OPEN và implementation vẫn BLOCKED. | Technical Operator | Account Owner acknowledgement `2026-08-12T08:33:58Z`; final approval pending |
| 0.14.11 | 2026-08-12 | Bổ sung decision register, các closure draft và validation evidence cho Task 1.3; giữ implementation BLOCKED và không thay đổi task authority. | Technical Operator | Pending Account Owner/Risk Approver review |
| 0.14.10 | 2026-08-12 | Thêm gói preflight Task 1.3 cho durable submit/local fake venue ở trạng thái DRAFT/BLOCKED; không mở task implementation hoặc thay đổi gate. | Technical Operator | Pending Account Owner review |
| 0.14.9 | 2026-08-12 | Account Owner xác nhận DONE Task 1.2; chuyển card completed; đồng bộ control references và giữ Task 1.3 chưa mở card. | Technical Operator | Account Owner `2026-08-11T20:06:59Z` |
| 0.14.8 | 2026-08-12 | Hoàn tất implementation/evidence Task 1.2; chuyển card IN_PROGRESS → REVIEW; đồng bộ control references và chờ Account Owner nghiệm thu. | Technical Operator | Pending Account Owner review |
| 0.14.7 | 2026-08-12 | Bắt đầu thực thi Task 1.2; chuyển card READY → IN_PROGRESS; đồng bộ control references. | Technical Operator | Account Owner baseline approval `2026-08-11T19:52:15Z` |
| 0.14.6 | 2026-08-12 | Account Owner phê duyệt baseline normative docs cho Phase 1; mở Task 1.2 OMS deterministic state machine READY và đồng bộ control references. | Technical Operator | Account Owner `2026-08-11T19:52:15Z` |
| 0.14.5 | 2026-08-12 | Account Owner xác nhận DONE Task 1.1; chuyển card completed; đồng bộ control references và ghi nhận blocker normative docs trước OMS task tiếp theo. | Technical Operator | Account Owner 2026-08-11T19:41:38Z |
| 0.14.4 | 2026-08-12 | Hoàn tất implementation/evidence Task 1.1; chuyển card IN_PROGRESS → REVIEW; đồng bộ control references và chờ Account Owner nghiệm thu. | Technical Operator | Pending Account Owner review |
| 0.14.3 | 2026-08-12 | Bắt đầu thực thi Task 1.1; chuyển card READY → IN_PROGRESS; đồng bộ control references. | Technical Operator | Account Owner 2026-08-11T19:16:45Z |
| 0.14.2 | 2026-08-12 | Mở Phase 1 local simulator/no venue; tạo Task 1.1 deterministic primitives READY; đồng bộ control references. | Technical Operator | Account Owner 2026-08-11T19:16:45Z |
| 0.14.1 | 2026-08-12 | Account Owner xác định DONE Task 0.6; chuyển card completed; đồng bộ control references và chuẩn bị Phase 1 deterministic-primitives task card. | Technical Operator | Account Owner 2026-08-11T19:16:45Z |
| 0.14.0 | 2026-08-11 | Hoàn tất operator phần Task 0.6; chuyển card IN_PROGRESS → REVIEW sau khi tạo capability matrix draft docs-only; đồng bộ trạng thái control references. | Technical Operator | Account Owner scope decision 2026-08-11T02:26:26Z; review requested 2026-08-11T02:32:26Z |
| 0.13.1 | 2026-08-11 | Bắt đầu thực thi Task 0.6; chuyển card READY → IN_PROGRESS sau khi tạo capability matrix draft docs-only; đồng bộ trạng thái control references. | Technical Operator | Account Owner scope decision 2026-08-11T02:26:26Z; execution 2026-08-11T02:29:48Z |
| 0.13.0 | 2026-08-11 | Account Owner xác nhận local simulator/no venue; mở Task 0.6 Capability draft READY; đồng bộ card/evidence/control references; OD-001 external venue vẫn OPEN. | Technical Operator | Account Owner 2026-08-11T02:26:26Z |
| 0.12.0 | 2026-08-11 | Account Owner xác định DONE Task 0.5.2; chuyển card completed; cập nhật evidence, control panel và trạng thái Task 0.6 BLOCKED do OD-001 OPEN. | Technical Operator | Account Owner 2026-08-11T02:14:42Z |
| 0.11.0 | 2026-08-11 | Account Owner approve Task 0.5.1; chuyển card completed; mở Task 0.5.2 READY. | Technical Operator | Account Owner 2026-08-11T00:30:47Z |
| 0.10.0 | 2026-08-11 | Tạo Task 0.0.7 Codex Enterprise documentation; đồng bộ master/AGENTS/README/task controls; đánh dấu gate Phase 0.0 cần revalidation sau substantive change; thêm evidence pointer cho task mới. | Technical Operator | Account Owner revalidated 2026-08-10T20:07:02Z |
| 0.9.1 | 2026-08-10 | Đồng bộ state sau Task 0.1–0.4 DONE: row Task controls (tasks/active/ trống, chờ card Task 0.5), Gate evidence (PASSED 2026-08-06), Task evidence (bổ sung 0.1–0.4); gỡ COMMIT_NOTES.md khỏi repo-root controls (file đã xóa theo quyết định Account Owner, nội dung trong git history); ghi nhận xóa `.kiro/` hooks (tool-specific, không thuộc artifact pack); master authority v2.2.3. | Technical Operator | Pending |
| 0.9.0 | 2026-08-06 | Gate Phase 0.0 PASSED — Account Owner approval. ADR 0001-0005/0007/0011/0012/0014 → APPROVED; task 0.0.x → completed; task 0.1 → READY; DOCS_INDEX → APPROVED. | Account Owner | Account Owner 2026-08-06 |
| 0.8.0 | 2026-08-02 | Audit toàn diện đợt 2 (6 cụm song song): đổi doc-ID SEC-AUTH-001 → SEC-AUTH-POL-001 (hết va chạm requirement ID); alias title-ID cho 13 tài liệu SEC-001..004/OPS-001..002/DATA-001..007 + REG-001; row ADR content ghi đúng "DRAFT (16/16)"; tách row template theo ID/status (GOV-TPL-INC-001 DRAFT); row gate/task evidence phản ánh chuỗi validation EV-GATE-0.0-2026-08-02-01/-02 và trạng thái stale của EV-0.0.6; header index bổ sung Ngày hiệu lực/Rà soát/Change summary; master authority v2.2.2. | Technical Operator | Pending |
| 0.7.0 | 2026-08-02 | Đồng bộ audit chéo 2026-08-02: addendum GOV-CLASS (103 tệp, Frontend lần đầu khác 0), FR-FE-001..007 vào traceability, RACI thêm row waiver, RAID thêm D-008/I-005..I-008, checklist 0.0.7/0.0.8, document-control §6 sửa row Frontend/Governance + thêm row Templates; master authority v2.2.1 + OD-009/010; thêm alias title-ID cho 4 tài liệu domain (DOM-001..004) và link COMMIT_NOTES.md vào repo-root controls. | Technical Operator | Pending |
| 0.6.0 | 2026-07-31 | Khởi tạo bộ tài liệu Frontend 8 artifact (FE-INDEX/CHARTER/SCREEN/API/ARC/DS/SEC/TEST-001, DRAFT) — trích xuất từ contract backend, input Phase 5/6; docs/frontend/ không còn là placeholder rỗng. | Technical Operator | Pending |
| 0.5.0 | 2026-07-31 | Bổ sung theo audit sâu backend: logging standard (ENG-LOG-001), 3 runbook mới RB-010/011/012; master authority v2.2.0; ~20 tài liệu backend được bổ sung nội dung (Fill contract, TIF matrix, isolation proposal, tech decisions, escalation logic...) và sửa nhất quán (FR-OMS-001, dead_letters FK, doc-ID scheme). | Technical Operator | Pending |
| 0.4.0 | 2026-07-31 | Bổ sung theo audit hoàn thiện hồ sơ: waiver register, compliance register, incident template, versioning/release policy, task card 0.1 (BLOCKED), bộ repo-root controls (README/AGENTS/SECURITY/CONTRIBUTING/CODEOWNERS/.editorconfig/.gitignore). | Technical Operator | Pending |
| 0.3.0 | 2026-07-31 | Tái cấu trúc docs/ theo lớp Backend/Frontend/Shared/Governance (GOV-CLASS-001): cập nhật toàn bộ đường dẫn register, thêm mục Frontend placeholder; không đổi status/nội dung artifact nào. | Technical Operator | Pending |
| 0.2.0 | 2026-07-31 | Bổ sung architecture, security policy và full provider/policy/connection contract baseline cho AI đa provider/BYOK DRAFT; cập nhật master authority v2.1.0. | Technical Operator | Pending |
| 0.1.0 | 2026-07-31 | Tạo chỉ mục artifact pack Phase 0.0. | Technical Operator | Pending |
