# AI Auto Trade

Nền tảng giao dịch thuật toán crypto spot (Python 3.12 / PostgreSQL 16 / FastAPI) — modular monolith, hexagonal, event-driven có chọn lọc, ưu tiên an toàn/audit/recovery hơn tốc độ ra tính năng.

| Thuộc tính | Giá trị |
|---|---|
| Trạng thái | **Phase 0.0 — Documentation Closure (IN_REVIEW)** — repo chỉ có tài liệu/contract, **chưa có application code** |
| Hiến pháp kỹ thuật | [AI_AUTO_TRADE_MASTER_SPEC.md](AI_AUTO_TRADE_MASTER_SPEC.md) |
| Gate hiện tại | Phase 0.0 — NOT PASSED ([gate record](docs/governance/evidence/gates/phase-0.0/gate-record.md)) |
| Quy tắc an toàn | Không có lệnh live trước khi vượt toàn bộ Go/No-Go gate |

## Thứ tự đọc bắt buộc

1. **[AI_AUTO_TRADE_MASTER_SPEC.md](AI_AUTO_TRADE_MASTER_SPEC.md)** — bắt đầu từ §0 control panel để biết phase hiện tại, blocker và việc kế tiếp.
2. **[AGENTS.md](AGENTS.md)** — bản rút gọn có thể thực thi của master §16, bắt buộc cho mọi AI coding agent trước khi chạm vào bất kỳ file nào.
3. **[docs/governance/DOCS_INDEX.md](docs/governance/DOCS_INDEX.md)** — chỉ mục toàn bộ artifact pack và trạng thái review từng tài liệu.
4. **Task card hiện hành** trong [tasks/active/](tasks/active/) — authority phạm vi duy nhất; không có task card READY thì không được sửa implementation file.

## Cấu trúc repository

```text
AI_AUTO_TRADE_MASTER_SPEC.md   # hiến pháp kỹ thuật — nguồn sự thật cao nhất sau regulatory
AGENTS.md                      # quy tắc bắt buộc cho AI coding agent (rút gọn §16)
docs/
  governance/                  # document control, RACI, traceability, ADR registry, templates, evidence
  shared/                      # glossary, non-functional requirements (áp dụng cả backend/frontend)
  backend/                     # product, architecture, domain, data, engineering, security-ops, ADR content
  frontend/                    # trống có chủ đích — Flutter dashboard hoãn tới Phase 5
contracts/                     # OpenAPI 3.1, JSON Schema (command/event/config), error catalog, fixtures
tasks/                         # task card YAML — authority phạm vi thực thi (validate bằng task-card schema)
```

`src/`, `migrations/`, `configs/`, `tests/`, `.github/` **chưa tồn tại theo chủ đích** — chúng chỉ được tạo từ Task 0.1 trở đi, sau khi gate Phase 0.0 PASSED và các ADR bắt buộc được APPROVED.

## Bootstrap (chỉ hiệu lực từ khi Task 0.1 DONE)

```bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

Trước thời điểm đó, không có lệnh build/test nào để chạy — mọi validation là schema/link check trên tài liệu và contract (xem gate record Phase 0.0).

## Đóng góp và bảo mật

- Quy tắc commit/branch/PR: [CONTRIBUTING.md](CONTRIBUTING.md)
- Chính sách bảo mật và báo cáo lỗ hổng: [SECURITY.md](SECURITY.md)
- Review matrix theo vùng: [CODEOWNERS](CODEOWNERS)

> Tài liệu này là đặc tả kỹ thuật, không phải lời khuyên đầu tư.
