# SEC-004 — Secrets and key management

| Trường | Giá trị |
|---|---|
| Version / Status | 1.1.2 / IN_REVIEW |
| Owner / Approver | Security/Backup Owner / Account Owner (pending) |
| Effective date / Last review | Chưa hiệu lực / 2026-08-02 |
| Related | NFR-SEC-001, NFR-AI-001, NFR-OPS-001, SEC-KEY-001, SEC-AI-002, SEC-AI-003; ADR-0010, ADR-0015, ADR-0016; SEC-001; runbook RB-007 |
| Change summary | 1.1.2 (2026-08-02, Technical Operator soạn thay Owner, Pending): đồng bộ Last review với ngày sửa; thêm SEC-KEY-001 vào Related (policy này là acceptance evidence chính của SEC-KEY-001 theo PRD-NFR-001 §8.1); thêm "(pending)" cho Approver. 1.1.1 (2026-08-02): sửa dangling requirement ID. 1.1.0/1.0.0 (2026-07-31): quy tắc lifecycle/injection, gồm BYOK AI secret-enrollment write-only; không chọn secret provider hoặc ghi secret thực. |

## 1. Scope and prohibition

A secret includes venue/API credential, session signing material, database password, encryption/private key, webhook token and recovery credential. No secret value may be committed, printed, serialized to fixture/manifest, copied to Markdown, placed in issue/evidence, sent to AI, or exposed/read back by API/UI/log/trace.

The only narrow ingress exception is an approved BYOK AI credential enrollment: an authenticated Account Owner submits a provider key once through a transport-protected, isolated `secret_ingress` boundary that writes directly to the approved secret provider. The normal Control API command/event/audit pipeline must not receive or persist the body. The preferred path is a single-use direct-vault enrollment session; the route is `no-store`, uses no Idempotency-Key/body hash/key fingerprint, and a lost response is resolved by safe status read rather than automatic resubmit. Neither dashboard nor any API response may reveal, mask-and-return, fingerprint or otherwise recover the key.

Config/deployment holds only a schema-validated reference such as `secret_ref`, never the resolved value. Example references use non-resolvable placeholders and are not credential values.

## 2. Required lifecycle

| Stage | Required control |
|---|---|
| Request | Owner, environment, process, purpose, expiry, privilege and no-withdrawal requirement documented. |
| Provision | Security/Backup Owner uses approved provider after ADR/topology decision; unique per environment/account/process. |
| BYOK enroll | Account Owner uses approved one-time isolated write-only/no-store enrollment for an approved provider connection; secret provider returns opaque candidate binding receipt only. |
| Inject | Least-privilege runtime injection; avoid disk persistence; allowlisted bootstrap only; no business/risk override from env. |
| Use | Process-specific identity, network allowlist where supported, redacted telemetry/no raw echo and short owner/connection/revision/job lease for AI binding. |
| Rotate/revoke | Scheduled and incident-driven; immutable manifest/new instance/restart; verify safe state and reconciliation. AI candidate validates before atomic cutover; suspend/revoke invalidates new leases, rechecks before egress, zeroizes and discards revoked in-flight output. |
| Retire | Revoke/disable provider-side when supported, remove bindings under approval, retain audit metadata but never secret material. Disconnect means platform stop-use unless provider-side revoke is verified. |

Trade credential must have no withdrawal permission. `LIVE_TRADE_ONLY` is only legal for approved CANARY/FULL_LIVE manifest; `LIVE_READ_ONLY` only within master §6.1 conditions. AI worker, research worker, CI and dashboard never receive a trade credential.

## 3. Environment and process matrix

| Environment / process | Permitted credential class | Rules |
|---|---|---|
| local / CI | NONE | No real venue credential; fixture/mock only. |
| paper simulator | NONE or approved LIVE_READ_ONLY | Simulator only; no venue submission capability. |
| testnet trading-node | TESTNET_TRADE_ONLY | Testnet endpoint/account only; no runtime class change. |
| canary trading-node | LIVE_TRADE_ONLY | Approved immutable manifest, dedicated monitored host, no withdrawal. |
| data worker | Public or approved read-only only | Never trade. |
| AI/research/dashboard | NONE for venue credentials | Never receives venue trade secret. Dashboard/research never resolve AI provider secret. AI worker may resolve only an active, owner-scoped AI binding just-in-time under ADR-0016. |

No database, endpoint, account, credential or provider namespace is shared across local, CI, paper, testnet and canary. An AI provider key is additionally scoped to one approved owner connection/provider policy; it is not a shared environment variable available to all workers.

## 4. Handling and observability

- Secret scanners run in local review and CI; suspected leak is an incident, not a normal code cleanup.
- Log/trace/error/redaction has deny-by-default field policy. Raw third-party payloads are treated as sensitive until classified/redacted.
- Access/rotation events record opaque connection/binding lifecycle ID/class, actor/process/environment, reason and timestamp — never a secret-provider reference, value, token length, key hash/fingerprint or material that aids recovery.
- Backups/dumps are encrypted and access-controlled. Restore artifacts use separate authorized handling and must not be attached to tickets or prompts.

## 5. Rotation and compromise

Rotation never hot-edits a running deployment manifest or silently upgrades a credential class. Create a new approved manifest/reference, place affected runtime in safe state as required, restart/verify least privilege, run reconciliation when venue access could have been in flight, then retire old material. For BYOK, start a no-key rotation command, create a candidate opaque binding/revision through isolated enrollment, validate it with a non-trading probe, atomically activate it and then disable the old binding; candidate failure must preserve the old active binding. Never place an AI key in a deployment manifest.

On suspected compromise: contain relevant scope, activate kill switch if trading exposure exists, revoke/rotate with Security/Backup Owner, review audit/venue activity, reconcile orders/balances, preserve evidence and do not resume merely because a replacement key works. Use RB-007.

## 6. Provider decision gate

Secret-provider product, encryption hierarchy, break-glass access and production injection topology require ADR-0010/0015 or a dedicated approved ADR before external venue/canary. BYOK AI provider catalog, owner scope, secret enrollment and data-egress controls additionally require ADR-0016 and OD-008 before Phase 6. This baseline is not authorization to create or use secrets.
