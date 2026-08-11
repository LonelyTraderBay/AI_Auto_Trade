# Evidence — Task 0.5.2 Local-only Control API skeleton

| Trường | Giá trị |
|---|---|
| Task | `0.5.2` |
| Phase | `0` — Foundation |
| Branch | `task/0.5.2-control-api` |
| Card status | `DONE` |
| Operator | Technical Operator |
| Reviewer | Account Owner |
| Owner opening decision | `2026-08-11T00:30:47Z` |
| Owner completion decision | `2026-08-11T02:14:42Z` — Account Owner xác định DONE |
| Gate | Phase 0.0 `APPROVED / REVALIDATED` — `2026-08-10T20:07:02Z` |
| Evidence timestamp | `2026-08-11` (Asia/Bangkok) |

## Phạm vi và truy vết

Task triển khai composition root FastAPI local-only theo `contracts/api/openapi.yaml`:
health, readiness, runtime, command intake stubs và command status projection.
ADR-0001/0002/0014 được giữ nguyên: app là modular-monolith composition root,
domain không nhận framework/vendor dependency và không có external side effect.

Task 0.5.1 đã được Account Owner approve trước khi mở task này; error envelope
và audit/error primitives được tái sử dụng từ commit `f56f2c7`.

## Thay đổi đã thực hiện

- Thêm `src/ai_auto_trade/apps/control_api/app.py` với `create_app()` và module
  `app` để chạy bằng Uvicorn trên localhost.
- Expose `GET /health`, `GET /readiness`, `GET /runtime`; runtime chỉ trả
  `local/BACKTEST/INTERNAL_SIMULATOR`, UUIDv7 deployment ID và manifest hash,
  không trả credential/venue state.
- Expose `POST /commands/reconciliations`, `/strategy-activations`,
  `/strategy-stops`, `/kill-switch-activations`, `/kill-switch-releases`,
  `/backtests`; mỗi route chỉ tạo projection `ACCEPTED` trong memory, trả `202`
  và `Location`, không thực thi command/worker/venue operation.
- Expose `GET /commands/{command_id}` cho projection trong memory; unknown route,
  validation và command-not-found đều dùng safe error envelope.
- Auth/RBAC là `NOOP_STUB`, không đọc/ghi token hoặc identity claim; proof header
  kill-switch release chỉ được parse, không log/persist/evaluate.
- Thêm config `configs/services/control-api.yaml` với bind `127.0.0.1`,
  `IN_MEMORY_PROJECTION`, `external_io=false`.
- Khóa dependency theo PyPI primary metadata: FastAPI `0.139.2`, Uvicorn
  `0.51.0`, HTTPX `0.28.1` (HTTPX chỉ dùng ASGI contract tests); toàn bộ lock
  được ghi trong `uv.lock`.

## Lệnh bắt buộc và kết quả

| Lệnh | Kết quả |
|---|---|
| `uv sync --locked` | PASS — resolved/checked 45 packages |
| `uv run ruff format --check .` | PASS — 186 files already formatted |
| `uv run ruff check .` | PASS — All checks passed |
| `uv run pyright` | PASS — 0 errors, 0 warnings, 0 informations |
| `uv run pytest` | PASS — 32 passed, 1 skipped |
| `uv run python scripts/validate_contracts.py` | PASS — all 14 JSON Schema files valid |
| `uv run uvicorn --version` | PASS — Uvicorn `0.51.0` |
| Uvicorn localhost smoke (`127.0.0.1:8766/health`) | PASS — HTTP `200`, sanitized health payload |
| `git diff --check` | PASS — chỉ cảnh báo LF/CRLF conversion của Git |

## Contract/security checks

- App OpenAPI generated component có `ErrorEnvelope`; required route set gồm 10
  paths và command POST routes có `202`/`Location`.
- Negative tests bao phủ invalid body/secret-like reason, unknown route và
  command projection lookup; lỗi không echo raw input/stack trace.
- Không có database/migration, venue adapter, exchange SDK, LLM provider,
  notification channel, public bind hoặc real authentication.
- Không có secret/API key/password/token trong code, config, fixture, log hoặc
  evidence. `auth_mode=NOOP_STUB` và `external_io=false` là non-secret markers.

## Artifact hashes (SHA-256)

| Path | SHA-256 |
|---|---|
| `pyproject.toml` | `8885445DA75308AEDBD3F243DB8EFB278A111D6EF6FD89BBEA5041DC5DB784FD` |
| `uv.lock` | `D85506AB591775C6C7B7FA42DAFDD6035580A8AE3547C1EF4D036F5842844EE7` |
| `tasks/completed/0.5.2-control-api-skeleton.yaml` | `D5CB669FC2BAC3D10025FEA28264364CBCF10F2D8B74B651E4F785437BF5BB47` |
| `configs/services/control-api.yaml` | `05264C79502525FAAD22FF6D52F667F1BD71A94BBA87E9745CAE36DABF68B034` |
| `src/ai_auto_trade/apps/control_api/app.py` | `463D311C84922EDFA00C48C5FF4F6BE3461BAEACB7E2C6867AB759144A72B56B` |
| `tests/unit/apps/test_control_api.py` | `5AF39B3CAD36E529F0A45941C2C564BC72D52D6825A8B332D533332E58D453C2` |
| `tests/contract/test_control_api_contract.py` | `C0F67C99E43715B86D0B0CF5073747D16815F7C91F1D32354B24A1464A6EDDB9` |

## Known limits và forward fix

- Đây là local-only skeleton; chưa có auth/RBAC thực, durable command/idempotency
  store, DB projection, background worker hay command handler.
- Không thêm `httpx2` chỉ để né deprecation của Starlette TestClient; tests dùng
  HTTPX ASGI transport trực tiếp và không tạo production client.
- Task 0.5.2 không mở endpoint order/venue/AI và không thay đổi safety gate.

## Quyết định nghiệm thu

Account Owner xác định Task 0.5.2 **DONE** tại `2026-08-11T02:14:42Z`.
Card được chuyển `REVIEW -> DONE` và đã được lưu tại `tasks/completed/`.
Không có waiver; các giới hạn local-only/no-auth/no-venue/no-DB và forward fix
được chấp nhận trong phạm vi Phase 0 skeleton.
