# Task 1.3 — Preflight validation evidence

| Trường | Giá trị |
|---|---|
| Document ID | GOV-TASK-1.3-VALIDATION-20260812 |
| Phiên bản | 0.3.1 |
| Trạng thái | DRAFT — validation evidence, không phải gate approval |
| Task scope | Task 1.3 preflight + Enterprise-Grade closure addendum; implementation vẫn BLOCKED |
| Branch | `task/1.3-durable-submit-fake-venue` |
| UTC run | 2026-08-12T07:53:19Z và các lệnh kế tiếp trong cùng phiên |
| Working tree policy | Docs-only changes; không thay `src/`, `tests/`, `migrations/`, `configs/`, `contracts/` |

## 1. Commands and results

| Command | Exit/result |
|---|---|
| `git diff --check` | PASS |
| `uv sync --locked` | PASS — resolved/checked 45 packages |
| `uv run ruff format --check .` | PASS — 214 files already formatted |
| `uv run ruff check .` | PASS — all checks passed |
| `uv run pyright` | PASS — 0 errors, warnings, informations |
| `uv run pytest` | PASS — 103 passed, 1 skipped |
| `uv run python scripts/validate_contracts.py` | PASS — all 14 JSON Schemas valid |
| `uv run python -c "json.loads(...)"` | PASS — 3 new draft JSON artifacts parse |
| `uv run python -c "jsonschema.Draft202012Validator(...).validate(...)"` | PASS — fake venue draft fixture conforms to draft schema |

## 2. Skip detail

Một integration test PostgreSQL vẫn `skipped` do môi trường chưa có `DATABASE_URL`. Đây là blocker evidence cho persistence/concurrency implementation, không được báo cáo là database integration đã pass.

## 3. Scope check

Các file mới/chỉnh trong lần chuẩn bị này chỉ thuộc governance/authority documentation và task control:

- `AGENTS.md`
- `AI_AUTO_TRADE_MASTER_SPEC.md`
- `docs/backend/adr/0012-transaction-concurrency.md`
- `docs/backend/contracts/contract-registry.md`
- `docs/backend/data/data-dictionary.md`
- `docs/backend/data/erd.md`
- `docs/backend/domain/canonical-domain-model.md`
- `docs/backend/domain/risk-policy.md`
- `docs/governance/DOCS_INDEX.md`
- `docs/governance/evidence/tasks/1.3/task-1.3-preflight.md`
- `docs/governance/evidence/tasks/1.3/owner-decision-register.md`
- `docs/governance/evidence/tasks/1.3/risk-fill-concurrency-closure.md`
- `docs/governance/evidence/tasks/1.3/data-persistence-closure.md`
- `docs/governance/evidence/tasks/1.3/fake-venue-closure.md`
- `docs/governance/evidence/tasks/1.3/enterprise-control-closure-matrix.md`
- `docs/governance/evidence/tasks/1.3/enterprise-readiness-audit.md`
- `docs/governance/evidence/tasks/1.3/ONE-TIME-APPROVAL-PACKET.md` v0.3.0
- `docs/governance/evidence/tasks/1.3/approval-record-2026-08-12.md`
- `docs/governance/evidence/tasks/1.3/risk-profile.local-simulator.v1.approved.json`
- `docs/governance/evidence/tasks/1.3/fake-venue-scenario.v1.schema.json`
- `docs/governance/evidence/tasks/1.3/fake-venue-scenario.v1.valid.json`
- `docs/governance/evidence/tasks/1.3/execution-risk-dictionary-addendum.md`
- `docs/governance/evidence/tasks/1.3/task-1.3-traceability-matrix.md`
- `docs/governance/evidence/tasks/1.3/task-1.3-runbook-drill-plan.md`
- `tasks/active/1.3-durable-submit-fake-venue.yaml`
- `tasks/completed/0.0.7-codex-enterprise-docs.yaml` (reconciled from `tasks/active/`)
- Tài liệu evidence này

Không có diff trong `src/`, `tests/`, `migrations/`, `configs/`, `contracts/` hoặc dependency/lockfile.

## 4. Readiness decision

Kết quả validation kỹ thuật của repo hiện tại là xanh, nhưng Definition of Ready của Task 1.3 vẫn **chưa đạt** vì:

- Task card implementation đã tạo nhưng đang `BLOCKED`, chưa `READY`.
- P-01..P-68 đã được ghi nhận approval trong [approval record](approval-record-2026-08-12.md) lúc `2026-08-12T09:19:16Z`; task-scoped authority references đã đồng bộ.
- Access/backup/security controls trong P-50..P-56/P-60 đã có dual-role record; runtime security evidence vẫn pending.
- P-68 task-directory hygiene đã hoàn tất: card `0.0.7` đã chuyển sang `tasks/completed/`.
- Risk policy, canonical Fill, data dictionary, ERD và fake venue harness vẫn DRAFT.
- Contract registry vẫn IN_REVIEW.
- ADR-0012 cần amendment/clarification.
- PostgreSQL integration chưa chạy do thiếu `DATABASE_URL`.

Đề xuất trạng thái: `BLOCKED` cho implementation; `IN_REVIEW` cho bộ preflight docs; approval, task-scoped authority references, branch `task/1.3-*` và clean reviewed tree đã có nhưng chưa có PostgreSQL no-skip evidence. Không tự chuyển card sang `READY`.
