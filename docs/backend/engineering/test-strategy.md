# ENG-TEST-001 — Test strategy và evidence

| Trường | Giá trị |
|---|---|
| Version / Status | 1.2.0 / IN_REVIEW |
| Owner / Approver | Technical Operator / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | FR-EXEC-001, FR-RSK-001, FR-REC-001, FR-AI-001, NFR-OPS-001, NFR-SEC-001, NFR-AI-001, SEC-AI-002, SEC-AI-003; ADR-0004, ADR-0005, ADR-0011, ADR-0012, ADR-0016 |
| Change summary | Xác định test pyramid, deterministic fixtures, coverage/evidence gate và baseline test Phase 6 AI đa provider/BYOK. |

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

Naming convention (DRAFT — cần phê duyệt): test function đặt theo `test_<behavior>_<condition>_<expected>` để failure output tự mô tả invariant bị vi phạm.

## 3. Invariant suite tối thiểu

- Decimal không mất precision qua serialize/deserialize; tick/lot rounding đúng instrument constraint.
- Journal entry luôn cân bằng; duplicate fill/event không book lần hai.
- Terminal order state không quay về non-terminal; late fill chỉ đi theo correction contract.
- Risk không approve vượt policy; manual approval re-runs full risk evaluation.
- Timeout sau submit hoặc mất lease không tạo duplicate order.
- Replay rebuild projection giống incremental projection.
- Unknown outcome mở reconciliation; stale/missing market/reference/private state chặn exposure mới.
- Invalid/timeout LLM không ảnh hưởng hot path và không có execution tool.
- AI/BYOK tests use a disabled or fake provider by default; they prove catalog/model/policy-profile denial, no arbitrary endpoint/proxy/DNS/redirect bypass, owner-scope denial, write-only/no-read-back/no-log/**no-body-hash** key handling, egress classification, atomic budget denial, output validation and outage/unknown-outcome without silent cross-provider retry.

Risk, OMS và reconciliation phải cover toàn bộ decision/state transition đã support. Coverage domain core >=80% là baseline, không thay thế invariant suite.

Scope đo "domain core" (DRAFT — cần phê duyệt): `src/ai_auto_trade/contexts/*/domain/**` cộng `shared_kernel`, đo bằng pytest-cov với branch coverage.

Mutation testing (DRAFT — cần phê duyệt): đã considered, rejected — thay bằng property/invariant suites ở trên; revisit sau Phase 2.

## 4. Fixture và deterministic test data

- Fixture immutable, versioned và có checksum; stored under `contracts/fixtures` hoặc `tests/fixtures` theo registry.
- Fixture pin UTC, locale, Decimal context, random seed, dataset/config/risk/execution-model version.
- Venue fixture phải redacted secret/account detail, ghi source/version/checksum và không tự refresh.
- Factory chỉ tạo object hợp lệ minh bạch; không dùng factory để che invalid state cần test.
- Test không dùng database/queue/account/credential của developer, paper, testnet hay canary. Integration dùng container/ephemeral instance.

## 5. Contract, compatibility và API testing

Mọi JSON Schema fixture validate bằng draft 2020-12; OpenAPI validate theo 3.1. Compatible change chỉ thêm optional field có default và cần consumer compatibility evidence. Breaking change tạo v2, migration/upcaster plan và không overwrite v1.

Venue-adapter conformance harness (DRAFT — cần phê duyệt): thiết kế harness kiểm tra adapter tuân thủ port contract là deliverable Phase 1 (fake venue) và Phase 3 (real venue); phải có named owner trước khi mở task venue adapter đầu tiên.

API tests phải verify Decimal string, UTC timestamp, UUIDv7, error envelope, idempotency (`same key + same payload` return original; payload khác trả `IDEMPOTENCY_KEY_REUSED`), `If-Match` 412 và cursor pagination. BYOK enrollment needs a route-specific test proving `api_key` is write-only/no-store, uses no Idempotency-Key/body hash/fingerprint, is absent from response/audit/command/event/log fixtures and never reaches a normal durable command mapping. Lost enrollment response requires safe GET/status resolution, not automatic re-post. Không test bằng secret/raw vendor payload or a real provider call.

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

Flaky policy (DRAFT — cần phê duyệt): không auto-retry test trên safety suite (risk/OMS/ledger/reconciliation); quarantine một test chỉ được phép khi có waiver ID còn hạn trong `docs/governance/waiver-register.md`.

## 7. Release/gate use

Failure của safety invariant, contract validation, migration upgrade, secret scan hoặc allowlist check chặn merge/gate. Test data/evidence không chứa secret. Trước paper/testnet/canary, runbook drill và replay/fault injection result là input gate độc lập, không được thay bằng coverage summary.

Performance testing (DRAFT — cần phê duyệt): benchmark submit-to-ack latency theo policy field của OPS-001, chạy từ Phase 2 paper trở đi; evidence benchmark là input bắt buộc tại Phase 3/4 gate.

## 8. Phase 6 AI/BYOK test gate

No provider key, external provider call or live model test is allowed in CI. Before any Phase 6 sandbox/paper enablement, evidence must include: catalog/adaptor artifact/digest capability approval and drift/deprecation behavior; fake-provider contract tests; owner/environment isolation; isolated secret-enrollment redaction/no-read-back/no-hash/no-store; data-egress/prompt sanitization plus DNS/redirect/private-route denial; quota reservation; timeout/rate/circuit; structured-output/provenance validation; initial/rotation candidate atomic cutover/rollback; dual-role validation/activation and emergency-suspend notification; revoke lease/in-flight behavior; provider outage and `AI_OUTCOME_UNKNOWN` without automatic cross-provider fallback; and proof that `ai_worker` has no execution port or venue credential. These tests are gated by ADR-0008, ADR-0015, ADR-0016 and OD-008, not merely by code coverage.

## 9. Change log

| Version | Date | Change | Owner | Approval |
|---|---|---|---|---|
| 1.2.0 | 2026-07-31 | Đổi title ID ENG-003 -> ENG-TEST-001; sửa Related FR-OMS-001 -> FR-EXEC-001; thêm DRAFT: naming convention, domain-core coverage scope, flaky/quarantine policy, mutation-testing decision, venue-adapter conformance harness, performance benchmark gate. | Technical Operator | Pending |
| 1.1.0 | 2026-07-31 | Add Phase 6 provider-neutral/BYOK negative and safety test baseline. | Technical Operator | Pending |
| 1.0.0 | 2026-07-31 | Initial baseline. | Technical Operator | Pending |
