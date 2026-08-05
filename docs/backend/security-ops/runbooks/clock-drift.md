# RB-012 — Clock drift or NTP synchronization failure

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.1 / DRAFT |
| Owner / Approver | Technical Operator / Account Owner (pending) |
| Effective date / Last review | Chưa hiệu lực / 2026-08-02 |
| Trigger / Severity | Drift alert beyond `clock_drift_threshold_ms` (new policy field, DRAFT — cần phê duyệt), NTP sync failure/unreachable time source / High; time underpins lease, idempotency and audit ordering |
| Scope / Incident commander | Affected host/process, lease/leader scope, idempotency/audit windows in the drift interval / Technical Operator |
| Related | NFR-OPS-001, NFR-SEC-001; ADR-0007; OPS-001; RB-001, RB-005; threat T-011 |
| Change summary | Fail-closed drift containment, supervised resync and time-dependent invariant verification; required before testnet (Phase 3). 1.0.1 (2026-08-02): bổ sung Owner/Approver + Effective/Last review theo GOV-DOC-001 §3 (audit toàn diện). |

## Safe-state objective

No submission decision, lease claim or idempotency judgment is made on untrusted local time. Drift is measured against a trusted source before any correction, and the clock is never stepped by a large jump under a live lease holder — a stepped clock can expire or extend a lease incorrectly and break fencing.

## Procedure

1. Measure actual drift against a trusted reference source (approved NTP servers, cross-checked); record per-host offset, direction, drift rate and the alert window. Do not trust a single local reading.
2. If measured drift exceeds `clock_drift_threshold_ms` (policy field, DRAFT — cần phê duyệt): block new order submission for the affected scope (fail closed). Keep read and reconciliation paths available; their outputs are evidence, not resume authorization.
3. Resync NTP under supervision — decision point:
   - Small drift within slew range: let the daemon slew gradually; monitor convergence.
   - Large drift: do NOT step the clock while the process holds an execution lease. Resync first, then restart the trading node under RB-005 so lease/fencing state is rebuilt on trusted time.
4. Verify time-dependent invariants after resync: lease TTL/heartbeat consistency (one leader, no lease that outlived its TTL during the drift window), idempotency key expiry windows (keys that expired/survived incorrectly), and timestamp ordering of recent audit/event records across the drift interval. Flag any record whose ordering is ambiguous.
5. Resume submission only after reconciliation for the affected scope is clean and step 4 shows no unresolved inconsistency. A synced clock alone is not resume authorization.

## Verify and resume

Evidence must show drift back within policy from independent measurement, NTP sync healthy and monitored, lease/leader state rebuilt on trusted time, no idempotency window violated with external effect and clean reconciliation. Technical Operator resumes; Risk Approver is required if any order-lifecycle ambiguity was found in step 4.

## Escalation and evidence

Escalate to Critical for suspected deliberate clock manipulation (T-011), a lease/fencing violation discovered in the drift window, duplicate external effect traced to idempotency expiry or drift that cannot be corrected within policy deadline. Retain drift measurements with source, resync method and timing, restart/lease evidence, invariant verification results and reconciliation output. This runbook must be drilled before testnet (Phase 3).
