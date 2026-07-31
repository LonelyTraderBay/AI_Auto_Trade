# OPS-002 — Runbook index

| Trường | Giá trị |
|---|---|
| Version / Status | 1.2.0 / IN_REVIEW |
| Owner / Approver | Security/Backup Owner / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | NFR-OPS-001, NFR-AI-001, SEC-OPS-001, SEC-AI-002, SEC-AI-003; OPS-001; master §12.6–§12.8 |
| Change summary | Bổ sung RB-010 venue rate-limit/ban, RB-011 outbox/DLQ backlog, RB-012 clock drift vào catalog theo audit supplement. |

## 1. Use policy

Runbooks are controlled operational procedures. They do not authorize a command beyond RBAC, task/gate state or environment policy. Never enter secret values in a runbook, evidence or incident ticket. If a command/endpoint is not implemented or authorization is unavailable, keep/enter safe state and escalate rather than improvising.

Each drill/incident evidence records runbook ID/version, UTC timeline, scope, actor/active role, command/result, correlation/incident IDs, manifest/config hash when applicable, safe-state proof, verification and approval to resume.

## 2. Runbook catalog

| ID | File | Trigger / safe objective | Primary owner | Required before |
|---|---|---|---|---|
| RB-001 | `runbooks/unknown-order.md` | Submit/cancel outcome unknown; no blind retry | Technical Operator + Risk Approver | Paper |
| RB-002 | `runbooks/stream-gap.md` | Public/private stream gap/stale; block affected exposure | Technical Operator | Paper |
| RB-003 | `runbooks/reconciliation-mismatch.md` | Internal/venue mismatch; freeze affected scope | Technical Operator + Risk Approver | Paper |
| RB-004 | `runbooks/kill-switch.md` | Activate/release kill switch safely | Technical Operator / Risk + Account for release | Paper |
| RB-005 | `runbooks/trading-node-restart.md` | Crash/restart/lease ambiguity; no duplicate submit | Technical Operator | Paper |
| RB-006 | `runbooks/database-unavailable.md` | DB unavailable/disk/lock failure; fail closed | Technical + Security/Backup Owner | Paper |
| RB-007 | `runbooks/credential-rotation.md` | Revocation/rotation/suspected compromise | Security/Backup Owner | Testnet; canary refresh |
| RB-008 | `runbooks/backup-restore.md` | Restore/rollback/recovery evidence | Security/Backup Owner | Paper; canary refresh |
| RB-009 | `runbooks/ai-provider-connection-incident.md` | AI key compromise/revoke, provider outage/budget/egress incident; disable AI only | Security/Backup Owner + Account Owner | Phase 6 |
| RB-010 | `runbooks/venue-rate-limit.md` | Venue 429/418, IP/key ban; pause submission, staged resume, no reflexive rotation | Technical Operator | Testnet (Phase 3 external-venue Go/No-Go drill, master §14) |
| RB-011 | `runbooks/outbox-dlq-backlog.md` | Outbox relay stuck/DLQ overflow with healthy DB; no silent drop, idempotent replay only | Technical Operator | Paper (Phase 2) |
| RB-012 | `runbooks/clock-drift.md` | Clock drift/NTP failure; fail-closed submission, supervised resync, verify lease/idempotency/audit | Technical Operator | Testnet (Phase 3) |

## 3. Common stop/escalate rules

Stop and escalate immediately for duplicate/unapproved order, risk bypass, unresolved unknown/reconciliation condition, missing audit chain, stale data submitted to venue, failed kill switch, compromised credential, ledger imbalance, split-brain or backup/restore integrity failure. For AI BYOK, disable the affected AI connection and block egress on suspected key leak, unauthorized endpoint/egress or cross-owner access; do not treat it as an automatic trading stop unless an independent trading control is affected. Do not resume strategy based on a dashboard green state alone; the relevant verification section and required approver decide.

## 4. Drill cadence

Runbooks are dry-run/reviewed before paper. While paper/testnet/canary is active: execute required drills and review at the cadence in OPS-001/master §12.8; retain evidence. A runbook with stale/failing evidence blocks the applicable gate.

## 5. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 1.2.0 | 2026-07-31 | Thêm RB-010 (venue rate-limit/IP-ban/key-ban), RB-011 (outbox/DLQ backlog), RB-012 (clock drift/NTP failure) vào catalog với owner, trigger và required-before phase. | Technical Operator | Pending |
