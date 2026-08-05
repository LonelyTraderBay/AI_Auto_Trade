# RB-006 — Database unavailable, disk full or integrity failure

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.1 / DRAFT |
| Owner / Approver | Technical Operator + Security/Backup Owner / Account Owner (pending) |
| Effective date / Last review | Chưa hiệu lực / 2026-08-02 |
| Trigger / Severity | Database unavailable, connection/lock exhaustion, disk threshold, replication/backup failure, integrity/ledger check failure / High; Critical for unsafe or financial/audit impact |
| Scope / Incident commander | Affected environment/database/processes / Technical Operator + Security/Backup Owner |
| Related | NFR-OPS-001, NFR-SEC-001; ADR-0003, ADR-0011, ADR-0012, ADR-0013; RB-005, RB-008 |
| Change summary | Fail-closed procedure; no destructive database action. 1.0.1 (2026-08-02): bổ sung Owner/Approver + Effective/Last review theo GOV-DOC-001 §3 (audit toàn diện). |

## Safe-state objective

Stop new state-changing submission when durable state/audit cannot be guaranteed. Treat in-flight external operations as `UNKNOWN`; preserve evidence and recover with forward-fix or isolated restore, never ad-hoc destructive commands.

## Procedure

1. Open incident; record environment/database identity (not password/connection string), symptom, health metrics, disk/lock/connection state, affected processes and last known transaction/outbox/lease evidence.
2. Block strategy enable/new submission and prevent unsafe retry. If execution was in flight, follow RB-001 and RB-005. Do not restart repeatedly, truncate queues, manually edit orders/ledger or run unreviewed SQL.
3. Determine class: connectivity/network, capacity/disk, lock/deadlock, database process, schema/migration mismatch, backup/WAL/PITR issue or integrity/ledger/audit anomaly. Contain only within approved infrastructure procedure.
4. Restore database availability using least-destructive approved action. If restore is considered, use RB-008: isolated restore/verification before any production decision. Financial/audit recovery defaults to forward-fix or tested restore, not downgrade.
5. On recovery, validate database role/connectivity, schema/migration revision, transaction health, outbox/inbox backlog, audit append-only checks, ledger balance checks and backup status. Run startup/periodic reconciliation before unblocking execution.

## Verify and resume

Verify durable writes/audit work under approved test, no lost/duplicated command/event effect, one lease leader, database disk/connection/lock metrics within policy, backup/PITR status known and account/order/fill/balance reconciliation completed. Security/Backup Owner and required risk/operator role approve resume based on scope.

## Escalation and evidence

Immediate Critical escalation for data corruption, ledger imbalance, audit tampering, unknown external order, unrecoverable disk exhaustion or failed restore verification. Preserve incident timeline, diagnostic hashes/metrics, migration revision, backup set ID, commands and post-recovery reconciliation evidence. Never attach database dump or secrets to the record.

