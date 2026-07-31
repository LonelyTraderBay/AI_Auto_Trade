# ADR-0010 — Canary topology, backup and deployment control

| Thuộc tính | Giá trị |
|---|---|
| Status | DRAFT — required before Phase 4; no canary authorization |
| Date | 2026-07-31 |
| Owner | Security/Backup Owner |
| Approver | Account Owner |
| Related | FR-OPS-001, NFR-OPS-001, NFR-SEC-001, NFR-SAFE-001; [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §6, §7.11–§7.12, §12, §14 Phase 4; DATA-006 |
| Supersedes / superseded by | None / None |

## Context and decision drivers

Canary real capital requires reproducible deployment identity, process/credential isolation, monitoring, backup/restore and incident response. None of the required host, alert channel, backup location, capital or risk-cap choices have been supplied; a generic topology must not be mistaken for authorization.

## Proposed decision

This ADR makes no canary deployment decision now. Before Phase 4, an approved deployment record must specify: Linux container image by pinned digest; one machine identity per process; isolated canary DB/credentials; trade-only credential with withdrawal disabled; network/IP restrictions when supported; immutable validated config/deployment/strategy/risk hashes; monitoring/alert/escalation; lease/kill/reconciliation/unknown-order runbooks; encrypted backup/PITR/offsite copy and restore drill evidence.

Canary is smallest approved scope only: one approved venue/account/instrument/strategy/cap, no auto-scale, no AI direct control, no shared paper/live database or credential. Increase of capital/scope or FULL LIVE needs a separate ADR/gate.

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| Treat testnet host as canary host without changes | credential/backup/network/incident controls differ materially |
| Manual deployment/config edit | cannot reproduce/audit/rollback safely |
| Rely on backup claim without restore drill | unverified recovery is no recovery |
| Full live after paper | skips bounded real-world operational validation |

## Consequences

Canary entry is blocked until OD-004/OD-005, security/risk owner approvals and Phase 3 canary-readiness evidence are complete. Default operational safety action is freeze and reconciliation; no automatic flatten is implied. Deployment manifest/config changes produce new immutable identity, not an in-place live mutation.

## Migration, rollout and rollback/forward-fix

No deployment now. Future rollout uses an approved manifest to canary scope after restore/kill/reconciliation drills. Rollback freezes new exposure, uses audited runbook/reconciliation and restores only tested consistency set as appropriate; it does not erase orders/ledger/audit history.

## Approval criteria

- [ ] OD-004 and OD-005 resolved; named reviewers/approvers and escalation path exist.
- [ ] Backup/restore/PITR, alert, credential, network and runbook evidence pass drill.
- [ ] Phase 3 canary-readiness and Account Owner/Risk Approver gate record are signed.

