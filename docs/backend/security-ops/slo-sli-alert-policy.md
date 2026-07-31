# OPS-001 — SLI, SLO and alert policy baseline

| Trường | Giá trị |
|---|---|
| Version / Status | 1.2.0 / DRAFT |
| Owner / Approver | Security/Backup Owner / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | NFR-OPS-001, NFR-SEC-001, NFR-AI-001, SEC-OPS-001, SEC-AI-002, SEC-AI-003; ADR-0007, ADR-0010, ADR-0012, ADR-0016; runbooks RB-001–RB-012 |
| Change summary | Bổ sung escalation logic (DRAFT), policy fields `slow_query_threshold_ms`/`alert_ack_timeout_s`/`clock_drift_threshold_ms`, dashboard views bắt buộc trước testnet (DRAFT) và weekly audit-event review. |

## 1. Principles

This is a design baseline, not evidence of achieved availability. Every SLO/threshold is versioned operations/risk policy input with owner, effective date, environment/scope and review cadence. Missing, invalid or stale policy fails closed for the related capability.

Alert severity is based on safety/integrity first, then availability. Alert suppression must be time-bounded, audited and cannot suppress a safety invariant breach.

## 2. Required signals

| Signal / SLI | Measurement | Breach behavior | Initial severity |
|---|---|---|---|
| Market/private stream freshness | `now - received_at`; gap/reconnect count | Block new exposure when stale/untrusted | High; Critical when safety gate breached |
| Submit-to-ack, ack-to-fill | Histograms by venue/instrument/mode | Investigate latency; unknown outcome enters reconcile | Medium/High |
| Unknown order age | `UNKNOWN` start to resolved | No blind retry; escalate at `unknown_order_sla_s` | Critical after SLA |
| Reconciliation mismatch age/count | Mismatch creation to resolution | Freeze affected new exposure | High/Critical by scope |
| Risk rejection/bypass indicator | Decision/reason and invariant monitor | Any bypass is incident/safe state | Critical |
| Ledger imbalance attempt | Deferred check/reconciliation result | Stop affected financial processing | Critical |
| Lease/fencing health | Heartbeat, leader count, clock drift | Block submission on lost/ambiguous lease | Critical |
| Outbox/inbox/DLQ backlog | Queue age/count, duplicate rate | Backpressure/triage; no silent drop | Medium/High |
| DB health | Connections, lock wait, disk, backup age | Fail closed; use RB-006 | High/Critical |
| Security/credential events | Denied dangerous action, scan leak, rotation failure | Contain/revoke/escalate | High/Critical |
| AI connection lifecycle | Initial/rotation enrollment, validation/activation/suspend/revoke/expiry and lease-invalidation propagation by safe status code | Disable failed connection; investigate only within owner scope | Low/Medium; High for suspected key leak or failed revoke |
| AI provider egress/capability | Denied provider/model/endpoint/data-egress policy, catalog capability drift | Deny request; review catalog/policy; no provider fallback | Medium; High for suspected unauthorized egress |
| AI budget/quota/rate/circuit | Reservation denial, actual usage, quota/rate breach, latency/timeout, circuit state, unknown outcome | Block AI request/connection per policy; trading unaffected | Low/Medium |
| AI output validation | Structured schema/provenance validation failure | Reject proposal/memory write; retain safe metadata | Low/Medium |
| Runbook/restore drill | Latest evidence age/result | Gate is blocked if required drill stale/fails | High |

## 3. Operational policy fields

The following values must be present in a validated operations/risk policy before their runtime feature starts: `market_data_max_age_ms`, `private_stream_max_age_ms`, `reconciliation_interval_s`, `unknown_order_sla_s`, `lease_ttl_s`, `heartbeat_interval_s`, retry/circuit-breaker bounds, `alert_deadline_s`, `slow_query_threshold_ms`, `alert_ack_timeout_s`, `clock_drift_threshold_ms`, backup/retention/restore-drill cadence and daily-loss reset timezone. Phase 6 additionally requires owner/connection/provider/model/environment/purpose-scoped AI daily/monthly budget, concurrency, RPM/TPM, maximum tokens, timeout, validation probe limit, circuit thresholds, egress-denial alert policy, binding-lease/cache TTL and suspend/revoke propagation SLA.

Values are deliberately not invented in this document. Owner approval and runtime evidence are required before paper/testnet/canary. A metric label must not include raw secret, free-form user PII or unbounded-cardinality IDs.

## 4. Severity and response

| Severity | Definition | Response deadline and owner |
|---|---|---|
| Critical | Safety/integrity breach or unknown exposure beyond policy | Immediate safe state, incident commander, runbook; Account/Risk/Security escalation as scope requires. |
| High | Reconciliation/data/DB/security condition that can become unsafe | Acknowledge/respond within approved `alert_deadline_s`; contain affected scope. |
| Medium | Degraded latency/quality/backlog with safety gate still holding | Triage within policy, evidence and trend review. |
| Low | Research/AI/non-trading degradation | Track and review; never hides trading alert. AI key leak or unauthorized egress is reclassified High/Critical, not Low. |

Notification channel, escalation roster and paging integration are OD-005/operations decisions before Phase 3. No alert integration is created by this draft.

### 4.1 Escalation logic (DRAFT — channel/roster là OD-005)

- Critical: primary responder (Technical Operator) → nếu không ack trong `alert_ack_timeout_s` (policy field mới, §3) → Security/Backup Owner → Account Owner.
- High: primary responder → fallback sang Security/Backup Owner sau 2× `alert_ack_timeout_s`.
- Medium/Low: ghi nhận vào review cadence (§5); không page.

Mọi alert Critical chưa được ack là blocker cho submission mới nếu alert liên quan execution/ledger path (fail-closed). Kênh thông báo, roster và paging integration cụ thể là OD-005; logic này chưa hiệu lực cho tới khi OD-005 được chốt — DRAFT, cần phê duyệt.

### 4.2 Dashboard views bắt buộc trước testnet (DRAFT — cần phê duyệt)

Trước testnet, dashboard/operations view tối thiểu phải hiển thị: `UNKNOWN` orders và tuổi của từng order; reconciliation queue/case đang mở; lease/leader state; outbox/inbox/DLQ backlog (count và age); kill-switch state theo từng scope; backup age và last restore drill; AI budget/egress (Phase 6). Thiếu view bắt buộc là gap đối với testnet gate evidence.

## 5. Evidence and review

Dashboard/alert output must carry environment, deployment/manifest hash when applicable, scope, metric window, threshold/policy version, correlation/incident ID and safe-state action. AI alerts may include provider/model/catalog/connection revision and safe normalized status/usage, but never key, secret reference, authorization header, raw prompt/response or raw vendor payload. Review per master §12.8: every deploy, daily while runtime runs, weekly health/security/backup age, weekly audit-event review by Security/Backup Owner, monthly drill/rotation trend, and after critical incident.

## 6. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 1.2.0 | 2026-07-31 | Thêm §4.1 escalation logic (DRAFT, roster/channel là OD-005) với `alert_ack_timeout_s` và fail-closed cho Critical chưa ack trên execution/ledger path; thêm `slow_query_threshold_ms`, `alert_ack_timeout_s`, `clock_drift_threshold_ms` vào §3; thêm §4.2 dashboard views bắt buộc trước testnet (DRAFT); thêm weekly audit-event review by Security/Backup Owner vào §5. | Technical Operator | Pending |
