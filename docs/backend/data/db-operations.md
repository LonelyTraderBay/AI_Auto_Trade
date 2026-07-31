# DATA-006 — Database operations, backup and access runbook baseline

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 0.1.0 |
| Trạng thái | DRAFT — chờ Security/Backup Owner và Account Owner phê duyệt |
| Owner | Security/Backup Owner |
| Approver | Account Owner |
| Ngày soạn | 2026-07-31 |
| Liên quan | FR-OPS-001, FR-REC-001, NFR-OPS-001, NFR-AUD-001, NFR-SEC-001; ADR-0003, ADR-0010, ADR-0012, ADR-0013, ADR-0015 |
| Nguồn policy | [Master specification](../../../AI_AUTO_TRADE_MASTER_SPEC.md), §6, §7.9–§7.12, §12, §14 |

## 1. Objective and current limitation

This is an operations baseline for a PostgreSQL system of record. It contains no credential, endpoint, backup location or execution command. Those values are deliberately open until Security/Backup Owner, OD-005, OD-007 and relevant ADRs are approved. A database not demonstrated restorable is treated as having no backup.

## 2. Environment and access model

| Environment | Database/credential rule | Runtime rule |
|---|---|---|
| local development | isolated local database/credential; no live trade credential | Windows developer support only; no evidence of production readiness |
| CI | ephemeral/isolated database and test secrets only | no external venue/LLM trade path |
| paper/testnet | isolated database and credentials | Linux container/image policy when execution begins |
| canary | isolated database, encrypted backup/PITR scope and least-privilege credentials | no shared paper/live DB or credentials |

Database role scope is defined in [database standards](database-standards.md). `db_migrator` is separate from runtime identities. Break-glass access, if later approved, needs named human identity, expiry, reason, audit and post-use review; it is not authorized by this DRAFT.

## 3. Required operational state and checks

| Area | Must observe | Safe behavior on failure |
|---|---|---|
| Connectivity/capacity | database availability, connection exhaustion, disk/WAL growth, replication/backup lag | fail closed for new trading exposure; alert operator |
| Transaction health | serialization/deadlock/lock timeout rate, slow query, blocked transaction | protect transaction budget, investigate; do not widen retry blindly |
| Delivery | outbox backlog/age, claim lease expiry, DLQ count/age, inbox dedupe failures | alert; pause affected flow if audit/financial delivery unsafe |
| Integrity | ledger balance checks, projection watermark lag, event sequence gaps, migration/schema drift | block strategy/exposure in affected scope until reconcile |
| Reconciliation | active case count/age and mismatch scope | `BLOCKED` scope prevents new exposure |
| Backup/restore | latest successful backup/WAL, offsite encryption status, last restore drill | no canary gate if missing/stale/failed |

Thresholds, alert channels and escalation times require the SLO/alert policy and owner sign-off; no numeric operational threshold is invented here.

## 4. Backup, restore and consistency set

| Stage | Required procedure/evidence |
|---|---|
| Before backup policy approval | document owner, storage classification, encryption/key rotation, access, retention and restore test plan |
| Dev milestone | execute a restore test before major persistence milestone; record schema/version, result and gaps |
| Canary baseline | daily base backup, WAL/PITR, encrypted offsite copy and routine restore drill; target RPO <= 15 minutes/RTO <= 60 minutes unless new approved gate says stricter |
| Consistency set | PostgreSQL base/WAL, Parquet/catalog manifests, evidence artifact, effective config/deployment manifest, ADR/gate records needed for replay/audit |
| Restore validation | verify journal balance, rebuild projections, check outbox/inbox behavior and catalog checksum, then reconcile before strategy enable |

Restore never resumes strategy automatically. The operator first verifies environment identity, config/manifest hash, role grants, integrity/reconciliation and explicit safe-state authorization.

## 5. Migration and incident handling

Only `db_migrator` performs approved migration. Before migration: verify backup/restore point, current revision/schema snapshot, task/ADR/dictionary, lock/duration risk and forward-fix plan. During: monitor duration, lock/lag/error evidence; do not improvise destructive rollback. After: verify revision/schema, constraints/indexes/roles, compatibility tests, data counts/checksum when relevant and operation health.

For DB unavailable/corruption/suspected drift: contain (stop new exposure), preserve evidence, classify scope, restore/forward-fix under approved runbook, rebuild/reconcile and only then release safe state. Never purge audit/ledger/outbox evidence to make the incident disappear.

## 6. Logs, data protection and review cadence

Logs/traces must redact credentials and sensitive payload; diagnostic queries/exports follow least privilege and avoid raw secret/full payload. Access grant changes, backup failures, restore drills, migration incidents and break-glass actions need immutable audit records. Security/Backup Owner reviews backup/restore evidence on the cadence defined in the approved SLO/runbook policy.

## 7. Gate checklist

- [ ] Environment/database/credential boundaries are verified.
- [ ] Roles have least privilege and runtime cannot perform DDL/history delete.
- [ ] Backup consistency set and restore procedure have named owner/storage/retention policy.
- [ ] Restore drill evidence includes ledger/projection/outbox/inbox/reconciliation checks.
- [ ] Alerts/runbooks/incident ownership are approved before testnet/canary gate as applicable.

