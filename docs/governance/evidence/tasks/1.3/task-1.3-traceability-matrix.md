# Task 1.3 — Requirement/authority/test traceability

| Trường | Giá trị |
|---|---|
| Document ID | GOV-TASK-1.3-TRACE-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | APPROVED FOR TASK 1.3 DESIGN — runtime evidence pending |
| Parent | [One-time approval packet](ONE-TIME-APPROVAL-PACKET.md) |

## Traceability matrix

| Requirement | Authority/ADR | Packet IDs | Implementation boundary | Test/evidence |
|---|---|---|---|---|
| FR-EXEC-001 | DOM-OMS-001; ADR-0005; C-CMD-002/C-EVT-002 | P-06..P-20, P-31..P-48 | Execution order/attempt/event/fill | State transition, idempotency, contract, replay, fault reports |
| FR-RSK-001 | DOM-RISK-001; ADR-0007; DATA-TXN-001 | P-21..P-30, P-31, P-49..P-53 | Risk decision/reservation boundary; fail closed | Policy fixture, stale/freshness/cap/kill-switch/reservation tests |
| FR-REC-001 | ADR-0007; ADR-0012; C-EVT-002 | P-11..P-13, P-33..P-35, P-41, P-53/P-59 | UNKNOWN/reconciliation evidence | Timeout, ambiguous response, duplicate, out-of-order, crash/restart |
| NFR-AUD-001 | Master §7/§12; ENG-LOG-001; SEC-001 | P-05, P-49, P-51, P-60/P-61 | Append-only audit/log/evidence | Redaction, immutable-history, correlation and audit completeness |
| NFR-SAFE-001 | Master §5/§7; ADR-0007/0012 | P-02, P-11, P-29, P-31..P-35, P-59 | No AI/venue bypass; UNKNOWN safe state | Negative import/path, no-blind-retry, lease/CAS, safe-state tests |
| NFR-SEC-001 | SEC-001/002; DATA-OPS-001 | P-49..P-56, P-60 | Access, secrets, roles, migration safety | Role denial, secret scan, DB grant, threat and recovery reports |
| NFR-OPS-001 | OPS-001; OPS-RUN-001; ENG-TEST-001 | P-52/P-53, P-56, P-59, P-62 | Signals/runbooks/evidence | Alert mapping, drill report, no-skip quality evidence |

## Required evidence linkage

Every implementation commit must link:

`requirement → approved ADR/contract → task-card path → test name → evidence artifact → reviewer decision`.

An unlinked code path is not accepted as Enterprise-Grade even if tests pass.

## Unresolved traceability

- DOM-RISK-001 remains DRAFT as normative document; local profile approval is recorded and task-scoped sync remains.
- DOM-MODEL-001 Fill remains DRAFT as normative document; semantics approval is recorded and sync remains.
- DATA-DICT-001/DATA-ERD-001 remain DRAFT as normative documents; task addendum review is approved and physical sync remains.
- REG-001 remains IN_REVIEW until C-CMD-002/C-EVT-002/FVENUE-1 permission is recorded.
- PostgreSQL integration evidence is absent while `DATABASE_URL` is missing.
