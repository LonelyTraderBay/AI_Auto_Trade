# Language and Technology Policy

| Thuộc tính | Giá trị |
|---|---|
| Document ID | ARC-TECH-001 |
| Phiên bản | 0.4.0 |
| Change summary | 0.4.0: đồng bộ PostgreSQL 17.x theo ADR-0003 amendment được Account Owner phê duyệt 2026-08-12T11:15:53Z; các công nghệ và ranh giới khác không đổi. |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-08-01 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §3, §4.3–§4.8, §6, §7, §13 và §15.1 |
| Related requirements | NFR-DET-001, NFR-SEC-001, NFR-OPS-001, SEC-SUP-001 |
| Related ADR | ADR-0001, ADR-0002, ADR-0003, ADR-0014; ADR-0006/0008/0016 only when applicable |

> Chính sách này chốt technology baseline cho MVP nhưng chưa là approval sử dụng package/version cụ thể. Version lock, security/license review và task approval vẫn bắt buộc trước khi dependency xuất hiện trong runtime.

## 1. Chính sách nền tảng

- MVP là modular monolith, hexagonal và event-driven có chọn lọc; không khởi tạo microservice hay distributed infrastructure.
- Python 3.12.x là ngôn ngữ runtime duy nhất cho domain, application, adapter, worker, CLI, test và migration helper.
- PostgreSQL 17.x là OLTP system of record; Parquet partitioned catalog + DuckDB reader dùng cho historical/research.
- Contract-first: OpenAPI/JSON Schema/config schema versioned là authority của wire detail sau khi được phê duyệt.
- Domain giữ Python thuần; framework/vendor/IO chỉ ở adapter/composition root.
- Target testnet/canary là Linux container image pin digest; Windows chỉ hỗ trợ local development tooling.

## 2. Technology matrix

| Technology / format | Status / vị trí được phép | Mục đích | Không được dùng cho |
|---|---|---|---|
| Python 3.12.x | Required: domain, application, ports, adapters, apps, tests, migration helper. | Runtime MVP thống nhất. | Tự thêm TypeScript/Go/Rust/Java cho MVP. |
| Python standard library | Required in domain/shared kernel. | Value object, policy, deterministic logic. | Vendor IO/framework bypass. |
| Pydantic v2 | API, adapter và config boundary. | Validation/serialization boundary. | Domain entity/policy ownership. |
| FastAPI + OpenAPI | Control API from Phase 0 skeleton. | Control/read contract. | Trading hot path, direct venue call or secret response. |
| PostgreSQL 17.x | Persistence/system of record from Phase 0. | Transaction, audit, concurrency, recovery. | Research data lake or arbitrary cross-context table write. |
| SQLAlchemy 2 + Alembic | Persistence adapter/migration. | Reviewed persistence and immutable migration. | Domain/risk policy hidden in SQL. |
| Parquet | data/catalog historical partition. | Immutable-ish dataset/research storage. | OLTP execution/ledger state. |
| DuckDB reader | research/backtest reader. | Analytical read of catalog. | Runtime system of record. |
| uv + pyproject.toml + lock file | Repository/package environment. | Reproducible dependency resolution. | Unlocked runtime dependency. |
| Ruff | CI/local formatting and lint. | Python quality baseline. | Replacing type/invariant test. |
| Pyright strict | CI/local type checking. | One type checker for MVP. | Introducing mypy in parallel. |
| Import Linter | CI/local architecture/import rule enforcement, cùng cấp Ruff/Pyright (master §13.1). | Enforce layer/context/adapter import contract. | Thay thế architecture test hoặc code review. |
| Pytest + Hypothesis | Test/property test. | Unit through chaos/golden evidence. | Replacing contract/integration test with mocks only. |
| OpenTelemetry-compatible tracing | Adapter/operations layer. | Structured trace/metrics correlation. | Raw secret or sensitive payload export. |
| Docker/Linux container | Testnet/canary runtime image. | Reproducible runtime/deploy. | Mutable-tag deployment. |
| YAML | Non-secret config, CI, manifest input. | Schema-validated declaration. | Secret store or bypass for risk/business override. |
| JSON / JSON Schema | API/event/command/config payload/fixture. | Versioned wire contract. | JSONB substitute for structured financial/domain state. |
| Markdown | Docs, ADR, runbook, gate evidence/template. | Human review and policy. | Runtime configuration authority. |
| SQL | Alembic/reviewed persistence query only. | Physical data operations. | Direct strategy/UI database access. |
| Shell / PowerShell | Idempotent bootstrap/lint/test helper. | Developer/CI utility. | Business, risk or execution logic. |
| Dart / Flutter | Phase 5 dashboard client only. | Control API UI. | Direct venue/DB/secret/trading logic. |

## 3. Deferred and constrained technologies

| Technology | Rule |
|---|---|
| NautilusTrader | Deferred until ADR-0006; not dependency in Phase 0–4; never owns canonical domain. |
| CCXT | Prototype, capability discovery or read tooling only; not default live execution core. |
| TimescaleDB | Deferred until measured time-series need and ADR; domain must not depend on extension. |
| pgvector | Phase AI/memory only, with ADR/scope. |
| AI provider SDK/HTTP client | Phase 6 only through `ai_worker` and `adapters/llm/<approved-provider>`; provider-neutral BYOK catalog/connection policy; proposal-only and no trade credential. OpenAI SDK is optional, never required. |
| Redis, Kafka, NATS, Kubernetes, extra database or orchestration framework | Forbidden by default; require ADR, owner, threat/operations impact, dependency review and phase gate. |

## 4. Code and repository topology

The intended repository shape is:

~~~text
src/ai_auto_trade/
  shared_kernel/
  contexts/<context>/{domain,application,ports}/
  adapters/<kind>/<provider>/
  apps/{control_api,trading_node,workers,cli}/
contracts/{api,commands,events,config,errors,fixtures}/
configs/{base,environments,services,venues,strategies,risk,deployments}/
migrations/
tests/{architecture,unit,property,state_machine,contract,integration,replay,golden,chaos,e2e,fixtures,factories}/
~~~

Rules:

- A context has domain/application/ports only; concrete adapter is global under adapters, not a parallel context-local adapter tree.
- Composition root is the only wiring point for framework/vendor implementation.
- No unowned utils.py, helpers.py, common.py or misc.py dumping ground.
- File/module uses snake_case; type/class PascalCase; field/function/contract key snake_case; wire enum SCREAMING_SNAKE_CASE.
- Contract/config filename carries a version, such as <name>.v1.schema.json; breaking change creates a new major file rather than overwriting.
- Generated output belongs in generated/ or explicitly authorized path and must not be manually edited.

Detailed repository/coding/CI enforcement is owned by the Phase 0.0 engineering artifact pack.

## 5. Data, format and compatibility rules

| Area | Mandatory policy |
|---|---|
| Internal identity | UUIDv7 in PostgreSQL UUID type; external venue ID stored separately. |
| Finance | Decimal in domain, NUMERIC(38,18) in DB, string in API/event payload; no float. |
| Timestamp | TIMESTAMPTZ UTC in database, ISO-8601 with Z on wire; names end in _at. |
| Canonical JSON/hash | UTF-8, lexicographic key sort, no whitespace, canonical Decimal/timestamp string, no NaN/Infinity, SHA-256. |
| Contract version | Every public contract has schema_version; optional addition with default is compatible. |
| Breaking change | New major schema/route/contract, migration/upcaster/consumer plan and compatibility evidence. |
| Configuration | Schema-validated, non-secret, immutable effective deployment identity; environment variable only allowed secret bootstrap scope. |

## 6. Dependency and version control

1. New package/runtime needs task ID, purpose, license/security review, pinned lock version and tests.
2. Production/testnet/canary artifact uses locked dependency set; no unreviewed range or ad hoc package install.
3. Container image must be pinned by digest before canary; mutable image tag is not deployable evidence.
4. CI runs secret/dependency/SAST scan appropriate to phase; runnable artifact gets SBOM when required.
5. Dependency that changes architecture, provider boundary, database, crypto/auth or external network behavior needs ADR and security/operations review.
6. Only official documentation/locked version may be used when implementing provider/library integration; record the version in task/evidence.

## 7. Required quality toolchain by phase

| From phase/task | Required capability |
|---|---|
| Task 0.1 | uv locked sync, Ruff format/lint, Pyright, Pytest. |
| Task 0.2 | Architecture/import rule and contract validation command. |
| Task 0.3 | Alembic/database verification and migration testing. |
| Phase 1 | State-machine, property, fake-venue, ledger/recovery test. |
| Phase 2 | Replay/golden/catalog quality test. |
| Phase 3+ | Adapter contract, integration, chaos, authorization/restore/drill evidence. |

Exact command profile follows master §13.2 and the approved task card. A command cannot be claimed as passing before the project exposes it and evidence includes exit result.

## 8. Runtime và tooling decisions bổ sung (DRAFT — cần Account Owner phê duyệt trước Task 0.1/0.2)

Các quyết định dưới đây là đề xuất bổ sung theo audit, chưa được phê duyệt; toàn bộ bảng mang trạng thái DRAFT — đề xuất, cần Account Owner phê duyệt. Cụm quyết định này được theo dõi qua RAID I-008; các package ngoài danh sách allowed (httpx, websockets, uvicorn, opentelemetry-python) chỉ được đưa vào dependency khi có amendment ADR-0014 hoặc ADR mới theo trigger §9 — không muộn hơn trước Task 0.2. Task 0.1 không bị ảnh hưởng (runtime dependencies rỗng theo ENG-PY-001 §5a-ref).

| Chủ đề | Đề xuất | Phạm vi | Lý do ngắn |
|---|---|---|---|
| Concurrency model | asyncio (stdlib), không thêm anyio/trio; ports khai báo sync/async rõ ràng theo context; trading_node hot path đơn luồng theo venue/account với Clock inject; mọi periodic loop (reconciliation_interval_s, lease heartbeat, outbox polling) là in-process asyncio task — không external scheduler/cron cho runtime loop. | Toàn bộ runtime process. | Determinism, một concurrency paradigm duy nhất, không dependency mới. |
| HTTP/WebSocket client | httpx (HTTP) + websockets (stream) — chỉ được import trong adapters/ và apps/cli; cấm trong domain/application. | Adapters và CLI. | Async-native, giữ hexagonal boundary. |
| ASGI server | uvicorn; FastAPI/Pydantic major upgrade cần task + compatibility evidence. | apps/control_api. | Chuẩn de-facto cho FastAPI, upgrade có kiểm soát. |
| Logging | stdlib logging + JSON formatter trong shared_kernel (không structlog — tránh dependency mới không ADR); schema chi tiết theo docs/backend/engineering/logging-standard.md. | Toàn bộ process. | Structured log không thêm dependency ngoài stdlib. |
| OpenTelemetry | opentelemetry-python SDK; exporter/collector topology chốt cùng OD-005 trước Phase 3. | Adapter/operations layer. | Trace/metrics chuẩn, hoãn topology tới OD-005. |
| Integration-test DB | PostgreSQL container ephemeral qua docker-compose test profile, image pin digest; không testcontainers-python khi chưa có ADR dependency. | tests/integration. | Test trên PostgreSQL thật, pin digest, không dependency mới. |
| Alembic | Một environment duy nhất, một linear branch (không multiple heads); SQLAlchemy naming_convention dict khai báo tường minh trong migration env; autogenerate chỉ là draft — revision áp dụng phải được review tay từng dòng so với data dictionary. | migrations/. | Migration history tuyến tính, deterministic và review được. |
| CLI framework | argparse (stdlib) cho Task 0.1 skeleton; nâng cấp typer/click cần dependency review theo CONTRIBUTING §3. | apps/cli. | Skeleton không cần dependency; nâng cấp có kiểm soát. |
| Canonical JSON/SHA-256 | Implement trong shared_kernel với golden fixtures; cấm third-party canonicalization dependency khi chưa có ADR. | shared_kernel + contract/hash path. | Hash/idempotency ổn định, kiểm soát toàn bộ canonicalization logic. |

## 9. Decision triggers

Create or amend ADR before:

- adding language, database, service, broker, framework or runtime not listed as allowed;
- introducing NautilusTrader, TimescaleDB, pgvector, an AI provider/endpoint family/SDK or a new venue execution boundary;
- changing AI provider catalog, BYOK credential ingress, secret boundary, model capability, data egress, budget/fallback or owner-scope semantics;
- changing PostgreSQL/Parquet ownership, public contract semantics, data retention, authentication/session or deployment topology;
- weakening a safety/security restriction.

## 10. Review checklist

- [ ] Choices agree with Master §3.5 and no deferred technology is implicitly added.
- [ ] Boundaries preserve pure domain and global adapter topology.
- [ ] Version/package/dependency policy can be enforced by CI/task card.
- [ ] Data/format rules agree with planned contract/data documents.
- [ ] Any unresolved selection is recorded as OD/ADR, not fabricated in code.

## 11. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.4.0 | 2026-08-12 | Đồng bộ PostgreSQL 17.x theo ADR-0003 amendment; giữ nguyên technology matrix và safety boundaries. | Technical Operator | Account Owner decision `2026-08-12T11:15:53Z` |
| 0.1.0 | 2026-07-31 | Tạo technology/language/repository baseline bám master v2.0. | Technical Operator | Pending |
| 0.2.0 | 2026-07-31 | Làm rõ provider-neutral BYOK: OpenAI SDK chỉ là adapter tùy chọn ở Phase 6. | Technical Operator | Pending |
| 0.3.0 | 2026-07-31 | Thêm §8 Runtime và tooling decisions bổ sung (DRAFT — cần Account Owner phê duyệt trước Task 0.1/0.2); thêm Import Linter vào technology matrix §2 (master §13.1). | Technical Operator | Pending |
| 0.3.1 | 2026-08-01 | Sửa cây tests/ trong §4 khớp master §4.6 v2.2.0: bổ sung `state_machine/`, `fixtures/`, `factories/` (trước đó thiếu — mâu thuẫn với ENG-REPO-001 và master). | Technical Operator | Pending |
| 0.3.2 | 2026-08-02 | Thêm câu tracking vào lead-in §8: cụm quyết định theo dõi qua RAID I-008; package ngoài allowed list cần amendment ADR-0014/ADR mới theo trigger §9 trước Task 0.2; Task 0.1 không bị ảnh hưởng (runtime dependencies rỗng theo ENG-PY-001 §5a-ref). | Technical Operator | Pending |
