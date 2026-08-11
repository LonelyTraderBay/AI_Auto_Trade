# Evidence — Task 1.1 deterministic primitives

| Trường | Giá trị |
|---|---|
| Task | `1.1` |
| Phase | `1` — Core safety |
| Card status | `DONE` |
| Branch | `task/1.1-deterministic-primitives` |
| Owner / reviewer | Technical Operator / Account Owner |
| Scope decision | Local simulator/no venue; Account Owner `2026-08-11T19:16:45Z` |
| Execution started | `2026-08-11T19:20:37Z` |
| Evidence timestamp | `2026-08-11T19:26:49Z` |
| Owner decision | Account Owner xác nhận `DONE` lúc `2026-08-11T19:41:38Z` |
| Gate impact | Phase 1; không tự approve gate |

## Đã thực hiện

- `identity.py`: generate/parse canonical UUIDv7, timestamp millisecond, RFC 4122 variant.
- `decimal_value.py`: parse/serialize Decimal finite, không exponent khi serialize, scale tối đa 18, không nhận binary float.
- `clock.py`: `Clock` protocol, `SystemClock` UTC và `FixedClock` cho test/replay.
- `random_source.py`: `RandomSource` protocol và `SeededRandomSource` cô lập khỏi module-global random.
- Bổ sung unit tests cho valid/invalid UUIDv7, Decimal boundary, UTC/fixed clock và deterministic random.

## Quality commands

| Command | Result |
|---|---|
| `uv sync --locked` | PASS — lock đã đồng bộ |
| `uv run ruff format --check .` | PASS — 195 files already formatted |
| `uv run ruff check .` | PASS |
| `uv run pyright` | PASS — 0 errors, 0 warnings, 0 informations |
| `uv run pytest` | PASS — 52 passed, 1 skipped |
| `uv run python scripts/validate_contracts.py` | PASS — 14 JSON Schemas hợp lệ |
| `git diff --check` | PASS — không có whitespace error; chỉ có cảnh báo LF/CRLF của Git |

## Security and scope checks

- Không có secret, credential, API key, network client, venue SDK, database access hoặc LLM path.
- Không sửa public contract, migration, dependency, lockfile, config, adapter, app hoặc context domain.
- `SeededRandomSource` chỉ dành cho deterministic simulator/test; không dùng làm security entropy hoặc credential generator.
- Task không implement OMS, risk, ledger, reconciliation hoặc execution lifecycle.

## Artifact hashes (SHA-256)

| Path | SHA-256 |
|---|---|
| `src/ai_auto_trade/shared_kernel/identity.py` | `5823AF37D30EAA2FF294434535C857C9A5E3CC3C2C1D7547DC0F02B5C6E65A68` |
| `src/ai_auto_trade/shared_kernel/decimal_value.py` | `C9DACAC240A14B6DDF4CEB4BE7C7E3368C1FDD77FD0697AE2F4A0DD5010EA3ED` |
| `src/ai_auto_trade/shared_kernel/clock.py` | `62E949525262FB2C1E5347697D06ED3101B00D45E0F9B182798F1E5BCEB293CE` |
| `src/ai_auto_trade/shared_kernel/random_source.py` | `804AD7A285A421899FC06EA7FF1CD13EE225E93C9934C1994FECA0E84C652174` |
| `tests/unit/shared_kernel/test_identity.py` | `E85740867DC78149D99F6184F084FEB7D7F1A6CC2891CD397CF7C43584F7AE7F` |
| `tests/unit/shared_kernel/test_decimal_value.py` | `0913DF5BD93993A32E0E8A216748446780C8F36119F57F881FBA12F8F6C20D4E` |
| `tests/unit/shared_kernel/test_clock.py` | `4827BECD6DA7E47BE743D8D387B47F68018D5E8E2292982E9704705425A2A28D` |
| `tests/unit/shared_kernel/test_random_source.py` | `DED6B5E20D275EE72497CA59F472A73D8221530457567D1ECC980F79D0E34436` |

## Operator handoff

Account Owner đã nghiệm thu và xác nhận card `DONE` lúc `2026-08-11T19:41:38Z` sau
khi toàn bộ acceptance commands PASS. Task không mở OMS/risk/ledger/venue.
