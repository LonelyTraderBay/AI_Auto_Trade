# REG-001 — Public contract registry

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.0 / IN_REVIEW |
| Owner / Approver | Technical Operator / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | FR-OPS-001, FR-OMS-001, NFR-SEC-001; ADR-0004, ADR-0005, ADR-0012, ADR-0014 |
| Change summary | Registry cho Phase 0.0 baseline contracts; implementation/validator command chưa tồn tại. |

## 1. Registry rule

OpenAPI is canonical for HTTP; versioned JSON Schema is canonical for command/event/config payload. Contract is DRAFT/IN_REVIEW and must not be implemented until task/ADR/gate conditions permit. Additive optional change needs compatibility evidence; semantic/removal/required/new-major behavior needs v2 and migration/deprecation plan. No schema contains secret or real venue/account data.

HTTP command request body is deliberately not the durable `C-CMD-001` record: server authentication derives actor/role, route derives command type/scope, header supplies idempotency key, server calculates canonical request hash and creates the `ACCEPTED` command record. Task 0.2 must add parity tests for every route mapping (body `reason`/`payload` -> C-CMD-001) and fail on drift; a client must never claim actor, status or request hash in HTTP JSON.

| Contract ID | Kind / version / status | Canonical path | Owner; producer -> consumer | Auth / sensitive classification / key | Fixture / validator / evidence | Related |
|---|---|---|---|---|---|---|
| C-API-001 | HTTP / v1 / IN_REVIEW | `contracts/api/openapi.yaml` | Technical Operator; Control API -> dashboard/CLI/operator | Actor auth/RBAC; sanitized operational data; HTTP idempotency key = actor + route + key | OpenAPI parser; API fixtures planned after Task 0.2; compatibility report required | FR-OPS-001, NFR-SEC-001, ADR-0015 |
| C-CFG-001 | config / v1 / IN_REVIEW | `contracts/config/task-card.v1.schema.json` | Technical Operator; task author -> CI/reviewer | No secret; task ID/branch governs diff allowlist | `contracts/fixtures/task-card.v1.valid.yaml`; JSON Schema 2020-12; task-card check evidence | NFR-OPS-001, ADR-0014 |
| C-CFG-002 | config / v1 / IN_REVIEW | `contracts/config/deployment-manifest.v1.schema.json` | Technical Operator; release process -> runtime/gate | Secret references only; immutable deployment identity; deployment ID partition | `contracts/fixtures/deployment-manifest.v1.paper.valid.yaml`; JSON Schema 2020-12 | NFR-SEC-001, NFR-OPS-001, ADR-0010 |
| C-CMD-001 | command / v1 / IN_REVIEW | `contracts/commands/operations/control-command.v1.schema.json` | Operations; Control API normalization -> owner handler | Durable internal command record; authenticated actor/RBAC; HTTP idempotency scope; no secret | `contracts/fixtures/control-command.v1.valid.json`; JSON Schema 2020-12 + C-API mapping parity test | FR-OPS-001, ADR-0007, ADR-0015 |
| C-CMD-002 | command / v1 / IN_REVIEW | `contracts/commands/execution/submit-order.v1.schema.json` | Execution; risk-approved execution app -> execution adapter | Internal only; ClientOrderId unique by venue/account; request hash | `contracts/fixtures/submit-order.v1.valid.json`; JSON Schema 2020-12 | FR-OMS-001, FR-RSK-001, ADR-0005, ADR-0012 |
| C-EVT-001 | event / v1 / IN_REVIEW | `contracts/events/platform/integration-event-envelope.v1.schema.json` | Platform; contexts -> consumers | Internal immutable event; `id` dedupe, `partition_key` ordering | `contracts/fixtures/integration-event-envelope.v1.valid.json`; JSON Schema 2020-12 | ADR-0004, ADR-0014 |
| C-EVT-002 | event / v1 / IN_REVIEW | `contracts/events/execution/order-event.v1.schema.json` | Execution; OMS -> projections/ledger/reconciliation | Internal immutable lifecycle event; event ID dedupe, order partition | `contracts/fixtures/order-event.v1.valid.json`; JSON Schema 2020-12 + parent envelope resolution | FR-OMS-001, FR-REC-001, ADR-0005 |
| C-ERR-001 | error catalog / v1 / IN_REVIEW | `contracts/errors/error-catalog.md` | Technical Operator; Control API -> all API consumers | Safe structured public error; correlation ID, no raw sensitive data | `ErrorEnvelope` in C-API-001; route contract tests planned | NFR-SEC-001, ADR-0015 |

## 2. Offline schema resolution

Contract validation must load schemas from the checked-out repository into an offline registry keyed by their `$id`; it must not fetch `https://ai-auto-trade.invalid` or any network URL. In particular, `C-EVT-002` resolves its relative `../platform/integration-event-envelope.v1.schema.json` reference against its canonical `$id` to `C-EVT-001`. The contract validator introduced in Task 0.2 must fail closed for missing, duplicate, unregistered, or network-resolved references and record the resolver/version in CI evidence.

## 3. Retirement and consumer impact

No v1 retirement is planned. A future retirement record must name producer/consumer, supported versions, compatibility window, migration/upcaster, task/ADR, evidence and removal gate. Consumer that receives an unsupported event version DLQs/alerts rather than crashes or interpreting guessed semantics.
