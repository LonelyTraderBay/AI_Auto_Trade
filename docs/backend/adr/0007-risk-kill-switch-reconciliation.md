# ADR-0007 — Risk, reservation, kill switch and reconciliation policy

| Thuộc tính | Giá trị |
|---|---|
| ADR ID | ADR-0007 |
| Phiên bản | 0.1.0 |
| Status | DRAFT — required for Phase 0.0; chưa mở gate |
| Date | 2026-07-31 |
| Owner | Risk Approver |
| Approver | Account Owner (pending) |
| Effective date | Chưa hiệu lực (chỉ điền khi APPROVED) |
| Decision deadline | Phase 0.0 gate |
| Rà soát gần nhất | 2026-08-02 |
| Related | FR-RSK-001, FR-EXEC-001, FR-REC-001, NFR-SAFE-001, NFR-AUD-001; [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §5.4–§5.6, §6.3, §8.4–§8.10; DOM-003 |
| Supersedes / superseded by | None / None |
| Change summary | 0.1.0 (2026-08-02): chuẩn hóa header theo TMP-ADR-001/GOV-DOC-001 §3 — thêm ADR ID/Phiên bản/Effective date/Decision deadline/Rà soát/Change summary (audit toàn diện); nội dung quyết định không đổi (soạn 2026-07-31). |

## Context and decision drivers

Capital safety needs deterministic pre-trade decision, balance/exposure reservation, safe behavior under stale data/unknown order and operator controls that cannot be bypassed. Venue can be inconsistent/unavailable, so local state and external snapshot must be reconciled rather than assumed equal.

## Proposed decision

If approved, risk is a synchronous, versioned, deterministic gate before any execution queue. It evaluates immutable intent against active policy, portfolio/reference/market snapshots, reservation/limit state, runtime health, valid leader lease and injected time. Missing/stale/ambiguous input rejects/fails closed. An approval persists decision and reservation atomically with durable queue; `REQUIRE_MANUAL_APPROVAL` creates pending risk state only and requires full fresh re-evaluation after authorized approval.

Reservations prevent pre-submit balance/exposure oversubscription and release only from proven lifecycle/reconciliation facts. Kill switch hierarchy is `GLOBAL -> VENUE -> ACCOUNT -> STRATEGY -> INSTRUMENT`; parent scope wins. MVP default action is `FREEZE` (no exposure increase). `CANCEL_OPEN_ORDERS` needs capability/policy; automatic `FLATTEN` is not MVP.

Reconciliation runs startup, periodic, on stream gap/disconnect/unknown order and operator request. Mismatch creates evidence/case; affected scope blocks new exposure. Local history is never overwritten to match venue.

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| Async/best-effort risk after submit | cannot prevent unsafe order reaching venue |
| UI approval as risk bypass | approval can be stale and is not deterministic policy evaluation |
| Clear stale reservation by timer | hides unknown order/exposure and can double spend |
| One global kill toggle only | insufficient scope/audit control |
| Auto-flatten by default | can create further unsafe execution under degraded data/capability |

## Consequences

Risk policy/parameters must be immutable, signed/versioned and scope-aware; no code default is a live parameter. Each decision/reservation/approval/kill action has audit/correlation/evidence. Risk and execution share approved `SERIALIZABLE`/lock-order rules in ADR-0012. Emergency reduce-only exception must be separately specified/approved; it is not implied.

## Migration, rollout and rollback/forward-fix

Phase 1 proves fake-venue policy, reservations, state block and reconciliation. Policy change creates a new effective version; no mutation in place. A safety issue uses kill/freeze, evidence, reconciliation and forward-fix; it does not remove audit or retry an unknown submit.

## Approval criteria

- [ ] Risk Approver and Account Owner approve DOM-003 policy structure/invariants.
- [ ] Owner supplies applicable parameter policy before environment activation; no values are inferred here.
- [ ] OMS/transaction/reconciliation tests cover stale data, concurrent reservation, approval expiry, kill scopes and unknown state.

