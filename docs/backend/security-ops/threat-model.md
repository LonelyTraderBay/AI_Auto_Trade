# SEC-001 — Threat model baseline

| Trường | Giá trị |
|---|---|
| Version / Status | 1.2.2 / IN_REVIEW |
| Owner / Approver | Security/Backup Owner / Account Owner (pending) |
| Effective date / Last review | Chưa hiệu lực / 2026-08-02 |
| Related | NFR-SEC-001, NFR-OPS-001, NFR-AI-001, SEC-AUTH-001, SEC-AI-002, SEC-AI-003; ADR-0007, ADR-0010, ADR-0012, ADR-0015, ADR-0016 |
| Change summary | Bổ sung T-017 (Control API DoS/resource exhaustion) và T-018 (insider/single-operator) vào threat register theo audit supplement; sửa dangling requirement ID theo audit 2026-08-02. |

## 1. Scope và security objectives

Scope bao gồm control plane, trading node, data/research/AI worker, PostgreSQL/Parquet/evidence, CI supply chain, dashboard và external venue boundary. Mục tiêu: không có lệnh trái phép/trùng, không lộ secret, risk/audit/ledger không bị bypass, mutation có actor/evidence và incident đưa runtime về safe state.

Out of scope hiện tại: chọn provider authentication/session (OD-006, ADR-0015), venue/account thật, live topology, legal/compliance locale, full-live và concrete AI BYOK catalog/vault/egress policy (OD-008, ADR-0016). Chúng là blocker cho phase liên quan, không phải assumption ngầm.

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
| AI provider key / credential binding | Restricted secret / opaque metadata | Write-only enrollment, secret provider only, owner-scope binding, no read-back/log/persist. |
| AI provider/model/endpoint catalog | Security/egress integrity | Versioned capability/adapter/endpoint/data policy allowlist; no arbitrary URL/model. |

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
| T-013 | BYOK enrollment leak, raw key/body hash/fingerprint in HTTP log/audit/event/DB/fixture/browser/proxy/WAF/APM | Provider/account takeover, billing/data exposure | One-time isolated no-store enrollment, no Idempotency-Key/body hash, secret provider, body/log suppression, no read-back, scan/redaction/rotation | Secret-leak/no-hash negative test, access audit, RB-009 drill | Security/Backup Owner |
| T-014 | Cross-owner connection use or secret-binding enumeration | Unauthorized provider use/data egress | Owner-scope authorization before existence disclosure, opaque binding, machine job scope, no shared environment key | Cross-scope authorization test, audit correlation, denied-access alert | Security/Backup Owner |
| T-015 | Arbitrary provider URL/model/proxy, DNS/redirect/private-route bypass or silent fallback | SSRF, key/data exfiltration, duplicate egress/cost | Approved catalog/endpoint profile, egress gateway hostname/SNI/TLS/DNS/redirect policy, adapter capability review, default no fallback | Endpoint/model/proxy/DNS/redirect deny test, egress audit, adapter/catalog evidence | Security + Technical |
| T-016 | Budget abuse, capability drift, provider timeout/unknown outcome or stale/revoked binding in flight | Cost exhaustion, invalid proposal, duplicated external data egress | Atomic quota reservation, model/catalog/adapter digest pin, circuit breaker, structured validation, short binding lease/recheck/zeroization, no blind retry/fallback | Usage/quota/circuit/revoke alerts, outage/budget drill, provenance test | Technical + Account Owner |
| T-017 | Control API DoS/resource exhaustion, kể cả vô ý từ script lỗi (retry loop, runaway client) | Control plane unavailable during incident; safe-state command starved | Rate limit theo master §11.3, request size/timeout limits, authorization before expensive work | Request-rate/error-rate metric per OPS-001 | Technical Operator; required before Phase 3 |
| T-018 | Insider/single-operator sai sót hoặc lạm quyền khi một người giữ nhiều role | Unauthorized/unsafe action passes as approved; audit blind spot | Dual-role recording master §1.6, independent approver for safety/security/live actions, append-only audit, second human reviewer before canary/live (no waiver) | Audit review cadence (OPS-001/master §12.8) | Security/Backup Owner; applies every phase, hard requirement from Phase 4 |

## 4. Control principles

1. Default deny, least privilege and separate human/machine identity.
2. Fail closed for risk, credentials, data freshness, lease, reconciliation and security errors.
3. Only execution context submits/cancels; direct venue replace is not MVP; AI/UI never calls venue directly.
4. Facts are append-only where audit/financial semantics require it. Evidence is retained, not rewritten.
5. Security boundaries are checked at API, process, database, network and deployment layers; one check never replaces another.
6. AI provider keys, egress and usage are independent of venue credentials/trading authority; AI failure is contained to the AI capability.

## 5. Verification plan and residual risk

Before external venue: authorization/re-auth/idempotency/error-redaction/secret scan tests, negative credential injection test, unknown-order/stream-gap/reconciliation/kill-switch/DB/restore runbook drills. Before canary: independent human reviewer, approved topology/credential/backup ADR and gate evidence.

Before Phase 6 BYOK: ADR-0008/0016 and OD-008 approved/resolved; fake-provider default test; isolated no-store/no-hash secret-enrollment/no-read-back/redaction test; owner-scope denial; provider/model/endpoint/policy-profile deny; egress/data classification and DNS/redirect/private-route deny; budget/rate/circuit; initial/rotation candidate/cutover/rollback; dual-role validation/activation; revoke lease/in-flight; outage/unknown-outcome/no-fallback; and zero-execution-tool evidence.

Residual risks such as provider choice, legal requirement, venue-specific control and operational thresholds remain `OPEN` in the relevant ADR/OD. No Phase 3/4 gate can pass on this draft alone.

## 6. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 1.2.2 | 2026-08-02 | Audit toàn diện: sửa dangling runbook ID "RB-AI-001" thành RB-009 tại T-013 (catalog chỉ có RB-001..RB-012); cập nhật Last review; sắp changelog newest-first. Thay đổi do Technical Operator thực hiện thay Owner (Security/Backup Owner). | Technical Operator (soạn thay Security/Backup Owner) | Pending |
| 1.2.1 | 2026-08-02 | Bỏ dangling ID SEC-OPS-001 khỏi Related (NFR-OPS-001 đã có sẵn) theo audit 2026-08-02. | Technical Operator | Pending |
| 1.2.0 | 2026-07-31 | Thêm T-017 (Control API DoS/resource exhaustion, kể cả vô ý) và T-018 (insider/single-operator sai sót hoặc lạm quyền) vào §3 threat register. | Technical Operator | Pending |
| 1.0.0–1.1.x | 2026-07-31 | Khởi tạo threat model T-001..T-016 (lineage chi tiết: xem git history — row bổ sung cho đủ chuỗi version). | Technical Operator | Pending |
