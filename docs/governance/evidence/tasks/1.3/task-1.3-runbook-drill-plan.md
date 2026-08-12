# Task 1.3 — Recovery and runbook drill plan

| Trường | Giá trị |
|---|---|
| Document ID | GOV-TASK-1.3-RUNBOOK-DRILLS-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | APPROVED FOR TASK 1.3 DRILL DESIGN — execution evidence pending |
| Parent | [Enterprise control closure matrix](enterprise-control-closure-matrix.md) |

## Drill matrix

| Drill | Injected condition | Safe behavior bắt buộc | Evidence |
|---|---|---|---|
| RB-1 Unknown order | Timeout/ambiguous fake venue response | Persist UNKNOWN; stop blind retry; open reconciliation case | Timeline, order/attempt/event IDs, operator decision |
| RB-2 Duplicate response | Same response delivered twice | Dedupe; no duplicate fill/order side effect | Request hash, response sequence and dedupe result |
| RB-3 Out-of-order fill | Sequence lower/higher arrives incorrectly | Reject/quarantine according to contract; preserve evidence | Event sequence report and reconciliation status |
| RB-4 Leader lease loss | Fencing token becomes stale mid-flow | Stop claim/submit; stale owner cannot mutate current state | Lease/fencing log and safe-state transition |
| RB-5 Database unavailable | Connection refused/transaction timeout | Block new exposure; preserve committed evidence; no unsafe retry | DB error, state snapshot, recovery steps |
| RB-6 Crash after commit | Process stops after durable intent/attempt commit | Restart resumes from durable state; no duplicate side effect | Before/after snapshot and replay result |
| RB-7 Crash before commit | Process stops before pre-submit commit | No externally visible submit; intent remains auditable or is safely rejected | Transaction outcome and audit trail |
| RB-8 Migration forward-fix | Approved schema defect in test database | Preserve history; apply reviewed forward-fix; verify compatibility | Revision/hash, lock duration, row/count/checksum result |
| RB-9 Secret/log probe | Inject secret-like text in request/reason/fixture | Redact/reject; no storage/log/evidence leakage | Secret scan and redaction report |
| RB-10 Kill switch | Scope freeze activated | Reject new exposure; preserve unknown/reconciliation; no auto flatten | Kill-switch audit, denied submit and recovery readiness |

## Drill execution rules

1. Run only against isolated local/ephemeral PostgreSQL and fake venue.
2. Pin UTC clock, seed, scenario revision, fixture hash and commit SHA.
3. No real venue/network/credential or production data.
4. Record command, operator role, start/end UTC, injected fault, expected/actual state and artifact path.
5. A failed drill blocks Task 1.3 review; no waiver for safety invariants.
6. Recovery never resumes strategy automatically; explicit safe-state release is separate human action.

## Required reviewers

- Technical Operator: execution and evidence.
- Account Owner: scope/recovery decision.
- Risk Approver: risk/kill-switch/reservation/UNKNOWN behavior.
- Security/Backup Owner: secret, access, backup/restore and incident evidence when applicable.
