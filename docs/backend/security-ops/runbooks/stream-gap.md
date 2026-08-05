# RB-002 — Market/private stream gap or stale feed

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.2 / DRAFT |
| Owner / Approver | Technical Operator / Account Owner (pending) |
| Effective date / Last review | Chưa hiệu lực / 2026-08-02 |
| Trigger / Severity | Disconnect, sequence gap, malformed stream, or freshness > approved max age / High; Critical if stale input reached submission |
| Scope / Incident commander | Affected feed, venue, account/instrument, consumer process / Technical Operator |
| Related | FR-MKT-001, FR-RSK-001, NFR-OPS-001; ADR-0007, ADR-0009; OPS-001 |
| Change summary | Design procedure for public and private feed recovery; sửa dangling requirement ID theo audit 2026-08-02. 1.0.2 (2026-08-02): bổ sung Owner/Approver + Effective/Last review theo GOV-DOC-001 §3 (audit toàn diện). |

## Safe-state objective

No new exposure is created from stale/untrusted market, reference, balance, position, open-order or private-stream data. Preserve watermarks/gap evidence, freeze affected strategy/execution scope and restore a verified snapshot-plus-delta sequence before resuming.

## Procedure

1. Record incident scope, stream type, expected/observed sequence or timestamp, received/processed time, deployment/manifest hash and affected orders/strategies.
2. Mark feed health degraded and block new exposure for the affected scope. For private account stream uncertainty, also evaluate RB-001/RB-003; do not assume no fills occurred.
3. Confirm clock/lease/process health. Do not compensate a gap using wall-clock guesswork or mixed environment data.
4. Reconnect through approved adapter with bounded retry/backoff. Obtain an authoritative snapshot and synchronize only compatible deltas/history after the snapshot watermark; deduplicate by venue sequence/trade ID/event ID.
5. Validate reference/instrument version, quality flags, source checksum, ordering and freshness against operations/risk policy. If history backfill is required, record source/version/checksum and do not use unverified data for decision.
6. If gap crosses an order lifecycle/private account uncertainty, request reconciliation using `POST /api/v1/commands/reconciliations` and keep submission blocked until it completes.

## Verify and resume

Evidence must show contiguous/acceptable sequence, valid snapshot/delta order, current freshness, cleared quality gate, no duplicate market/private event effect, matching position/open-order state where applicable, and risk gate re-evaluation. Technical Operator may request resume only within approved policy; Risk Approver is required when safety/risk scope dictates.

## Escalation and evidence

Escalate to Critical if stale data reached a submitted intent, private stream remains unavailable beyond policy, gap cannot be backfilled, data source appears poisoned, or reconciliation differs. Retain redacted stream metadata, quality report, commands, timing, policy version and incident decision.

