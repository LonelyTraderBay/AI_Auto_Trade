# DOCS_INDEX — AI Auto Trade Phase 0.0

| Thuộc tính | Giá trị |
|---|---|
| Document ID | GOV-INDEX-001 |
| Phiên bản | 0.3.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner |
| Ngày tạo | 2026-07-31 |
| Master authority | [AI_AUTO_TRADE_MASTER_SPEC.md](../../AI_AUTO_TRADE_MASTER_SPEC.md) v2.1.1 |

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
| DOM-MODEL-001 | [Canonical domain model](../backend/domain/canonical-domain-model.md) | DRAFT |
| DOM-OMS-001 | [OMS state machine](../backend/domain/oms-state-machine.md) | DRAFT |
| DOM-RISK-001 | [Risk policy](../backend/domain/risk-policy.md) | DRAFT |
| DOM-ACC-001 | [Accounting policy](../backend/domain/accounting-policy.md) | DRAFT |

### Backend — Data — `docs/backend/data/`

| ID | Artifact | Status |
|---|---|---|
| DATA-ARC-001 | [Data architecture](../backend/data/data-architecture.md) | DRAFT |
| DATA-ERD-001 | [ERD](../backend/data/erd.md) | DRAFT |
| DATA-DICT-001 | [Data dictionary](../backend/data/data-dictionary.md) | DRAFT |
| DATA-STD-001 | [Database standards](../backend/data/database-standards.md) | DRAFT |
| DATA-TXN-001 | [Transaction and concurrency](../backend/data/transaction-and-concurrency.md) | DRAFT |
| DATA-OPS-001 | [Database operations](../backend/data/db-operations.md) | DRAFT |
| DATA-MIG-001 | [Migration and backfill playbook](../backend/data/migration-backfill-playbook.md) | DRAFT |

### Backend — Engineering and security/operations — `docs/backend/engineering/`, `docs/backend/security-ops/`

| ID | Artifact | Status |
|---|---|---|
| ENG-REPO-001 | [Repository conventions](../backend/engineering/repository-conventions.md) | IN_REVIEW |
| ENG-PY-001 | [Python coding standards](../backend/engineering/coding-standards-python.md) | IN_REVIEW |
| ENG-TEST-001 | [Test strategy](../backend/engineering/test-strategy.md) | IN_REVIEW |
| ENG-CI-001 | [CI/CD design](../backend/engineering/ci-cd-design.md) | IN_REVIEW |
| ENG-AI-001 | [AI coding protocol](../backend/engineering/ai-coding-protocol.md) | IN_REVIEW |
| SEC-THREAT-001 | [Threat model](../backend/security-ops/threat-model.md) | IN_REVIEW |
| SEC-ACCESS-001 | [Access-control matrix](../backend/security-ops/access-control-matrix.md) | IN_REVIEW |
| SEC-AUTH-001 | [Auth/session policy](../backend/security-ops/auth-session-policy.md) | DRAFT |
| SEC-SECRETS-001 | [Secrets/key management](../backend/security-ops/secrets-and-key-management.md) | IN_REVIEW |
| SEC-AI-POL-001 | [AI BYOK security and data-egress policy](../backend/security-ops/ai-byok-security-policy.md) | DRAFT |
| OPS-SLO-001 | [SLO/SLI/alert policy](../backend/security-ops/slo-sli-alert-policy.md) | DRAFT |
| OPS-RUN-001 | [Runbook index](../backend/security-ops/runbook-index.md) | IN_REVIEW |

### Frontend — `docs/frontend/`

| ID | Artifact | Status |
|---|---|---|
| — | [docs/frontend/README.md](../frontend/README.md) — placeholder có chủ đích, chưa có nội dung; xem GOV-CLASS-001 | N/A |

### Contracts, ADRs, controls and evidence

| Artifact | Canonical location | Status |
|---|---|---|
| Contract registry | [docs/backend/contracts/contract-registry.md](../backend/contracts/contract-registry.md) | IN_REVIEW |
| HTTP contract | [contracts/api/openapi.yaml](../../contracts/api/openapi.yaml) | IN_REVIEW |
| Command/event/config schemas | [contracts/](../../contracts/) | IN_REVIEW |
| AI BYOK provider/policy/connection schemas | [catalog](../../contracts/config/ai-provider-catalog.v1.schema.json) · [endpoint](../../contracts/config/ai-endpoint-profile.v1.schema.json) · [egress](../../contracts/config/ai-data-egress-policy.v1.schema.json) · [usage](../../contracts/config/ai-usage-policy.v1.schema.json) · [profile](../../contracts/config/ai-policy-profile.v1.schema.json) · [connection](../../contracts/config/ai-provider-connection.v1.schema.json) · [lifecycle command](../../contracts/commands/ai/provider-connection-command.v1.schema.json) · [lifecycle event](../../contracts/events/ai/provider-connection-event.v1.schema.json) | IN_REVIEW — Phase 6 DRAFT |
| Error catalog | [contracts/errors/error-catalog.md](../../contracts/errors/error-catalog.md) | IN_REVIEW |
| ADR set (registry) | [ADR register](adr/README.md) | IN_REVIEW — individual ADRs remain DRAFT until Account Owner approval |
| ADR set (content, 0001–0016) | [docs/backend/adr/](../backend/adr/) | IN_REVIEW/DRAFT theo từng ADR |
| Templates | [docs/governance/templates/](templates/) | IN_REVIEW |
| Task controls | [tasks/active/](../../tasks/active/) | IN_REVIEW |
| Gate evidence | [gate record](evidence/gates/phase-0.0/gate-record.md) · [review checklist](evidence/gates/phase-0.0/review-checklist.md) | IN_REVIEW — not passed |
| Task evidence | [docs/governance/evidence/tasks/](evidence/tasks/) | IN_REVIEW — placeholder only; no validation result recorded |

## Approval rule

Update this register and `docs/governance/document-control.md` in the same review change. A file changing to `APPROVED` must record approver identity, UTC timestamp, decision evidence and any supersession link. Never mark an ADR or gate `APPROVED` merely because its draft exists.

## Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.3.0 | 2026-07-31 | Tái cấu trúc docs/ theo lớp Backend/Frontend/Shared/Governance (GOV-CLASS-001): cập nhật toàn bộ đường dẫn register, thêm mục Frontend placeholder; không đổi status/nội dung artifact nào. | Technical Operator | Pending |
| 0.2.0 | 2026-07-31 | Bổ sung architecture, security policy và full provider/policy/connection contract baseline cho AI đa provider/BYOK DRAFT; cập nhật master authority v2.1.0. | Technical Operator | Pending |
| 0.1.0 | 2026-07-31 | Tạo chỉ mục artifact pack Phase 0.0. | Technical Operator | Pending |
