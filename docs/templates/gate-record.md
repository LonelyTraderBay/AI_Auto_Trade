# Template — Gate Record

| Thuộc tính | Giá trị |
|---|---|
| Document ID | TMP-GATE-001 |
| Artifact type | Reusable gate-record template |
| Phiên bản | 0.1.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §0.1, §14.2, §15.3 và Phụ lục C.4 |
| Related requirements | NFR-AUD-001, NFR-SAFE-001, NFR-OPS-001, SEC-AUD-001 |
| Related ADR | Theo phase/gate cụ thể |

> Copy template này vào docs/evidence/gates/phase-N/<GATE_ID>.md. Không có evidence thì gate là FAIL. Một gate record DRAFT/IN_REVIEW không mở phase tiếp theo.

---

# GATE-<PHASE>-<NNN> — <Tên gate>

| Thuộc tính | Giá trị |
|---|---|
| Gate ID | GATE-<PHASE>-<NNN> |
| Phase | <0.0 / 0 / 1 / ...> |
| Record version | 0.1.0 |
| Status | DRAFT / IN_REVIEW / APPROVED / REVOKED |
| Scope | <venue/account/instrument/strategy/environment hoặc documentation scope> |
| Environment | <local/fake/paper/testnet/canary; no secret> |
| Deployment/config manifest hash | <hash or N/A> |
| Owner / runner | <role/actor> |
| Required approver | <role/actor> |
| Started / completed UTC | <timestamps> |
| Related requirements | <FR/NFR/SEC IDs> |
| Related ADR/task/contract | <IDs and canonical paths> |

## 1. Entry conditions

| ID | Condition | Evidence path/hash | Result |
|---|---|---|---|
| EC-001 | <condition from master/ADR/task> | <path/hash> | PASS / FAIL / N/A |

Entry condition marked FAIL blocks execution/approval of this gate.

## 2. Procedure and result

| Step | Exact command/procedure | Runner | Start/end UTC | Expected result | Actual result | Artifact/evidence |
|---|---|---|---|---|---|---|
| 1 | <exact command or runbook procedure> | <actor/role> | <UTC> | <observable result> | <actual result> | <path/hash> |

Commands must be copied exactly, with exit result or equivalent procedure evidence. Do not write “tested successfully” without data.

## 3. Requirement and invariant coverage

| Requirement / invariant | Test/procedure | Result | Evidence |
|---|---|---|---|
| <FR/NFR/SEC/ADR invariant> | <test/drill/review> | PASS / FAIL | <path/hash> |

## 4. Incident, exception and waiver

| Field | Value |
|---|---|
| Incident / anomaly ID | <none or ID> |
| Description and affected scope | <text> |
| Immediate safe state | <FREEZE/BLOCKED/disabled/etc.> |
| Waiver ID and expiry | <none or approved waiver; safety invariant cannot be waived> |
| Compensating control | <text> |
| Follow-up task / RAID link | <TASK/RAID ID> |

## 5. Decision

| Field | Value |
|---|---|
| Decision | PASS / FAIL / REVOKED |
| Decision rationale | <evidence-based text> |
| Permitted next action | <specific task/phase, or none> |
| Expiry/revalidation condition | <date/condition/config/dependency change> |
| Revocation trigger | <event that invalidates gate> |

PASS only means the exact scope/version/evidence passed. It never implicitly approves more capital, venue, instrument, strategy, mode or a future phase.

## 6. Sign-off

| Role | Actor | Action | UTC timestamp | Version/hash reviewed | Evidence |
|---|---|---|---|---|---|
| Runner | <actor> | Submitted evidence | <UTC> | <hash> | <path> |
| Reviewer | <actor/role> | Reviewed | <UTC> | <hash> | <path> |
| Required approver | <actor/role> | PASS / FAIL / REVOKED | <UTC> | <hash> | <path> |

## 7. Change log

| Version | Date | Change | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | YYYY-MM-DD | Initial record draft. | <owner> | Pending |
