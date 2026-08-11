# Capability matrix — Internal simulator v1 (DRAFT)

| Trường | Giá trị |
|---|---|
| Task | `0.6` |
| Matrix ID | `internal-simulator.v1-draft` |
| Profile scope | Local `PAPER_SIMULATOR` / `BACKTEST` only |
| Execution target | `INTERNAL_SIMULATOR` |
| Owner | Technical Operator |
| Owner decision | Account Owner xác nhận local simulator/no venue tại `2026-08-11T02:26:26Z` |
| Effective time | `2026-08-11T02:26:26Z` |
| Status | `DRAFT` — không phải venue approval, không mở Phase 3 |
| External I/O | `false` |
| Credential class | `NONE` |

## Matrix theo Master §10.3

| Dimension | Giá trị/giới hạn local simulator | Source/effective time | Test evidence | Status |
|---|---|---|---|---|
| Market/instrument | Chỉ dữ liệu tổng hợp/replay fixture; không biểu diễn instrument của venue thật; precision/min-notional thật chưa được chọn | `contracts/fixtures/deployment-manifest.v1.paper.valid.yaml`; effective `2026-08-11T02:26:26Z` | `scripts/validate_contracts.py`; fixture validation | `supported` cho synthetic only; external `DEFERRED` |
| Order | Control API chỉ nhận command projection/stub; chưa submit, cancel, fill hoặc direct replace; không có đường tới venue | `docs/governance/evidence/tasks/0.5.2/control-api-evidence.md` | `tests/unit/apps/test_control_api.py`; `tests/contract/test_control_api_contract.py` | `supported` cho intake projection; execution `DEFERRED` |
| Recovery | Không có durable order store, reconciliation worker hoặc unknown-outcome recovery trong profile này | Task 0.5.2 known limits; effective `2026-08-11T02:26:26Z` | Chưa có conformance evidence; không claim pass | `DEFERRED` |
| Rate/availability | Không network, không endpoint, không rate limit venue; local process chỉ bind loopback theo control-api config | `configs/services/control-api.yaml`; effective `2026-08-11T02:26:26Z` | Control API localhost smoke trong Task 0.5.2 evidence | `supported` cho local-only; external `NOT_APPLICABLE` |
| Account | `SIMULATED`, không account/sub-account thật, không credential, không withdrawal hoặc settlement bên ngoài | `contracts/fixtures/deployment-manifest.v1.paper.valid.yaml`; effective `2026-08-11T02:26:26Z` | Deployment-manifest schema validation | `supported` cho synthetic account; external `DEFERRED` |

## Ranh giới bắt buộc

- `OD-001` (external venue/testnet), `OD-002` (jurisdiction) và `OD-003` (account/instrument scope) vẫn `OPEN`; matrix này không giải quyết hoặc giả định các quyết định đó.
- Các giá trị synthetic trong fixture chỉ phục vụ schema/contract validation; không phải venue ID, account ID hay capability profile của sàn thật.
- Không được dùng matrix này để bật `TESTNET`, `CANARY`, `FULL_LIVE`, `VENUE_TESTNET` hoặc `VENUE_LIVE`.
- Chưa có adapter conformance, submit/cancel, fill, reconciliation hay unknown-outcome evidence; Phase 1 phải tạo task card và evidence riêng.
- Không có secret, API key, endpoint credential, raw venue payload hoặc dữ liệu tài khoản thật trong artifact này.

## Quyết định nghiệm thu

Đây là baseline thiết kế docs-only cho local simulator/no venue. Account Owner đã cho phép mở Task 0.6 để chuẩn bị capability matrix; việc chuyển card sang `REVIEW`/`DONE` vẫn cần review theo quy trình, và không tự mở Phase 0/Phase 1 gate.

## Validation evidence

- `uv run python scripts/validate_contracts.py` — **PASS**, 14 JSON Schemas hợp lệ (`2026-08-11T02:26:26Z`).
- `git diff --check` — **PASS**, không có whitespace error; cảnh báo LF/CRLF của Git chỉ là cảnh báo chuyển dòng.
- Task-card instance được kiểm tra thủ công theo `contracts/config/task-card.v1.schema.json`; môi trường lock không có YAML parser nên chưa claim automated instance validation.
