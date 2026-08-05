# RB-008 — Backup, restore and rollback verification

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.1 / DRAFT |
| Owner / Approver | Security/Backup Owner / Account Owner (pending) |
| Effective date / Last review | Chưa hiệu lực / 2026-08-02 |
| Trigger / Severity | Scheduled restore drill, data-loss/corruption recovery, failed deployment rollback or backup/PITR alert / High; Critical for integrity/audit/financial data loss |
| Scope / Incident commander | Approved consistency set/environment/incident / Security/Backup Owner |
| Related | NFR-OPS-001, NFR-SEC-001; ADR-0003, ADR-0010, ADR-0013; SEC-004; RB-006 |
| Change summary | Consistency-set and isolated-restore procedure; no destructive restore instruction. 1.0.1 (2026-08-02): bổ sung Owner/Approver + Effective/Last review theo GOV-DOC-001 §3 (audit toàn diện). |

## Safe-state objective

Preserve original evidence and avoid destructive overwrite. A restore is first performed in an isolated authorized environment. The consistency set includes PostgreSQL + WAL/PITR material, Parquet/catalog manifests, evidence artifacts, immutable config/deployment manifests and required ADR/gate records for replay/audit.

## Procedure

1. Create incident/drill record: purpose, scope, owner/approver, requested recovery point, source consistency-set ID/checksums, encryption/access classification, manifest/migration revision and expected verification.
2. Freeze affected changes and execution as required. For live external uncertainty, use RB-001/RB-003; database failure uses RB-006. Do not delete production data, overwrite backup, or use unreviewed downgrade migration.
3. Select approved backup/PITR material and verify availability/checksums/chain without exposing keys or copying sensitive dump into ticket/prompt.
4. Restore to isolated environment with separate credentials/network and no venue execution capability. Verify decrypt/access, PostgreSQL/WAL consistency, schema revision, catalog/Parquet manifest checksums, deployment/config/ADR/gate provenance and append-only audit/ledger integrity.
5. Run approved read-only reconciliation/replay checks: order/fill/balance/position evidence, outbox/inbox position, ledger balance, audit chain, data lineage and application health. Record actual RPO/RTO versus policy.
6. Decide forward-fix, rollback to known-good immutable deployment manifest, or controlled production recovery only with role approvals and a dedicated gate. No production restore is authorized merely because isolated restore passed.

## Verify and close

Closure requires isolated restore evidence, integrity/reconciliation/replay result, migration compatibility, no secret leakage, backup freshness/retention status, action decision, approval and follow-up remediation. Canary/live restoration requires the required independent approvals and updated gate evidence.

## Escalation and evidence

Escalate Critical for unreadable/incomplete consistency set, audit/ledger mismatch, data loss beyond approved RPO, encryption/access failure, untrusted backup, or any pressure to overwrite production without gate. Retain set identifiers/checksums, not secret material or dump contents, plus drill timeline and post-mortem.

