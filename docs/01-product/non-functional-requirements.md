# Non-Functional Requirements — chất lượng, safety và vận hành

| Thuộc tính | Giá trị |
|---|---|
| Document ID | PRD-NFR-001 |
| Phiên bản | 0.2.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §1.2, §5, §6, §7, §12, §13 và §14 |
| Related requirements | NFR-DET-001, NFR-AUD-001, NFR-SAFE-001, NFR-SEC-001, NFR-OPS-001, NFR-AI-001; SEC-CRED-001, SEC-AUTH-001, SEC-AUD-001, SEC-SUP-001, SEC-DATA-001, SEC-AI-001–003 |
| Related ADR | ADR-0001–0005, ADR-0007, ADR-0011–0016 theo phạm vi |

> Non-functional requirements là acceptance criteria ngang qua mọi context. Chúng không phải tùy chọn chỉ vì một task không thêm feature mới.

## 1. NFR-DET-001 — Determinism và reproducibility

**Requirement:** Cùng code version, config hash, input data/dataset manifest, seed, timestamp policy và execution model version MUST tạo cùng decision/event/ledger result trong replay/backtest.

**Acceptance evidence:**

- Fixture pin UTC, locale, Decimal context, seed và data/version checksum.
- Domain không dùng wall clock/global random; Clock và RandomSource được inject.
- Strategy checkpoint/config/feature contract/version được kiểm khi restore.
- Golden/replay test so sánh canonical output/event sequence và ledger outcome theo tolerance chỉ khi model stochastic đã pin.
- Backtest/report lưu code/config/risk/dataset/execution model lineage.

**Applies to:** FR-MKT-001, FR-STR-001, FR-LED-001, FR-RSK-001.
**Primary evidence:** replay/golden test, dataset/backtest manifest, checkpoint compatibility test.
**Phase gate:** Phase 1–2.

## 2. NFR-AUD-001 — Auditability và traceability

**Requirement:** Mỗi trading decision MUST có chuỗi truy vết từ market event/snapshot qua strategy/risk/order/fill đến journal/posting, với correlation/causation/trace identity và evidence không mơ hồ.

**Acceptance evidence:**

- Event envelope có id, type, schema_version, source, occurred_at, correlation_id, causation_id, trace_id, subject_id và data schema.
- Order/risk/fill/ledger/audit record liên kết canonical internal UUIDv7, actor/role khi có human action và hash/version của policy/config/input.
- Audit, order lifecycle event, journal và posting là append-only theo policy; projection có thể rebuild.
- API/error/log không lộ secret hoặc raw sensitive payload; evidence có redaction/classification.
- Trace-chain/rebuild tests chứng minh dữ liệu đủ để giải thích decision và phát hiện missing link.

**Applies to:** FR-EXEC-001, FR-LED-001, FR-REC-001, FR-RSK-001, FR-OPS-001.
**Primary evidence:** audit-chain test, property/rebuild test, immutable audit control, gate record.
**Phase gate:** Phase 0.0 và Phase 1.

## 3. NFR-SAFE-001 — Safety và fail-closed behavior

**Requirement:** Hệ thống MUST ngăn duplicate order, risk bypass và ledger imbalance; MUST fail closed khi market/reference/portfolio/runtime/external state không đáng tin cậy.

**Acceptance evidence:**

- ClientOrderId duy nhất theo venue/account; no blind retry sau external outcome unknown; reconciliation trước conflicting intent.
- OMS state-machine guard cấm terminal-to-non-terminal transition; fill duplicate không tạo effect lần hai.
- Risk dùng fresh immutable snapshot/version, reservation và concurrency control; missing/stale input reject theo policy.
- Ledger entry cân bằng và double booking bị chặn; adjustment có evidence/approval.
- Mất execution lease dừng claim/submission mới; split-brain/timeout/disconnect/DB failure được kiểm qua chaos/state-machine tests.
- Kill switch FREEZE default ngăn exposure tăng; release cần approval/re-auth/reconciliation/health evidence.

**Applies to:** FR-EXEC-001, FR-LED-001, FR-REC-001, FR-RSK-001.
**Primary evidence:** property/state-machine/chaos/reconciliation tests.
**Phase gate:** Phase 1, Phase 3 và Phase 4.

## 4. NFR-SEC-001 — Least privilege và secure boundaries

**Requirement:** Credential, process, API, UI và AI MUST dùng least privilege; AI/UI không có direct order path và trade credential không được xuất hiện ngoài trading-node scope đã được manifest cho phép.

**Acceptance evidence:**

- Credential tách theo environment/account; trade key không withdrawal; không có secret trong code, log, trace, fixture, UI hay AI worker.
- Mỗi process có machine identity/database role tối thiểu; không dùng DB superuser hoặc shared human token.
- Trước external venue, control API có actor authentication, permission enforcement, rate limit và audit; dangerous action có re-auth/reason.
- UI chỉ gọi Control API; AI worker đọc sanitized projection, ghi proposal/memory và không có execution tool/config promotion.
- Dependency/image/artifact được pin/review/scan; build/release evidence có lock/digest/SBOM khi phase yêu cầu.

**Applies to:** FR-EXEC-001, FR-RSK-001, FR-OPS-001 và mọi adapter.
**Primary evidence:** access-control/secret policy, authorization/negative-security test, scan result, deployment review.
**Phase gate:** Phase 0.0, Phase 3, Phase 4 và Phase 6 theo scope.

## 5. NFR-OPS-001 — Operability, recovery và evidence

**Requirement:** Runtime MUST có health/readiness, observability, alert, backup/restore/reconciliation procedure và runbook evidence phù hợp mode/phase.

**Acceptance evidence:**

- Structured log/tracing/metrics mang identity cần thiết để điều tra decision path mà không lộ secret.
- Health/readiness, worker heartbeat, outbox backlog, DB/lease/clock/feed/reconciliation/risk/ledger signals được định nghĩa và có alert severity policy.
- Runbook tồn tại cho unknown order, stream gap, reconciliation mismatch, kill switch, crash/restart, database failure, credential rotation và backup restore.
- Every deployment validates manifest/config hash, health, lease, reconciliation và alert route trước enable strategy.
- Restore/drill evidence được lưu; Phase 3 external venue gate yêu cầu mismatch alert trong tối đa 60 giây theo master.

**Applies to:** FR-MKT-001, FR-EXEC-001, FR-REC-001, FR-OPS-001.
**Primary evidence:** health/integration tests, drill report, incident/gate records.
**Phase gate:** Phase 0.0 through Phase 4.

## 6. NFR-AI-001 — Provider-independent, private và bounded AI operation

**Requirement:** AI capability MUST operate through approved provider/model profiles without making any provider mandatory. BYOK credential, data egress, budget/quota, timeout/rate/circuit behavior, provenance and failure handling MUST be enforced independently of the trading hot path.

**Acceptance evidence:**

- Provider/model/endpoint/policy profile is immutable-versioned, capability-tested and explicitly allowlisted; it pins adapter artifact digest, residency/retention terms, host/SNI/route and egress/usage policy. Unknown/deprecated/drifted provider, model, endpoint or profile is denied/revalidated/suspended without network attempt.
- API key is accepted only by isolated write-only secret ingress with no-store semantics and is absent from API response, browser storage, logs, proxy/WAF/APM, traces, errors, audit/event/command payload, DB/config/fixture/backup and prompt content. Ingress uses a one-time server-side enrollment session, not Idempotency-Key/body hash/fingerprint; lost response is resolved only by safe status read.
- Connection/job request validates owner scope, active connection revision/lease, provider/model/catalog/adapter version, resolved policy profile, egress class, purpose and hard budget/quota before provider call. DNS resolution/host/SNI/TLS/redirect/private-address policy is enforced by approved egress route.
- Input is sanitized/allowlisted; raw venue/account secret/session/private data is denied. Output/provider response is untrusted and must pass a versioned structured schema before any proposal/memory write.
- Cost/quota reservation is concurrency-safe and reconciled to actual usage; provider availability, latency, rate limit, invalid credential, budget exhaustion and circuit state are observable without raw vendor payload.
- Default failure policy is disable/fail AI only. No AI timeout, invalid output, provider outage, revoked key or unknown outcome changes trading/risk/OMS/ledger or causes silent cross-provider/key fallback. Rotation keeps active binding until candidate validation and atomic cutover; suspend/revoke invalidate binding leases, cancel when possible and discard invalidated in-flight output.
- Local/CI use fake/disabled provider and prove no execution tool/trade credential/key leak/cross-owner connection use, no secret-like audit reason, no egress bypass, and both initial/rotation lifecycle transitions.

**Applies to:** FR-AI-001 and every AI adapter, dashboard/control-plane AI connection route, `ai_worker`, memory/retrieval/proposal workflow.
**Primary evidence:** provider capability/contract test, secret-leak negative test, owner-scope authorization test, egress/budget/circuit test, outage/revoke drill and Phase 6 gate record.
**Phase gate:** Phase 6.

## 7. Implementation quality constraints

Các constraint dưới đây là phương thức bắt buộc để chứng minh NFR, không thay thế requirement ID:

| Chủ đề | Rule |
|---|---|
| Numeric/time | Decimal + NUMERIC(38,18); TIMESTAMPTZ UTC; API decimal string; no float. |
| Compatibility | Public contract có schema_version; optional addition compatible; breaking change tạo major version/upcaster/migration. |
| Test isolation | Unit/property/architecture test không dùng network, real clock, global random, locale hoặc production database. |
| Type/quality | Python public interface có type hint; Pyright strict; Ruff/Pytest/Hypothesis theo phase. |
| Dependency | Không thêm language/framework/database/runtime mới, dependency hoặc mutable image tag không có ADR/task/review. |
| Error/failure | External transient retry theo policy; unknown outcome reconcile, không blind retry; security/infrastructure fail closed. |
| Waiver | Chỉ SHOULD/non-safety goal có waiver; không waiver OMS/risk/ledger/audit/credential/migration/external-venue invariant. |

## 8. Security/control mapping

| NFR | SEC mapping |
|---|---|
| NFR-DET-001 | SEC-SUP-001, SEC-DATA-001 |
| NFR-AUD-001 | SEC-AUD-001, SEC-DATA-001 |
| NFR-SAFE-001 | SEC-AUD-001, SEC-CRED-001, SEC-AUTH-001 |
| NFR-SEC-001 | SEC-CRED-001, SEC-AUTH-001, SEC-SUP-001, SEC-AI-001 |
| NFR-OPS-001 | SEC-AUD-001, SEC-DATA-001, SEC-CRED-001 |
| NFR-AI-001 | SEC-AI-001, SEC-AI-002, SEC-AI-003, SEC-CRED-001, SEC-AUTH-001, SEC-AUD-001 |

## 9. Review and change policy

NFR acceptance must be verified by actual command/procedure, exit/result, evidence path and gate linkage. A higher coverage percentage, a successful demo or a human assertion does not replace invariant/recovery/security evidence. Any semantic change to an NFR needs traceability update and ADR if it affects architecture, persistence, risk, security or live gate.

## 10. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | Chuẩn hóa acceptance/evidence cho baseline non-functional requirements. | Technical Operator | Pending |
| 0.2.0 | 2026-07-31 | Thêm NFR-AI-001 cho vận hành BYOK đa provider, egress/budget và failure isolation. | Technical Operator | Pending |
