# SEC-001 — Threat model baseline

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.0 / IN_REVIEW |
| Owner / Approver | Security/Backup Owner / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | NFR-SEC-001, NFR-OPS-001, SEC-AUTH-001, SEC-OPS-001; ADR-0007, ADR-0010, ADR-0012, ADR-0015 |
| Change summary | Threat baseline cho Phase 0.0; không chọn authentication provider hoặc topology production. |

## 1. Scope và security objectives

Scope bao gồm control plane, trading node, data/research/AI worker, PostgreSQL/Parquet/evidence, CI supply chain, dashboard và external venue boundary. Mục tiêu: không có lệnh trái phép/trùng, không lộ secret, risk/audit/ledger không bị bypass, mutation có actor/evidence và incident đưa runtime về safe state.

Out of scope hiện tại: chọn provider authentication/session (OD-006, ADR-0015), venue/account thật, live topology, legal/compliance locale và full-live. Chúng là blocker cho phase liên quan, không phải assumption ngầm.

## 2. Asset, trust boundary và safe state

| Asset | Classification | Boundary / required protection |
|---|---|---|
| Venue trade credential | Restricted | Chỉ trading node của mode được phép; no withdrawal; secret provider/injection; never log. |
| Control command/approval/audit | Sensitive integrity | Authenticated actor, RBAC, idempotency, immutable audit, re-auth for dangerous action. |
| Order/fill/ledger/risk data | High integrity | Context ownership, append-only facts, transaction/lock policy, reconciliation. |
| Deployment/config manifest | High integrity | Schema-validated, hash, immutable, approved; secret reference only. |
| Market/reference data | Integrity/availability | Quality flags, checksum, freshness/gap gates, provenance. |
| CI artifact/dependency | Supply-chain integrity | Lock/digest/SBOM/scan/review; no external trade operation. |
| AI memory/prompt/output | Untrusted data | Sanitized projection, structured schema validation, no execution credential/tool. |

Safe state nghĩa là strategy disabled/frozen, submission blocked, risk/kill-switch/reconciliation state preserved, no blind retry, forensic evidence retained. Safe state không tự xóa/cancel venue order khi outcome chưa biết.

## 3. Threat register

| ID | Threat / attack path | Impact | Mandatory controls | Detection / evidence | Owner |
|---|---|---|---|---|---|
| T-001 | API key theft, source/log/fixture leak | Unauthorized trade/read | Environment-scoped least privilege, no withdrawal, secret refs only, scan/redaction/rotation | Secret scan, access audit, credential-rotation runbook | Security/Backup Owner |
| T-002 | Unauthorized command, deployment or risk bypass | Loss / unsafe execution | Authn/RBAC, immutable audit, re-auth, task/gate approval, no UI-only confirmation | Authorization tests, audit chain, access-control matrix | Security + Risk |
| T-003 | Duplicate/replayed request or venue event | Duplicate trade/ledger effect | ClientOrderId, HTTP idempotency scope/hash, inbox/event dedupe, immutable fills | Idempotency/property tests, duplicate event alerts | Technical Operator |
| T-004 | Timeout/disconnect followed by blind retry | Duplicate/unknown exposure | Persist attempt before HTTP; state UNKNOWN; reconciliation only | Unknown-order SLO, incident/runbook evidence | Technical + Risk |
| T-005 | Poisoned/stale market or reference data | Bad pricing/risk decision | Provenance, checksum, quality/freshness gate, capability/reference version | Gap/stale metrics, feed runbook | Technical Operator |
| T-006 | Database tampering, migration error, data loss | Audit/ledger corruption | DB roles, append-only enforcement, reviewed migration, backup/PITR/restore drill | Audit hash, migration report, restore evidence | Security/Backup Owner |
| T-007 | Split-brain execution leader / stale lease | Parallel submit | Lease/fencing, single leader, loss -> UNKNOWN/block submit | Lease heartbeat/fencing metric, restart drill | Technical Operator |
| T-008 | Dashboard session theft / CSRF | Dangerous control action | Provider-neutral session policy, CSRF/session expiry, re-auth, audit reason | Auth tests, session/re-auth audit | Security/Backup Owner |
| T-009 | Prompt injection / memory poisoning | Unsafe proposal or data exfiltration | Treat inputs as data, sanitize/redact, output schema, no tool/credential, human review | Validation failure, provenance/review record | Technical + AI owner |
| T-010 | Malicious/vulnerable dependency or build artifact | Code compromise | Lock pinning, license/vuln/SAST/secret scan, SBOM/digest, review | CI artifact scan, checksum mismatch | Technical Operator |
| T-011 | Clock manipulation / non-determinism | Wrong expiry/replay/audit | Injected Clock/RandomSource, UTC, NTP/clock-drift alert, persisted seed | Replay result, drift metric | Technical Operator |
| T-012 | Alert/runbook/backup failure during incident | Prolonged unsafe state | SLO policy, tested runbooks, restore drills, escalation ownership | Drill report, incident closure evidence | Security/Backup Owner |

## 4. Control principles

1. Default deny, least privilege and separate human/machine identity.
2. Fail closed for risk, credentials, data freshness, lease, reconciliation and security errors.
3. Only execution context submits/cancels; direct venue replace is not MVP; AI/UI never calls venue directly.
4. Facts are append-only where audit/financial semantics require it. Evidence is retained, not rewritten.
5. Security boundaries are checked at API, process, database, network and deployment layers; one check never replaces another.

## 5. Verification plan and residual risk

Before external venue: authorization/re-auth/idempotency/error-redaction/secret scan tests, negative credential injection test, unknown-order/stream-gap/reconciliation/kill-switch/DB/restore runbook drills. Before canary: independent human reviewer, approved topology/credential/backup ADR and gate evidence.

Residual risks such as provider choice, legal requirement, venue-specific control and operational thresholds remain `OPEN` in the relevant ADR/OD. No Phase 3/4 gate can pass on this draft alone.

