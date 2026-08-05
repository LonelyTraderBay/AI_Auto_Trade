# ADR-0014 — Toolchain, repository topology, language policy and contract authority

| Thuộc tính | Giá trị |
|---|---|
| ADR ID | ADR-0014 |
| Phiên bản | 0.1.0 |
| Status | DRAFT — required for Phase 0.0; chưa mở gate |
| Date | 2026-07-31 |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Effective date | Chưa hiệu lực (chỉ điền khi APPROVED) |
| Decision deadline | Phase 0.0 gate |
| Rà soát gần nhất | 2026-08-02 |
| Related | NFR-DET-001, NFR-AUD-001, NFR-SEC-001, NFR-OPS-001; [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §1.5–§1.6, §3.5, §4.6–§4.8, §7.13, §13, §16 |
| Supersedes / superseded by | None / None |
| Change summary | 0.1.0 (2026-08-02): chuẩn hóa header theo TMP-ADR-001/GOV-DOC-001 §3 — thêm ADR ID/Phiên bản/Effective date/Decision deadline/Rà soát/Change summary (audit toàn diện); nội dung quyết định không đổi (soạn 2026-07-31). |

## Context and decision drivers

AI-assisted implementation needs narrow, executable authority so it cannot substitute libraries, languages, folder layouts, contracts or undocumented assumptions. Reproducible build/test/review and a clear source-of-truth hierarchy are necessary before code/migration/API is allowed.

## Proposed decision

If approved, MVP uses Python 3.12.x for domain/application/ports/adapters/API/workers/CLI/tests; `uv`, `pyproject.toml` and locked dependency file for reproducible environment; Pyright strict as the one type checker; Ruff/pytest/Hypothesis as listed in Master. PostgreSQL SQL is restricted to reviewed migrations/repositories; YAML is non-secret validated config; JSON Schema/OpenAPI define wire contracts; Markdown defines governance/ADR/runbook, not runtime config.

Repository topology is exactly Master §4.6: context layers under `src/ai_auto_trade/contexts`, concrete adapters globally under `adapters/<kind>/<provider>`, apps as composition roots, versioned `contracts/`, controlled `docs/`, `tasks/`, migrations/config/test topology. Public HTTP is OpenAPI 3.1; command/event/config use JSON Schema 2020-12. Authority order is regulatory constraint -> Master + APPROVED ADR -> versioned executable DDL/schema/manifest -> approved task/gate -> code -> test/log.

Additional language/runtime/database/broker/framework is forbidden by default and needs ADR, owner, security/operations/dependency review and phase gate. Node/TypeScript/Go/Rust/Java/Redis/Kafka/NATS/Kubernetes are not convenience additions for MVP.

Executable reference block cho toolchain config: ENG-PY-001 §5a/§5a-ref (pyproject.toml là config authority; Task 0.1 tái tạo khối chuẩn). Runtime/IO client selection (asyncio/httpx/websockets/uvicorn/OTel — ARC-TECH-001 §8) cần amendment ADR này hoặc ADR riêng trước Task 0.2 (RAID I-008).

## Alternatives considered

| Alternative | Why not proposed |
|---|---|
| Let each task pick “best” tool/language | AI-driven drift, duplicated toolchains and non-reproducible review |
| Docs only as authority | code/API/DDL details need machine-readable validation |
| ORM model as public contract | couples consumers to internal persistence and misses compatibility/versioning |
| Unlocked dependencies | rebuild behavior/security surface changes over time |

## Consequences

Task cards contain allowed/forbidden paths, required commands and references. CI validates task/schema/contract/allowlist before merge. `Any`, type-ignore/noqa, broad/bare exception, test skip/xfail and unapproved dependency are prohibited for safety work absent a valid waiver. Bootstrap exception is only the Master-authorized Task 0.0.0 document/contract/task scope; it permits no runtime/database code.

## Migration, rollout and rollback/forward-fix

Phase 0 creates tooling/topology/CI incrementally under approved task cards. A toolchain change is a breaking engineering control: make a new ADR, assess lockfile/security/CI/developer migration, run compatibility evidence and retain rollback/forward-fix plan. No unreviewed global rewrite.

## Approval criteria

- [ ] Account Owner accepts the language/tooling/authority hierarchy and forbidden-by-default rule.
- [ ] Repository conventions, coding standards, CI/test and AI protocol contain executable links to this ADR.
- [ ] Task 0.1/0.2 card acceptance can be verified with exact locked commands.

