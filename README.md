# AI Auto Trade

Nền tảng giao dịch thuật toán crypto spot (Python 3.12 / PostgreSQL 16 / FastAPI) — modular monolith, hexagonal, event-driven có chọn lọc, ưu tiên an toàn/audit/recovery hơn tốc độ ra tính năng.

| Thuộc tính | Giá trị |
|---|---|
| Trạng thái | **Phase 0 — Foundation (IN_PROGRESS)** — Gate Phase 0.0: PASSED 2026-08-06. Task 0.1–0.4 DONE; việc kế tiếp: Task 0.5 — Operations skeleton (chờ task card). |
| Hiến pháp kỹ thuật | [AI_AUTO_TRADE_MASTER_SPEC.md](AI_AUTO_TRADE_MASTER_SPEC.md) |
| Gate gần nhất | Phase 0.0 — PASSED 2026-08-06 ([gate record](docs/governance/evidence/gates/phase-0.0/gate-record.md)) |
| Quy tắc an toàn | Không có lệnh live trước khi vượt toàn bộ Go/No-Go gate |

## Thứ tự đọc bắt buộc

1. **[AI_AUTO_TRADE_MASTER_SPEC.md](AI_AUTO_TRADE_MASTER_SPEC.md)** — master specification; bắt đầu từ §0 control panel để biết phase hiện tại, blocker và việc kế tiếp.
2. **[AGENTS.md](AGENTS.md)** — AI coding agent rules (enforced); bản rút gọn có thể thực thi của master §16, bắt buộc cho mọi AI coding agent trước khi chạm vào bất kỳ file nào.
3. **[docs/governance/DOCS_INDEX.md](docs/governance/DOCS_INDEX.md)** — chỉ mục toàn bộ artifact pack và trạng thái review từng tài liệu.
4. **Task card hiện hành** trong [tasks/active/](tasks/active/) — authority phạm vi duy nhất; không có task card READY thì không được sửa implementation file.

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

`src/`, `tests/`, `migrations/`, `.github/` đã được tạo bởi Task 0.1–0.4. `configs/` và `infra/` **chưa tồn tại theo chủ đích** — chúng chỉ được tạo bởi task card tương ứng ở phase sau, khi ADR bắt buộc được APPROVED.

## Trạng thái Phase 0

- Task 0.1–0.4: **DONE** (Account Owner approve 2026-08-06) — card trong [tasks/completed/](tasks/completed/), evidence trong [docs/governance/evidence/tasks/](docs/governance/evidence/tasks/).
- `tasks/active/` đang trống: Task 0.5 — Operations skeleton (master §14) chưa có task card. Không có card `READY` thì AI không sửa implementation file (master §16).

## Đóng góp và bảo mật

- Quy tắc commit/branch/PR: [CONTRIBUTING.md](CONTRIBUTING.md)
- Chính sách bảo mật và báo cáo lỗ hổng: [SECURITY.md](SECURITY.md)
- Review matrix theo vùng: [CODEOWNERS](CODEOWNERS)

> Tài liệu này là đặc tả kỹ thuật, không phải lời khuyên đầu tư.
