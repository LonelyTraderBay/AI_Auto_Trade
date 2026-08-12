# Task 1.3 — Enterprise control closure matrix

| Trường | Giá trị |
|---|---|
| Document ID | GOV-TASK-1.3-ENTERPRISE-CONTROLS-001 |
| Phiên bản | 0.2.0 |
| Trạng thái | APPROVED FOR TASK 1.3 DESIGN; runtime evidence pending |
| Parent | [One-time approval packet](ONE-TIME-APPROVAL-PACKET.md) |
| Authority references | Master §7, §12, §13, §14; SEC-001; SEC-002; ENG-LOG-001; DATA-OPS-001; ENG-TEST-001 |

> Ma trận này đóng các khoảng trống Enterprise-Grade ngoài domain decision. Mỗi control phải có owner, enforcement point và evidence; không được dùng tuyên bố trong Markdown để thay thế test hoặc gate.

## 1. Control matrix

| ID | Control | Enforcement point | Evidence bắt buộc | Scope/status |
|---|---|---|---|---|
| EC-01 | Actor/machine identity và correlation | Command/event envelope, audit boundary | Actor, role, trace/correlation/causation IDs; negative identity test | Task 1.3 — REQUIRED |
| EC-02 | Deny-by-default và scope isolation | Application handler + DB role | Cross-scope denial, no direct adapter write, role matrix review | Task 1.3 — REQUIRED |
| EC-03 | Idempotency/replay | Order/attempt uniqueness + request hash | Same-key same-payload replay; same-key different-payload conflict | Task 1.3 — REQUIRED |
| EC-04 | UNKNOWN safe state | Attempt state + reconciliation case | Timeout/ambiguous response; no blind retry; operator evidence | Task 1.3 — REQUIRED |
| EC-05 | Append-only audit/history | DB permissions + domain API | Update/delete denial; immutable event/fill/order history test | Task 1.3 — REQUIRED |
| EC-06 | Secret/PII redaction | Logger formatter, fixtures, evidence scanner | No secret, credential, raw payload or key-like value in log/evidence | Task 1.3 — REQUIRED |
| EC-07 | Structured logging | Shared logger boundary | JSON-lines fields: timestamp, level, event, trace, correlation, actor, context | Task 1.3 — REQUIRED |
| EC-08 | Operational metrics | Metrics/alert adapter boundary | Counters for UNKNOWN, duplicate, lease loss, reconciliation age, outbox/backlog, DB errors | Task 1.3 — REQUIRED; thresholds pending OPS policy |
| EC-09 | Safe-state alerts | Alert policy/runbook | Critical event maps to freeze/block-new-exposure and alert evidence | Task 1.3 — REQUIRED |
| EC-10 | Runbook coverage | Incident/recovery procedure | Unknown-order, DB unavailable, reconciliation mismatch, trading-node restart drill | Task 1.3 — REQUIRED |
| EC-11 | Database least privilege | Migration grants + runtime role | Runtime cannot DDL/delete history; migrator role separate; grant denial evidence | Task 1.3 — REQUIRED |
| EC-12 | Migration safety | Approved migration + expand/forward-fix | Revision/schema snapshot, lock/timeout plan, forward-fix and compatibility evidence | Task 1.3 — REQUIRED before DDL |
| EC-13 | Backup/restore boundary | DB operations runbook | Restore procedure and consistency-set checklist | Task 1.3 — design required; drill before canary |
| EC-14 | Data retention/legal hold | ADR-0013 + retention matrix | Retention/hold/archive/purge rule and owner | DEFERRED before Phase 2; no purge in Task 1.3 |
| EC-15 | Contract compatibility | Registry + fixture validator | Schema validation, version, fixture, compatibility/upcaster evidence | Task 1.3 — REQUIRED |
| EC-16 | Architecture/import boundary | Import linter/pyright | Domain has no FastAPI/DB/vendor/venue SDK import | Task 1.3 — REQUIRED |
| EC-17 | Deterministic test data | Clock/random/Decimal fixture | UTC, seed, Decimal context, scenario revision and checksum | Task 1.3 — REQUIRED |
| EC-18 | Fault and chaos evidence | Fake venue/test harness | Duplicate, partial, out-of-order, timeout, crash, lease loss, DB failure | Task 1.3 — REQUIRED |
| EC-19 | Quality/supply chain | Locked toolchain + diff policy | `uv sync --locked`, Ruff, Pyright, tests, schema validator, diff/secret scan | Task 1.3 — REQUIRED |
| EC-20 | Rollback/forward-fix | Task card + migration playbook | Revert code safely; forward-fix schema; preserve financial/audit history | Task 1.3 — REQUIRED |
| EC-21 | Threat review | SEC-001 threat register | T-003/T-004/T-006/T-007/T-011/T-018 control mapping | Task 1.3 — REQUIRED |
| EC-22 | Access matrix review | SEC-002 role/process matrix | Human/machine deny tests; dual-role record; no direct venue access | Task 1.3 — REQUIRED |
| EC-23 | SLO/alert thresholds | OPS-001 | Numeric thresholds/escalation owner | Deferred until OPS-001 approval; Task 1.3 must emit fields |
| EC-24 | Performance benchmark | ENG-TEST-001 | Submit-to-ack benchmark | Deferred to Phase 2 paper; no performance claim in Task 1.3 |
| EC-25 | External venue readiness | OD-001/ADR-0009 | Capability/terms/credential/recovery evidence | Deferred; explicitly forbidden in Task 1.3 |
| EC-26 | AI boundary | ADR-0008/0016 | Proof no AI execution port/venue credential | Task 1.3 — REQUIRED negative check; AI runtime deferred |

## 2. Required evidence manifest

Before implementation can reach `REVIEW`, evidence must include:

- `contract-validation.txt` — schema/fixture output and registry versions.
- `quality-commands.txt` — command, UTC start/end, exit code and artifact path.
- `task-1.3-invariant-report.md` — idempotency, UNKNOWN, immutable history, lease/CAS and Decimal results.
- `fake-venue-conformance-report.md` — all scenario IDs, seed/clock/revision and result.
- `postgres-migration-report.md` — revision, schema snapshot, grants, constraints, indexes and no-skip integration result.
- `fault-injection-report.md` — timeout, duplicate, crash, out-of-order, lease loss and DB failure.
- `security-negative-report.md` — secret/log redaction, access denial, no AI/venue path, import boundary.
- `recovery-runbook-drill.md` — unknown-order, reconciliation and restart procedure evidence.
- `rollback-forward-fix-report.md` — safe revert/forward-fix and preserved history.
- `risk-profile.local-simulator.v1.approved.json` — synthetic-only risk profile with approved hash/effective/expiry; draft candidate retained for provenance.
- `fake-venue-scenario.v1.schema.json` + `fake-venue-scenario.v1.valid.json` — versioned deterministic scenario contract/fixture.
- `execution-risk-dictionary-addendum.md` — column-level proposal before DDL.
- `task-1.3-traceability-matrix.md` — requirement/ADR/contract/test/evidence links.
- `task-1.3-runbook-drill-plan.md` — recovery/fault drill steps and safe-state expectations.

## 3. Gaps found in current repository

| Gap | Current evidence | Required action |
|---|---|---|
| No active canonical Task 1.3 card | Master/README/DOCS_INDEX say card not opened | Create `tasks/active/1.3-*.yaml` only after approval prerequisites |
| Risk policy/Fill/data/ERD drafts | DOCS_INDEX status rows | Approve or explicitly defer each item; no implementation from draft |
| Fake venue harness not implemented | ENG-TEST-001 §5 is DRAFT | Name owner, version scenario contract, create conformance test task |
| ADR-0012 wording conflict | APPROVED header with `If approved` body | Apply reviewed amendment proposal |
| Contract registry IN_REVIEW | REG-001 status | Approve implementation permission for C-CMD-002/C-EVT-002/FVENUE-1 |
| PostgreSQL integration skipped | `DATABASE_URL` missing | Run ephemeral PostgreSQL test and save no-skip evidence |
| Logging/DB ops/SLO policies not effective | ENG-LOG-001/DATA-OPS-001/OPS-001 DRAFT | Use master/approved ADR minimum for Task 1.3; approve numeric operations before paper/canary |
| Threat/access docs IN_REVIEW | SEC-001/SEC-002 | Record review mapping; no direct credential/network scope |

## 4. Approval boundary

Approval record [GOV-TASK-1.3-APPROVAL-20260812-091916](approval-record-2026-08-12.md) authorizes the control requirements and their evidence plan for Task 1.3. It does not make unrelated DRAFT policy documents `APPROVED`, does not authorize external venue, and does not waive the PostgreSQL integration/no-skip requirement or any non-waivable safety invariant.
