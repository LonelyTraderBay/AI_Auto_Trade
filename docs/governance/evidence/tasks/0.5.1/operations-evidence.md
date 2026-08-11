# Evidence — Task 0.5.1 Config/audit/error envelope

| Trường | Giá trị |
|---|---|
| Task | `0.5.1` |
| Phase | `0` — Foundation |
| Branch | `task/0.5.1-config-audit-envelope` |
| Card status | `DONE` |
| Operator | Technical Operator |
| Reviewer | Account Owner — approved `2026-08-11T00:30:47Z` |
| Gate | Phase 0.0 `APPROVED / REVALIDATED` — `2026-08-10T20:07:02Z` |
| Evidence timestamp | `2026-08-11` (Asia/Bangkok) |

## Phạm vi và truy vết

Task thực hiện đúng mục tiêu config validation path, operations audit event và
safe error envelope. Các quyết định được truy về ADR-0001 (modular monolith),
ADR-0002 (hexagonal dependency rule), ADR-0014 (locked Python toolchain) và
các contract deployment manifest, task card, error catalog, integration event
envelope. Không tạo HTTP endpoint, database/migration, venue adapter, LLM
provider, credential hay execution path.

## Thay đổi đã thực hiện

- Thêm `ErrorCode` đủ 26 mã C-ERR-001 và immutable `ErrorEnvelope` tương thích
  ErrorEnvelope OpenAPI: UUIDv7 canonical, giới hạn message/hint 1024 ký tự,
  structured details chỉ chứa giá trị JSON an toàn và từ chối key secret-like.
- Thêm immutable `AuditEvent`/`AuditStatus` cho lifecycle
  `ACCEPTED -> RUNNING -> SUCCEEDED | FAILED | CANCELLED`, UUIDv7, schema
  version 1 và timestamp UTC với hậu tố `Z`.
- Thêm loader config JSON-compatible YAML (JSON là subset YAML 1.2), từ chối
  duplicate key/secret-like key và environment override các vùng
  `risk/strategy/execution/venue/ai`; merge precedence `base -> environment`.
- Thêm CLI local-only:
  `ai-auto-trade config validate --manifest configs/sample-manifest.yaml`.
- Thêm base/local config, manifest BACKTEST hợp lệ
  (`SIMULATED`/`NONE`/`INTERNAL_SIMULATOR`) và fixture unit/contract.
- Chỉ thêm project script vào `pyproject.toml`; không thêm package và
  `uv.lock` không thay đổi.

## Lệnh bắt buộc và kết quả

| Lệnh | Kết quả |
|---|---|
| `uv sync --locked` | PASS — resolved/checked 31 packages |
| `uv run ruff format --check .` | PASS — 182 files already formatted |
| `uv run ruff check .` | PASS — All checks passed |
| `uv run pyright` | PASS — 0 errors, 0 warnings, 0 informations |
| `uv run pytest` | PASS — 26 passed, 1 skipped |
| `uv run python scripts/validate_contracts.py` | PASS — all 14 JSON Schema files valid |
| `uv run ai-auto-trade config validate --manifest configs/sample-manifest.yaml` | PASS — `CONFIG_VALID`, `environment=local`, `precedence=base->environment` |
| `git diff --check` | PASS — chỉ cảnh báo chuyển đổi LF/CRLF của Git, không có whitespace error |

## Safety và security check

- Không có import FastAPI, SQLAlchemy, Pydantic, CCXT, NautilusTrader, SDK,
  HTTP client hoặc OpenAI trong domain/application path.
- Không có secret value, API key, password, token, stack trace hay credential
  trong code/config/fixture/evidence.
- Không có retry submit, external side effect, persistence, venue/LLM call,
  migration hoặc thay đổi safety invariant.
- Negative tests bao phủ manifest tuple sai, UUID không phải v7, timestamp không
  phải UTC `Z`, error code lạ, secret-like error details và environment override
  vùng safety.

## Artifact hashes (SHA-256)

Hashes được tính trên working tree sau khi chuyển card sang `REVIEW`:

| Path | SHA-256 |
|---|---|
| `pyproject.toml` | `DD234BD3261A31B29202152FCE38E1289BD0840FB7EC27F7019648E81F8CC036` |
| `tasks/active/0.5.1-config-audit-envelope.yaml` | `5C11E4EAC3B5F9CE791E5C7A7E33C7FEEBB16807E50A9FC78272D04849A36DA6` |
| `configs/README.md` | `7211EF99138BB3A47926C00524CB0A7FC3B75FECB61CD1EBE69097598DFA9B5C` |
| `configs/base.yaml` | `D2C6574004D0CA8C42AC4FACC5D110DD2A262A5A8AC4CCFC6EDCAEBE72844809` |
| `configs/environments/local.yaml` | `2A316A810924C6F2570A23E310B1F6398145CDFF6AE56C5B4537A962044AA9F6` |
| `configs/sample-manifest.yaml` | `5379AAB3089C4A4E717F888C8B48BE1559ECEB3DD286F99145D4AFD053B2D8BD` |
| `src/ai_auto_trade/apps/cli/entrypoint.py` | `F448B6D9EEFD34B8821FBB5DE7641D26ADE415530CE871842793083A70AFE47A` |
| `src/ai_auto_trade/contexts/operations/application/config_validation.py` | `67D8F09C5F76D92A0AE19C5924243174B9BC7D14C4576003FCF6DD00589F53C1` |
| `src/ai_auto_trade/shared_kernel/audit.py` | `767216DB4568D5B96D6E7C0D880F700AACD90E15F97FEFCA6216BB2A7E31115D` |
| `src/ai_auto_trade/shared_kernel/error.py` | `CAC567814ABA1E24948C0F44956618DA863D5F478E0C83E27546DE8D9EB7417B` |
| `tests/contract/test_config_validation.py` | `54A834796A214DDA55A9BE4A12967FA3AA1A96CE3B98DF797A58AC3B1E3FDD65` |
| `tests/fixtures/operations/audit-event.valid.json` | `BCFA52560D0D77CC666A331E8C235DFFBED95D1107BD195FAE2A54E21EE15526` |
| `tests/fixtures/operations/error-envelope.invalid.json` | `52E8E64A60EFB13793D4ED5D7351CE73E3F6735E7C96E8C08FC3ADB5C35FAF04` |
| `tests/fixtures/operations/error-envelope.valid.json` | `9F8275396C64F968B06E42DEF7CA2A0E50A3D80D08ABB6BB3661EC3F3D34E248` |
| `tests/unit/contexts/operations/test_audit_envelope.py` | `18616BBF47EE4A05B19E2BD305533652189D8A8B21030EEC77C40621F16AC1B3` |
| `tests/unit/contexts/operations/test_error_envelope.py` | `96499F5898441CB0DDBBE5EC1BE40B24DE890EA31416C71FD60E5A97AA2C7328` |
| `tests/unit/shared_kernel/test_audit.py` | `AEBEBB03D60208519747B80E14726246B110BB114799DBC1E92662CA7C4945AA` |
| `tests/unit/shared_kernel/test_error.py` | `CC1CB912FFE714EAF0577EF47F15E2600866059F83499D6D612FE57084DDE3EC` |

## Quyết định Owner và trạng thái

Account Owner xác nhận tiếp tục trong phiên làm việc `2026-08-11T00:30:47Z`.
Quyết định này được ghi nhận là approval cho evidence/implementation của Task
0.5.1; card đã chuyển `REVIEW -> DONE` và Task 0.5.2 được mở `READY`. Không có
waiver safety nào được tạo hoặc gia hạn.

Known limitation: config fixtures dùng JSON-compatible YAML để giữ validator
stdlib-only và tránh thêm YAML runtime dependency chưa được ADR phê duyệt.
Task 0.0.8 (parser/runner task-card trong locked environment) vẫn là follow-up
riêng, không nằm trong scope 0.5.1.
