# Task 1.3.1 — Evidence secret-redaction cleanup approval

| Field | Value |
|---|---|
| Document ID | GOV-TASK-1.3.1-APPROVAL-20260813 |
| Scope | Redact one credential-like DSN from historical Task 0.3 evidence only |
| Account Owner decision | APPROVED — user confirmation in this session |
| UTC timestamp | 2026-08-13T13:27:48Z |
| Canonical card | `tasks/active/1.3.1-evidence-secret-redaction.yaml` |
| Current state | BLOCKED pending Security/Backup Owner role action, clean branch and branch precondition |

## Approval boundary

This approval authorizes preparation and review of the scoped cleanup task. It
does not authorize changing the target file on the current Task 1.3 branch,
does not approve a secret value, and does not waive the required redaction,
hash/provenance, branch or reviewer controls.

## Required next role action

Security/Backup Owner must record a separate role action before the target file
is edited. The same human may hold both roles only if the two role actions are
recorded separately, as required by the repository governance rules.
