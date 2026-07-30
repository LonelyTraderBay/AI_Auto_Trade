# ENG-003 — Test strategy và evidence

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.0 / IN_REVIEW |
| Owner / Approver | Technical Operator / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | FR-OMS-001, FR-RSK-001, FR-REC-001, NFR-OPS-001, NFR-SEC-001; ADR-0004, ADR-0005, ADR-0011, ADR-0012 |
| Change summary | Xác định test pyramid, deterministic fixtures, coverage và evidence gate. |

## 1. Mục tiêu

Test chứng minh safety invariant và recovery behavior, không chỉ happy path hoặc coverage. Mỗi test/capability phải trace được Requirement -> ADR -> contract/module -> test -> evidence. Không có traceability thì feature chưa được mở implementation.

## 2. Pyramid bắt buộc

| Lớp | Mục tiêu | Isolation / evidence |
|---|---|---|
| Unit | value object, policy, entity, mapping thuần | Không network/DB/clock/RNG thật. |
| Property | Decimal, rounding, balance, idempotency | Hypothesis; seed và counterexample lưu trong report. |
| State machine | OMS, reconciliation, kill switch, lease | Bảng transition được test đủ hợp lệ/không hợp lệ. |
| Architecture | import/layer/context boundary | Import linter hoặc equivalent rule. |
| Contract | JSON Schema/OpenAPI, adapter/provider capability | Fixture versioned, redacted, compatibility result. |
| Integration | PostgreSQL, migration, outbox/inbox | DB ephemeral riêng; không dev/canary DB. |
| Replay / golden | deterministic market/order/ledger path | Dataset/config/seed/checksum pin. |
| Chaos / E2E | network, DB, clock, crash, disk, split-brain | Controlled fault scenario và incident/evidence. |

E2E không được là lớp test duy nhất cho business logic.

## 3. Invariant suite tối thiểu

- Decimal không mất precision qua serialize/deserialize; tick/lot rounding đúng instrument constraint.
- Journal entry luôn cân bằng; duplicate fill/event không book lần hai.
- Terminal order state không quay về non-terminal; late fill chỉ đi theo correction contract.
- Risk không approve vượt policy; manual approval re-runs full risk evaluation.
- Timeout sau submit hoặc mất lease không tạo duplicate order.
- Replay rebuild projection giống incremental projection.
- Unknown outcome mở reconciliation; stale/missing market/reference/private state chặn exposure mới.
- Invalid/timeout LLM không ảnh hưởng hot path và không có execution tool.

Risk, OMS và reconciliation phải cover toàn bộ decision/state transition đã support. Coverage domain core >=80% là baseline, không thay thế invariant suite.

## 4. Fixture và deterministic test data

- Fixture immutable, versioned và có checksum; stored under `contracts/fixtures` hoặc `tests/fixtures` theo registry.
- Fixture pin UTC, locale, Decimal context, random seed, dataset/config/risk/execution-model version.
- Venue fixture phải redacted secret/account detail, ghi source/version/checksum và không tự refresh.
- Factory chỉ tạo object hợp lệ minh bạch; không dùng factory để che invalid state cần test.
- Test không dùng database/queue/account/credential của developer, paper, testnet hay canary. Integration dùng container/ephemeral instance.

## 5. Contract, compatibility và API testing

Mọi JSON Schema fixture validate bằng draft 2020-12; OpenAPI validate theo 3.1. Compatible change chỉ thêm optional field có default và cần consumer compatibility evidence. Breaking change tạo v2, migration/upcaster plan và không overwrite v1.

API tests phải verify Decimal string, UTC timestamp, UUIDv7, error envelope, idempotency (`same key + same payload` return original; payload khác trả `IDEMPOTENCY_KEY_REUSED`), `If-Match` 412 và cursor pagination. Không test bằng secret/raw vendor payload.

## 6. Test execution và evidence

Sau Task 0.1, baseline command profile là:

~~~text
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
~~~

Từ Task 0.2 thêm `uv run ai-auto-trade contracts validate`; từ Task 0.3 thêm `uv run ai-auto-trade db verify`. Trước lúc CLI tồn tại, task/gate phải chỉ định validator thay thế và lưu exit code/artifact; không được claim pass chỉ bằng review tay.

Test report phải lưu Task ID, commit SHA, command, UTC start/end, seed/dataset/config hash khi áp dụng, pass/fail/skip, waiver ID và artifact path. `skip`/`xfail` trong risk/OMS/reconciliation cần waiver còn hạn; CI fail khi expiry qua.

## 7. Release/gate use

Failure của safety invariant, contract validation, migration upgrade, secret scan hoặc allowlist check chặn merge/gate. Test data/evidence không chứa secret. Trước paper/testnet/canary, runbook drill và replay/fault injection result là input gate độc lập, không được thay bằng coverage summary.

