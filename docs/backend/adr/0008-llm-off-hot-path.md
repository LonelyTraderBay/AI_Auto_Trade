# ADR-0008 — LLM/AI is proposal-only and off the trading hot path

| Thuộc tính | Giá trị |
|---|---|
| Status | DRAFT — required only before Phase 6; no AI runtime authorized |
| Date | 2026-07-31 |
| Owner | Technical Operator |
| Approver | Account Owner |
| Related | NFR-SEC-001, NFR-DET-001, NFR-SAFE-001, ADR-0016; [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §4.1–§4.5, §10.6–§10.8, §14 Phase 6 |
| Supersedes / superseded by | None / None |

## Context and decision drivers

LLM output is probabilistic, may be unavailable, may leak sensitive context and is unsuitable as a latency/correctness/safety dependency for order path. The architecture needs a hard technical boundary so a provider, prompt or memory item cannot acquire trading capability through an indirect tool.

## Proposed decision

Until this ADR is approved, no LLM/provider dependency/runtime exists. If later approved, `ai_worker` has a separate machine identity and resolves only a scoped opaque AI credential binding just-in-time; it never receives a venue credential or raw provider key. It reads only sanitized projection and writes only proposal/memory context. It can produce structured, schema-validated proposals that enter the normal candidate/backtest/review workflow. It has zero execution port, no risk/config promotion privilege and no direct tool/API route that can place/cancel order. Provider selection, BYOK lifecycle, catalog, egress and budget controls are defined by ADR-0016.

Trading remains functional when AI is disabled, slow, invalid or unavailable. Memory has provenance, review status, effective time/retention and point-in-time retrieval; replay cannot use future memory. No self-modification, auto-promotion or live-code/risk/config change is authorized.

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| LLM directly chooses/submits orders | unverifiable safety/latency and credential escalation risk |
| AI shares trading node credentials | violates least privilege and blast-radius boundary |
| AI result blocks strategy hot path | availability/provider outage changes trading behavior unpredictably |
| Store unreviewed memory as truth | provenance/future leakage and audit failure |

## Consequences

AI is optional advisory capability, not an execution component. It needs provider/redaction/budget/structured-output contract, owner-scoped BYOK catalog/connection controls (ADR-0016), threat model, zero-credential test and controlled learning gates. A fake/disabled provider is the first allowed provider. No enablement before paper/canary core stability.

## Migration, rollout and rollback/forward-fix

No rollout now. Future rollout is disabled -> fake provider -> sanitized proposal -> backtest/walk-forward/stress -> shadow/paper -> separately approved canary. Rollback is disable AI worker/provider; no trading replay or ledger fact depends on it.

## Approval criteria

- [ ] Phase 6 entry conditions and core stability evidence exist.
- [ ] Security review proves zero execution/venue credential path.
- [ ] Structured-output, redaction, budget, provenance/retention and no-future-memory tests pass.
