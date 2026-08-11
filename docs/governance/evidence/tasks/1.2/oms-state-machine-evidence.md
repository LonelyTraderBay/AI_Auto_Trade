# Evidence — Task 1.2 OMS deterministic state machine

| Trường | Giá trị |
|---|---|
| Task | `1.2` |
| Phase | `1` — Core safety |
| Card status | `DONE` |
| Branch | `task/1.2-oms-state-machine` |
| Owner / reviewer | Technical Operator / Account Owner |
| Normative baseline | DOM-OMS-001 v0.3.1, DATA-TXN-001 v0.2.1, DOM-ACC-001 v0.2.1; Account Owner `2026-08-11T19:52:15Z` |
| Execution started | `2026-08-11T19:55:00Z` |
| Evidence timestamp | `2026-08-11T19:57:56Z` |
| Owner decision | Account Owner xác nhận `DONE` lúc `2026-08-11T20:06:59Z` |
| Gate impact | Phase 1; không tự approve gate hoặc chuyển DONE |

## Đã thực hiện

- `order_lifecycle.py`: typed `OrderState`, `OrderLifecycleEvent`, approved transition map và terminal-correction guard.
- Reject fail-closed mọi state/event mismatch, duplicate/out-of-order event, terminal-to-non-terminal event và transition PROPOSED tại DOM-OMS-001 §3a.
- Pure deterministic domain code; không database, network, venue, risk engine, ledger runtime, wall clock hoặc global random.
- Unit tests bao phủ allowed transitions, invalid/duplicate/out-of-order, §3a rejection và terminal correction.

## Quality commands

| Command | Result |
|---|---|
| `uv sync --locked` | PASS — lock đã đồng bộ |
| `uv run ruff format --check .` | PASS — 198 files already formatted |
| `uv run ruff check .` | PASS |
| `uv run pyright` | PASS — 0 errors, 0 warnings, 0 informations |
| `uv run pytest` | PASS — 103 passed, 1 skipped |
| `uv run python scripts/validate_contracts.py` | PASS — 14 JSON Schemas hợp lệ |
| `git diff --check` | PASS |

## Security and scope checks

- Không có secret, credential, API key, network client, venue SDK, database access hoặc LLM path.
- Không sửa public contract, migration, dependency, config, adapter, application hoặc ledger/risk implementation.
- Không mở durable submit protocol; đây là state validation slice duy nhất.

## Artifact hashes (SHA-256)

| Path | SHA-256 |
|---|---|
| `src/ai_auto_trade/contexts/execution/domain/order_lifecycle.py` | `9C25794275C106B005260A24649D30CCBBBC5A33A528CA0E9DB43EA21F3F423C` |
| `tests/unit/contexts/execution/test_order_lifecycle.py` | `E330A430AFF3DA69A5A0DB5B8D1F8350BE73F412E8278EA14EC34E07D8407009` |

## Operator handoff

Implementation và evidence đã đủ acceptance commands. Account Owner đã nghiệm thu
code/evidence và xác nhận card `DONE` lúc `2026-08-11T20:06:59Z`. Task tiếp theo
mới được mở cho durable submit/fake venue sau task card riêng.
