# SEC-004 — Secrets and key management

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.0 / IN_REVIEW |
| Owner / Approver | Security/Backup Owner / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | NFR-SEC-001, SEC-OPS-001; ADR-0010, ADR-0015; SEC-001; runbook RB-007 |
| Change summary | Quy tắc lifecycle và injection; không chọn secret provider hoặc ghi secret thực. |

## 1. Scope and prohibition

A secret includes venue/API credential, session signing material, database password, encryption/private key, webhook token and recovery credential. No secret value may be committed, printed, serialized to fixture/manifest, copied to Markdown, placed in issue/evidence, sent to AI, or exposed by API/UI/log/trace.

Config/deployment holds only a schema-validated reference such as `secret_ref`, never the resolved value. Example references use non-resolvable placeholders and are not credential values.

## 2. Required lifecycle

| Stage | Required control |
|---|---|
| Request | Owner, environment, process, purpose, expiry, privilege and no-withdrawal requirement documented. |
| Provision | Security/Backup Owner uses approved provider after ADR/topology decision; unique per environment/account/process. |
| Inject | Least-privilege runtime injection; avoid disk persistence; allowlisted bootstrap only; no business/risk override from env. |
| Use | Process-specific identity, network allowlist where supported, redacted telemetry and no raw echo. |
| Rotate/revoke | Scheduled and incident-driven; immutable manifest/new instance/restart; verify safe state and reconciliation. |
| Retire | Revoke provider-side, remove references under approval, retain audit metadata but never secret material. |

Trade credential must have no withdrawal permission. `LIVE_TRADE_ONLY` is only legal for approved CANARY/FULL_LIVE manifest; `LIVE_READ_ONLY` only within master §6.1 conditions. AI worker, research worker, CI and dashboard never receive a trade credential.

## 3. Environment and process matrix

| Environment / process | Permitted credential class | Rules |
|---|---|---|
| local / CI | NONE | No real venue credential; fixture/mock only. |
| paper simulator | NONE or approved LIVE_READ_ONLY | Simulator only; no venue submission capability. |
| testnet trading-node | TESTNET_TRADE_ONLY | Testnet endpoint/account only; no runtime class change. |
| canary trading-node | LIVE_TRADE_ONLY | Approved immutable manifest, dedicated monitored host, no withdrawal. |
| data worker | Public or approved read-only only | Never trade. |
| AI/research/dashboard | NONE | Never receives venue trade secret. |

No database, endpoint, account, credential or provider namespace is shared across local, CI, paper, testnet and canary.

## 4. Handling and observability

- Secret scanners run in local review and CI; suspected leak is an incident, not a normal code cleanup.
- Log/trace/error/redaction has deny-by-default field policy. Raw third-party payloads are treated as sensitive until classified/redacted.
- Access/rotation events record secret reference ID/class, actor/process/environment, reason and timestamp — never value, token length or material that aids recovery.
- Backups/dumps are encrypted and access-controlled. Restore artifacts use separate authorized handling and must not be attached to tickets or prompts.

## 5. Rotation and compromise

Rotation never hot-edits a running deployment manifest or silently upgrades a credential class. Create a new approved manifest/reference, place affected runtime in safe state as required, restart/verify least privilege, run reconciliation when venue access could have been in flight, then retire old material.

On suspected compromise: contain relevant scope, activate kill switch if trading exposure exists, revoke/rotate with Security/Backup Owner, review audit/venue activity, reconcile orders/balances, preserve evidence and do not resume merely because a replacement key works. Use RB-007.

## 6. Provider decision gate

Secret-provider product, encryption hierarchy, break-glass access and production injection topology require ADR-0010/0015 or a dedicated approved ADR before external venue/canary. This baseline is not authorization to create or use secrets.

