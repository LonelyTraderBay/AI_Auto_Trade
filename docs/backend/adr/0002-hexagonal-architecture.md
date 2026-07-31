# ADR-0002 — Hexagonal architecture, dependency rules and composition root

| Thuộc tính | Giá trị |
|---|---|
| Status | DRAFT — required for Phase 0.0; chưa mở gate |
| Date | 2026-07-31 |
| Owner | Technical Operator |
| Approver | Account Owner |
| Related | FR-STR-001, FR-EXEC-001, FR-RSK-001, FR-LED-001, NFR-DET-001, NFR-SEC-001; [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §4–§5; ADR-0001, ADR-0014 |
| Supersedes / superseded by | None / None |

## Context and decision drivers

Core trading rules must be deterministic/testable without FastAPI, SQLAlchemy, Pydantic, venue SDK, CCXT, NautilusTrader or OpenAI provider. The project also needs to change adapter/provider/mode without rewriting OMS/risk/ledger semantics. An architectural dependency rule is therefore a safety control, not a preference.

## Proposed decision

If approved, every bounded context uses three allowed layers:

```text
domain/       pure entities, value objects, policies, commands, events
application/  use cases/handlers/services and boundary DTO mapping
ports/        protocols/interfaces required from outside
```

Concrete vendor/framework implementations live only under `src/ai_auto_trade/adapters/<kind>/<provider>/`. The composition root of each process under `apps/` is the only place wiring a concrete adapter to a port. Dependencies point inward: domain uses Python standard library/shared kernel only; application uses domain/ports; adapters implement ports. Contexts do not import each other’s private implementation or ORM model.

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| Framework-first modules | lets persistence/API/vendor types leak into business/safety rules |
| Context-local adapters | gives each context a divergent topology and makes vendor ownership opaque |
| Shared `utils`/service layer | becomes unowned cross-domain coupling |
| Direct strategy adapter/DB/network calls | breaks deterministic replay and bypasses security/risk boundaries |

## Consequences

Implementation has explicit mapping at API/adapter boundaries and some files/types that a prototype might omit. In exchange, fake venue, replay, deterministic strategy and contract testing remain possible. Shared kernel is narrow: only stable concepts used by at least three contexts; it is not a convenience package.

Domain may not import FastAPI, SQLAlchemy, Pydantic, CCXT, NautilusTrader, OpenAI SDK or HTTP client. Strategy may not read environment/files/database/network directly. UI cannot call venue/database. AI has no execution path.

## Migration, rollout and rollback/forward-fix

Phase 0 creates empty topology and architecture/import tests before implementation. A dependency violation blocks the task; it is fixed by moving interface/mapping to the appropriate layer, not by adding an exception. Any intentional new dependency/layer needs ADR plus updated tests and repository policy.

## Approval criteria

- [ ] Account Owner accepts this as a safety/maintainability boundary.
- [ ] Architecture diagram/repository convention/coding protocol link to this ADR.
- [ ] Phase 0 acceptance includes architecture test proving domain/vendor isolation.

