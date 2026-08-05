# RB-011 — Outbox relay stuck or DLQ backlog with healthy database

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.2 / DRAFT |
| Owner / Approver | Technical Operator / Account Owner (pending) |
| Effective date / Last review | Chưa hiệu lực / 2026-08-02 |
| Trigger / Severity | Outbox backlog/dead-letter count or age beyond OPS-001 signal threshold, publisher making no progress while the database itself is healthy / Medium; High as backlog age grows or execution/ledger consumers are affected |
| Scope / Incident commander | Affected outbox publisher, partition/consumer scope, dead-letter set / Technical Operator |
| Related | NFR-AUD-001, NFR-OPS-001; ADR-0003, ADR-0011; OPS-001; RB-005, RB-006 |
| Change summary | Triage procedure for stuck relay/poison message/DLQ overflow; no silent drop, no manual payload edit; sửa dangling requirement ID theo audit 2026-08-02. 1.0.2 (2026-08-02): bổ sung Owner/Approver + Effective/Last review theo GOV-DOC-001 §3 (audit toàn diện). |

## Safe-state objective

No event is silently dropped, reordered within a `partition_key` or replayed through a non-idempotent path. The durable outbox/dead-letter record is the evidence; triage classifies and moves records under audit, it never rewrites them.

## Procedure

1. Confirm the database is actually healthy (connections, disk, locks, transaction health). If it is not, this is RB-006, not this runbook.
2. Classify the stall — decision point:
   - Publisher dead or lease/leader problem: publisher process crashed, heartbeat stale, lease held by a stale holder. Recover the publisher via approved restart (RB-005 for trading-node scope); do not run two publishers against one partition.
   - Poison message: the same head message fails repeatedly and blocks the partition.
   - Slow consumer: publisher progresses but downstream lag grows.
3. Poison message handling: inspect the redacted/sanitized payload projection only; never edit the payload in place. Move it to `dead_letters` with an explicit reason code and correlation ID so the partition can progress. Manual payload repair in the outbox table is prohibited.
4. DLQ triage: every dead letter must reach exactly one classified outcome — resolve (root cause fixed, no replay needed), replay or discard. Replay goes only through the idempotent consumption path (dedupe by event/message ID). Discard requires explicit approval and an audit record with reason; silent drop violates OPS-001. Backlog left unclassified beyond policy age escalates severity.
5. Large but healthy backlog: increase batch size/poll rate only within approved config bounds (versioned config change, not a live hand-edit) and never bypass ordering within a `partition_key` to drain faster.
6. Close with root cause (publisher fault, poison payload origin, consumer capacity), backlog drain evidence and an explicit review of whether the OPS-001 backlog/age thresholds need adjustment.

## Verify and resume

Evidence must show backlog age/count back under threshold, zero unclassified dead letters for the incident scope, replayed events proven idempotent (no duplicate downstream effect), partition ordering preserved and exactly one active publisher/lease holder. Technical Operator confirms; Security/Backup Owner joins if audit/ledger events were in the affected set.

## Escalation and evidence

Escalate High/Critical if execution or ledger consumers are starved, a dead letter contains an order-lifecycle event whose external effect is uncertain (then also RB-001/RB-003), or any evidence of dropped/duplicated effect appears. Retain queue depth/age metrics over the incident window, dead-letter IDs with classification and approver, replay/discard audit records and the config revision used to drain. This runbook must be drilled before paper (Phase 2).
