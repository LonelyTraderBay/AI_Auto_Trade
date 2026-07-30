# DOCS_INDEX — AI Auto Trade Phase 0.0

| Thuộc tính | Giá trị |
|---|---|
| Document ID | GOV-INDEX-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner |
| Ngày tạo | 2026-07-31 |
| Master authority | [AI_AUTO_TRADE_MASTER_SPEC.md](../AI_AUTO_TRADE_MASTER_SPEC.md) v2.0.0 |

## Mục đích và trạng thái

Đây là chỉ mục chính thức của artifact pack Phase 0.0. Các tài liệu trong pack đã được tạo để review; **không tài liệu nào trong trạng thái `DRAFT` hoặc `IN_REVIEW` được phép mở Phase 0 hay cho phép code application, migration, endpoint hoặc venue integration**.

Khi có mâu thuẫn, áp dụng hierarchy ở §1.5 của master. Physical schema, wire contract và runtime config chỉ trở thành authority thực thi sau khi artifact tương ứng được review/approved theo master.

## Trình tự review bắt buộc

1. Governance, scope, requirements và RACI.
2. ADR 0001–0005, 0007, 0011, 0012 và 0014.
3. Architecture/domain/data policy và data dictionary cho Task 0.3.
4. Contract registry, OpenAPI, JSON Schema và task-card control.
5. Engineering/CI/security/operations policy.
6. Task 0.1 card, validation record và gate record Phase 0.0.

## Document register

### Governance

| ID | Artifact | Status |
|---|---|---|
| GOV-DOC-001 | [Document control](00-governance/document-control.md) | IN_REVIEW |
| GOV-RACI-001 | [RACI](00-governance/raci.md) | IN_REVIEW |
| GOV-RAID-001 | [RAID register](00-governance/raid-register.md) | IN_REVIEW |
| GOV-TRACE-001 | [Requirements traceability](00-governance/requirements-traceability.md) | IN_REVIEW |

### Product

| ID | Artifact | Status |
|---|---|---|
| PRD-CHARTER-001 | [Product charter](01-product/product-charter.md) | IN_REVIEW |
| PRD-FR-001 | [Functional requirements](01-product/functional-requirements.md) | IN_REVIEW |
| PRD-NFR-001 | [Non-functional and security requirements](01-product/non-functional-requirements.md) | IN_REVIEW |
| PRD-GLOSSARY-001 | [Glossary](01-product/glossary.md) | IN_REVIEW |

### Architecture and domain

| ID | Artifact | Status |
|---|---|---|
| ARC-C4-001 | [C4 context](02-architecture/c4-context.md) | IN_REVIEW |
| ARC-C4-002 | [C4 container](02-architecture/c4-container.md) | IN_REVIEW |
| ARC-SEQ-001 | [Runtime sequences](02-architecture/runtime-sequences.md) | IN_REVIEW |
| ARC-TECH-001 | [Language and technology policy](02-architecture/language-and-technology-policy.md) | IN_REVIEW |
| DOM-MODEL-001 | [Canonical domain model](03-domain/canonical-domain-model.md) | DRAFT |
| DOM-OMS-001 | [OMS state machine](03-domain/oms-state-machine.md) | DRAFT |
| DOM-RISK-001 | [Risk policy](03-domain/risk-policy.md) | DRAFT |
| DOM-ACC-001 | [Accounting policy](03-domain/accounting-policy.md) | DRAFT |

### Data

| ID | Artifact | Status |
|---|---|---|
| DATA-ARC-001 | [Data architecture](04-data/data-architecture.md) | DRAFT |
| DATA-ERD-001 | [ERD](04-data/erd.md) | DRAFT |
| DATA-DICT-001 | [Data dictionary](04-data/data-dictionary.md) | DRAFT |
| DATA-STD-001 | [Database standards](04-data/database-standards.md) | DRAFT |
| DATA-TXN-001 | [Transaction and concurrency](04-data/transaction-and-concurrency.md) | DRAFT |
| DATA-OPS-001 | [Database operations](04-data/db-operations.md) | DRAFT |
| DATA-MIG-001 | [Migration and backfill playbook](04-data/migration-backfill-playbook.md) | DRAFT |

### Engineering and security/operations

| ID | Artifact | Status |
|---|---|---|
| ENG-REPO-001 | [Repository conventions](05-engineering/repository-conventions.md) | IN_REVIEW |
| ENG-PY-001 | [Python coding standards](05-engineering/coding-standards-python.md) | IN_REVIEW |
| ENG-TEST-001 | [Test strategy](05-engineering/test-strategy.md) | IN_REVIEW |
| ENG-CI-001 | [CI/CD design](05-engineering/ci-cd-design.md) | IN_REVIEW |
| ENG-AI-001 | [AI coding protocol](05-engineering/ai-coding-protocol.md) | IN_REVIEW |
| SEC-THREAT-001 | [Threat model](06-security-ops/threat-model.md) | IN_REVIEW |
| SEC-ACCESS-001 | [Access-control matrix](06-security-ops/access-control-matrix.md) | IN_REVIEW |
| SEC-AUTH-001 | [Auth/session policy](06-security-ops/auth-session-policy.md) | DRAFT |
| SEC-SECRETS-001 | [Secrets/key management](06-security-ops/secrets-and-key-management.md) | IN_REVIEW |
| OPS-SLO-001 | [SLO/SLI/alert policy](06-security-ops/slo-sli-alert-policy.md) | DRAFT |
| OPS-RUN-001 | [Runbook index](06-security-ops/runbook-index.md) | IN_REVIEW |

### Contracts, ADRs, controls and evidence

| Artifact | Canonical location | Status |
|---|---|---|
| Contract registry | [docs/contract-registry.md](contract-registry.md) | IN_REVIEW |
| HTTP contract | [contracts/api/openapi.yaml](../contracts/api/openapi.yaml) | IN_REVIEW |
| Command/event/config schemas | [contracts/](../contracts/) | IN_REVIEW |
| Error catalog | [contracts/errors/error-catalog.md](../contracts/errors/error-catalog.md) | IN_REVIEW |
| ADR set | [ADR register](adr/README.md) | DRAFT — Account Owner approval pending |
| Templates | [docs/templates/](templates/) | IN_REVIEW |
| Task controls | [tasks/active/](../tasks/active/) | IN_REVIEW |
| Gate evidence | [gate record](evidence/gates/phase-0.0/gate-record.md) · [review checklist](evidence/gates/phase-0.0/review-checklist.md) | IN_REVIEW — not passed |
| Task evidence | [docs/evidence/tasks/](evidence/tasks/) | NOT_STARTED |

## Approval rule

Update this register and `docs/00-governance/document-control.md` in the same review change. A file changing to `APPROVED` must record approver identity, UTC timestamp, decision evidence and any supersession link. Never mark an ADR or gate `APPROVED` merely because its draft exists.
