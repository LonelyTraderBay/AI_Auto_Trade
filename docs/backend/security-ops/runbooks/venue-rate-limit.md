# RB-010 — Venue API rate limit, IP ban or key ban

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.0 / DRAFT |
| Trigger / Severity | HTTP 429/418, venue ban notification, sustained request rejections / High; Critical if any open order is `UNKNOWN` while the order path is throttled/banned |
| Scope / Incident commander | Affected venue, environment, API key/IP/egress path, order path vs market-data path / Technical Operator |
| Related | FR-EXEC-001, FR-REC-001, NFR-OPS-001, NFR-SEC-001; ADR-0007; OPS-001, SEC-002; RB-001, RB-005, RB-007; master §11.3, §14 |
| Change summary | Rate-limit/ban containment and staged resume procedure; drill of this runbook is a Phase 3 external-venue Go/No-Go condition (master §14). |

## Safe-state objective

No new exposure is created through a degraded/banned venue path and no retry storm makes the ban worse. Existing order/position uncertainty is resolved through reconciliation at the lowest request rate the venue still permits. Keys and IPs are not rotated reflexively: an unclassified ban that follows a rotated key/IP only spreads the ban surface.

## Procedure

1. Open incident; record venue, environment, response codes (429/418/ban payload metadata, never raw credential), affected endpoints, request-rate metrics before onset, deployment/manifest hash and current open orders/strategies.
2. Classify the affected path — decision point:
   - Order path only, market-data path only, or both. Order-path impact with any in-flight submit/cancel means the affected orders follow RB-001 (`UNKNOWN`, no blind retry).
3. Enter safe state: pause new order submission for the affected scope (do not mass-cancel; cancel requests consume the same limited budget and can themselves be rejected or become `UNKNOWN`). Keep reconciliation and read paths running at the lowest rate the venue permits. Do NOT rotate key or IP reflexively; an IP-ban vs key-ban vs endpoint throttle must be classified first.
4. Determine cause — decision point:
   - Self-inflicted burst: retry storm, wrong/missing backoff, duplicate poller, misconfigured batch size. Compare retry/circuit-breaker config against the approved venue capability profile and recent config/manifest changes.
   - Venue-side change: reduced limits, maintenance, ban policy change. Verify against venue status/notification through the approved channel; record evidence.
5. Recover with controlled backoff: exponential backoff with jitter within approved policy bounds, then staged resume with an error-rate threshold per stage — read-only/market data first, then reconciliation, then order submission. A stage that breaches its error-rate threshold drops back one stage; record each stage transition time.
6. Ban handling — decision point:
   - Key-ban or suspected key-level restriction: switch to RB-007 credential rotation; the replacement key inherits the paused submission state until reconciliation completes.
   - IP-ban: escalate to Security/Backup Owner; egress/IP topology change is an OD-005 topology decision, not an operator improvisation.

## Verify and resume

Evidence must show rejection rate back within policy, retry/backoff config validated against the capability profile, no `UNKNOWN` order remaining unresolved, reconciliation clean for the affected account scope and each resume stage passing its error-rate threshold. Technical Operator resumes submission only after the final stage holds; Risk Approver is required if risk scope was frozen.

## Escalation and evidence

Escalate to Critical for any `UNKNOWN` open order while the order path is unavailable, a ban that persists beyond policy deadline, suspected venue-side compromise or a self-inflicted storm from an unapproved config. Retain timeline, response codes/headers metadata, rate/retry config before and after, stage-resume timestamps and the classification decision. A completed drill of this runbook is required evidence for the Phase 3 external-venue Go/No-Go gate (master §14).
