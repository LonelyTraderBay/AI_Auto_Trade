# ADR-0001 — Modular monolith trước microservice

| Thuộc tính | Giá trị |
|---|---|
| ADR ID | ADR-0001 |
| Phiên bản | 0.2.0 |
| Status | APPROVED — approved by Account Owner 2026-08-06T00:00:00Z |
| Date | 2026-07-31 |
| Owner | Technical Operator |
| Approver | Account Owner |
| Effective date | 2026-08-06 |
| Decision deadline | Phase 0.0 gate |
| Rà soát gần nhất | 2026-08-06 |
| Related | FR-EXEC-001, FR-LED-001, FR-REC-001, NFR-OPS-001; [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §3–§4; ADR-0002, ADR-0014 |
| Supersedes / superseded by | None / None |
| Change summary | 0.2.0 (2026-08-06): Status → APPROVED; Account Owner decision 2026-08-06T00:00:00Z. |

## Context and decision drivers

MVP có một người phát triển/vận hành, một venue crypto spot, một account và mục tiêu trước hết là correctness, audit, recovery. Trading lifecycle có nhiều boundary domain nhưng chưa có bằng chứng tải/đội ngũ/vận hành cần distributed service. Microservice hoặc external broker sớm sẽ nhân bản transaction, delivery, deployment, credential và reconciliation boundary.

## Proposed decision

If approved, MVP runs as a **modular monolith**: one versioned repository, one deployable logical system and bounded contexts inside it. Context ownership/dependency is enforced by modules, ports, contracts and architecture tests. Separate processes (`control_api`, `trading_node`, workers, CLI) may exist for responsibility/credential separation but are not independently owned microservices and do not create new system-of-record boundaries.

Inter-process delivery uses typed in-process dispatch only after commit plus PostgreSQL outbox/inbox where necessary. PostgreSQL remains the system of record; no Kafka/NATS/Redis/Kubernetes/additional database is introduced by default.

## Alternatives considered

| Alternative | Why not proposed now |
|---|---|
| Microservices per context | adds network failure, distributed transaction, observability, deploy/version and credential overhead before vertical slice proves need |
| Event broker first | duplicates delivery/ops surface while PostgreSQL outbox/inbox meets MVP delivery requirement |
| Single unbounded application module | lower initial ceremony but destroys ownership/audit/test boundaries and makes later extraction unsafe |
| Multiple databases by context | creates reconciliation/backup/transaction complexity without demonstrated benefit |

## Consequences

Positive: simpler local/CI/restore story, one migration lineage, low operations cost and explicit domain boundaries. Negative: module discipline is mandatory; a bad import/direct table access can create a hidden monolith. Architecture tests, CODEOWNERS/task allowlists and ADR-0002 are required compensating controls.

There is no promise that all processes share memory, credentials or runtime state. `trading_node` remains the only execution-wiring process; control/UI/AI do not receive venue trade capability.

## Migration, rollout and rollback/forward-fix

Phase 0.0 approves topology only. Phase 0 creates repository guardrails; no service deployment is created by this ADR. Future extraction requires a new ADR proving workload/team/operational reason, data ownership transition, contract compatibility, dual-run/reconciliation, backup and rollback/forward-fix plan. Reversing an extraction is not assumed trivial.

## Approval criteria

- [x] Account Owner accepts MVP scope and non-microservice default.
- [x] ADR-0002/0014 and architecture docs enforce context/process boundaries.
- [x] No task introduces a broker, extra database, orchestration platform or service without a new ADR.

## Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.2.0 | 2026-08-06 | Status → APPROVED; Account Owner decision 2026-08-06T00:00:00Z. | Account Owner | Account Owner |

