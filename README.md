# AI Auto Trade

Nền tảng giao dịch thuật toán crypto spot (Python 3.12 / PostgreSQL 17 / FastAPI) — modular monolith, hexagonal, event-driven có chọn lọc, ưu tiên an toàn/audit/recovery hơn tốc độ ra tính năng.

| Thuộc tính | Giá trị |
|---|---|
| Trạng thái | **Phase 1 — Core safety (IN_PROGRESS)** — Gate Phase 0.0 APPROVED/REVALIDATED 2026-08-10T20:07:02Z. Task 0.1–0.4, 0.0.7, 0.5.1, 0.5.2, 0.6, 1.1, 1.2, 1.3, 1.3.1 và 1.3.2 DONE; Enterprise-Grade one-time approval packet đã được Account Owner approve bounded local-only lúc 2026-08-14T21:24:41Z. OD-001 vẫn OPEN cho external venue; ledger activation còn gated bởi accounting annex. |
| Hiến pháp kỹ thuật | [AI_AUTO_TRADE_MASTER_SPEC.md](AI_AUTO_TRADE_MASTER_SPEC.md) |
| Gate gần nhất | Phase 0.0 — PASSED 2026-08-06 ([gate record](docs/governance/evidence/gates/phase-0.0/gate-record.md)) |
| Quy tắc an toàn | Không có lệnh live trước khi vượt toàn bộ Go/No-Go gate |

## Thứ tự đọc bắt buộc

1. **[AI_AUTO_TRADE_MASTER_SPEC.md](AI_AUTO_TRADE_MASTER_SPEC.md)** — master specification; bắt đầu từ §0 control panel để biết phase hiện tại, blocker và việc kế tiếp.
2. **[AGENTS.md](AGENTS.md)** — AI coding agent rules (enforced); bản rút gọn có thể thực thi của master §16, bắt buộc cho mọi AI coding agent trước khi chạm vào bất kỳ file nào.
3. **[docs/governance/DOCS_INDEX.md](docs/governance/DOCS_INDEX.md)** — chỉ mục toàn bộ artifact pack và trạng thái review từng tài liệu.
4. **Task card hiện hành** trong [tasks/active/](tasks/active/) — authority phạm vi duy nhất; không có task card READY thì không được sửa implementation file.

OpenAI Codex phải đọc `AGENTS.md` ở root trước khi sửa. `AGENTS.md` là instruction source chính; tài liệu này không cấp quyền vượt master, ADR, contract, gate hoặc task card. “OpenAI-compatible” ở Phase 0 chỉ là quy trình Codex có thể thực thi được, không phải cho phép thêm OpenAI runtime/API.

## Quick-start

```bash
# Prerequisites: Python 3.12.x, uv
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv run python scripts/validate_contracts.py
```

## Cấu trúc repository

```text
AI_AUTO_TRADE_MASTER_SPEC.md   # hiến pháp kỹ thuật — nguồn sự thật cao nhất sau regulatory
AGENTS.md                      # quy tắc bắt buộc cho AI coding agent (rút gọn §16)
docs/
  governance/                  # document control, RACI, traceability, DOCS_INDEX, layer classification, waiver/compliance register, ADR registry, templates, evidence
  shared/                      # glossary, non-functional requirements (áp dụng cả backend/frontend)
  backend/                     # product, architecture, domain, data, engineering, security-ops, ADR content
  frontend/                    # bộ tài liệu Flutter dashboard (FE-*-001, input Phase 5/6 — chưa cho phép code)
contracts/                     # OpenAPI 3.1, JSON Schema (command/event/config), error catalog, fixtures
tasks/                         # task card YAML — authority phạm vi thực thi (validate bằng task-card schema)
```

`src/`, `tests/`, `migrations/`, `.github/` đã được tạo bởi Task 0.1–0.4. `configs/services/control-api.yaml` được tạo trong phạm vi Task 0.5.2; `infra/` chưa tồn tại theo chủ đích và chỉ được tạo bởi task card tương ứng ở phase sau, khi ADR bắt buộc được APPROVED.

## Trạng thái Phase 0

- Task 0.1–0.4: **DONE** (Account Owner approve 2026-08-06) — card trong [tasks/completed/](tasks/completed/), evidence trong [docs/governance/evidence/tasks/](docs/governance/evidence/tasks/).
- Task 0.0.7 — Codex Enterprise documentation: **DONE**, docs-only; evidence tại `docs/governance/evidence/tasks/0.0.7/`.
- Task 0.5.1 — Config/audit/error envelope: **DONE**, card trong `tasks/completed/`, Account Owner approve `2026-08-11T00:30:47Z`.
- Task 0.5.2 — Control API skeleton: **DONE** (Account Owner xác định `2026-08-11T02:14:42Z`); local-only, không auth/venue/DB thật.
- Task 0.6 — Capability draft: **DONE**, card trong `tasks/completed/`; matrix local simulator/no venue đã tạo.
- Phase 1 — Task 1.1 deterministic primitives: **DONE**, card trong `tasks/completed/`; chưa OMS/risk/ledger/venue.
- Phase 1 — Task 1.2 OMS deterministic state machine: **DONE**, card trong `tasks/completed/`; chưa durable DB submit/ledger runtime.
- Phase 1 — Task 1.3 durable submit/fake venue: **DONE** (Account Owner xác nhận `2026-08-13T14:40:01Z`); local-only, không mở external venue/ledger/AI execution.
- Phase 1 — Task 1.3.1 evidence redaction cleanup: **DONE** (Account Owner xác nhận `2026-08-14T04:48:21Z`).
- Phase 1 — Task 1.3.2 durable-submit hardening: **DONE** (Account Owner xác nhận `2026-08-14T17:03:06Z`); chỉ local persistence/recovery/fault-injection, không mở external venue/ledger/AI execution.
- Enterprise-Grade one-time approval packet: [approved packet](docs/governance/evidence/tasks/1.3.2/enterprise-grade-one-time-approval-packet-2026-08-15.md); Account Owner approve bounded local-only continuation, không mở các gate rủi ro cao.
- OD-001 — external venue/testnet: **OPEN**; local simulator không thay thế quyết định venue.
- Không có card `READY` phù hợp thì AI không sửa implementation file (master §16).

## Đóng góp và bảo mật

- Quy tắc commit/branch/PR: [CONTRIBUTING.md](CONTRIBUTING.md)
- Chính sách bảo mật và báo cáo lỗ hổng: [SECURITY.md](SECURITY.md)
- Review matrix theo vùng: [CODEOWNERS](CODEOWNERS)

> Tài liệu này là đặc tả kỹ thuật, không phải lời khuyên đầu tư.
