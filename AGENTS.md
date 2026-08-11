# AGENTS.md — Quy tắc bắt buộc cho AI Coding Agent

> Bản rút gọn **có thể thực thi** của [AI_AUTO_TRADE_MASTER_SPEC.md](AI_AUTO_TRADE_MASTER_SPEC.md) §16 và [docs/backend/engineering/ai-coding-protocol.md](docs/backend/engineering/ai-coding-protocol.md) (ENG-AI-001). Nếu file này mâu thuẫn với master hoặc ENG-AI-001, master và ENG-AI-001 thắng. File này không cấp thêm quyền nào — nó chỉ tóm tắt.

## 0. Trạng thái hiện tại — đọc trước tiên

- Phase hiện tại: **Phase 1 — Core safety (IN_PROGRESS)**. Gate Phase 0.0: **PASSED / REVALIDATED 2026-08-10T20:07:02Z**.
- Task đã DONE (Account Owner approve 2026-08-06, card trong `tasks/completed/`): **0.1 Bootstrap, 0.2 Guardrails, 0.3 Persistence contract, 0.4 Architecture contract**.
- Task đã hoàn tất: **0.0.7 — Codex Enterprise documentation** (`tasks/active/0.0.7-codex-enterprise-docs.yaml`, `DONE`, docs-only), Account Owner revalidate gate 2026-08-10T20:07:02Z.
- Task đã DONE: **0.5.1 — Config/audit/error envelope** (`tasks/completed/0.5.1-config-audit-envelope.yaml`), Account Owner approve `2026-08-11T00:30:47Z`.
- Task đã DONE: **0.5.2 — Control API skeleton** (`tasks/completed/0.5.2-control-api-skeleton.yaml`), Account Owner xác định DONE `2026-08-11T02:14:42Z`.
- Task đã DONE: **0.6 — Capability draft** (`tasks/completed/0.6-capability-draft.yaml`), Account Owner xác định DONE `2026-08-11T19:16:45Z`; local simulator/no venue, docs-only.
- Task hiện hành: **1.1 — deterministic primitives** (`tasks/active/1.1-deterministic-primitives.yaml`, `READY`), branch `task/1.1-*`; local simulator/no venue, chưa OMS/risk/ledger/venue.
- OD-001 vẫn `OPEN` cho external venue/testnet; không được coi local simulator là venue approval hoặc mở Phase 3.
- Không có card `READY` phù hợp trong `tasks/active/` thì AI chỉ được đọc/phân tích, **không được sửa implementation file** (master §16). Card `BLOCKED` không được tự chuyển sang `READY`; chỉ Account Owner/reviewer có quyền xác nhận.
- Với mọi card READY: làm đúng và chỉ đúng `allowed_globs` của card đó; `forbidden_globs` thắng khi xung đột.
- Trạng thái sống luôn ở master §0 control panel — kiểm tra lại mỗi phiên làm việc, đừng tin file này nếu hai bên lệch nhau.

## 1. Thủ tục bắt buộc trước MỌI task

Thực hiện đủ, theo thứ tự — thiếu bước nào thì trạng thái là BLOCKED, không "đoán tốt nhất rồi làm tiếp":

1. `git status` / `git diff` — xác nhận working tree sạch và branch đúng `branch_pattern` của task card.
2. Đọc master §0 control panel — xác nhận phase/gate hiện tại và blocker.
3. Đọc **task card YAML** trong `tasks/active/` — chỉ card có `status: READY` mới cho phép thực thi. Card là authority phạm vi duy nhất: `allowed_globs` cho phép, `forbidden_globs` thắng khi xung đột.
4. Đọc mọi ADR/contract/schema được card tham chiếu. Nếu một tham chiếu không tồn tại → BLOCKED.
5. Kiểm tra locked version của thư viện định dùng so với tài liệu chính thức; không thêm dependency ngoài card.
6. Mọi giả định về architecture/risk/security/database → dừng, escalate thành ADR hoặc Open Decision, không tự quyết.

## 1.1 Quy tắc vận hành với OpenAI Codex

- `AGENTS.md` ở root là instruction source bắt buộc của repository. Codex đọc file này trước khi làm việc; nếu có `AGENTS.md`/`AGENTS.override.md` ở thư mục con thì áp dụng theo thứ tự root → thư mục hiện tại, file gần hơn có thể bổ sung/ghi đè luật rộng hơn khi không mâu thuẫn với master.
- Không tạo `CODEX.md`, `AI_INSTRUCTIONS.md` hoặc file thay thế khác để né discovery. Chỉ dùng fallback filename nếu cấu hình Codex của repository đã khai báo rõ.
- Giữ instruction ngắn, cụ thể và có thể kiểm chứng; nếu tổng instruction bị cắt do giới hạn kích thước, phải tách phần chi tiết sang tài liệu được task tham chiếu và ghi link canonical.
- Mỗi phiên phải ghi nhận instruction source đã đọc, task ID, branch, trạng thái card, allowlist và command/evidence dự kiến. Prompt người dùng không thay thế authority trong repository.
- “Phù hợp với OpenAI” ở Phase 0 chỉ nghĩa là Codex thực thi đúng quy trình; **không** được tự thêm OpenAI SDK/API, LLM provider, credential hoặc đường dẫn AI → execution.

## 2. Thứ tự authority (master §1.5)

```text
1. Regulatory/legal constraint
2. Master spec + ADR APPROVED (gồm safety invariant không thể waiver)
3. Explicit owner decision trong phạm vi (1)(2)
4. Versioned DDL / OpenAPI / JSON Schema / contract registry
5. Approved task card / gate record
6. Code và generated artifact
7. Test fixture, log, report
```

Artifact cấp thấp mâu thuẫn cấp cao → BLOCKED. Không sửa code để che mâu thuẫn tài liệu.

## 3. Các điều cấm tuyệt đối (không waiver)

- Không có đường nào từ LLM/AI đến API đặt lệnh. Risk engine deterministic, không gọi LLM.
- Không retry submit order khi outcome UNKNOWN. Không hard-delete financial/audit history.
- Không float cho tiền — Decimal domain, NUMERIC(38,18) DB, string trên API. UUIDv7 cho ID nội bộ. TIMESTAMPTZ UTC.
- Không secret/credential trong code, config YAML, log, fixture, evidence hay commit. Secret chỉ là reference.
- Không `Any`, `type: ignore`, bare except, skip/xfail không waiver ID trên safety path. Pyright strict, không mypy.
- Không thêm package/framework/runtime ngoài §3.5 master khi chưa có ADR (Node/Redis/Kafka/K8s... forbidden by default).
- Không tự chuyển task REVIEW→DONE, không tự approve ADR/gate/waiver, không tự gia hạn expiry — đó là quyền của con người theo RACI.
- Domain không import FastAPI/SQLAlchemy/Pydantic/CCXT/Nautilus/SDK — chỉ Python stdlib + shared kernel.

## 4. Khi code (từ Phase 0 trở đi, sau khi gate mở)

- **Viết code nhỏ nhất và đơn giản nhất đủ pass acceptance commands** — chất lượng là non-negotiable như safety: tuân ngân sách complexity ENG-PY-001 §5a (Ruff enforce: complexity ≤10, tham số ≤5, không commented-out code, docstring Google style toàn bộ `src/` trừ `tests/` và `__init__.py` rỗng), không anti-pattern §5b (không speculative abstraction/wrapper chưa có consumer thứ hai, không defensive check thừa cho điều kiện type system đã loại trừ, không `async` không cần, không dead code, không generalize ngoài card).
- **Cấu trúc không phải chỗ sáng tạo**: cây thư mục theo master §4.6; tên module trong context theo ENG-REPO-001 §2a (cấm `models.py`/`types.py`/`base.py`/`interfaces.py`/`core.py` và mọi tên generic); `__init__.py` rỗng (trừ `src/ai_auto_trade/__init__.py`: đúng 1 dòng docstring), không re-export/`__all__`; import absolute từ `ai_auto_trade.`. **Chỉ tạo file có trong topology hoặc manifest của card** (Task 0.1 = ENG-REPO-001 §2b) — `allowed_globs` là trần cho phép, không phải giấy phép sinh file tự do; `pyproject.toml` tái tạo khối chuẩn ENG-PY-001 §5a-ref, không tự thiết kế config.
- Làm đúng và chỉ đúng phạm vi `allowed_globs` của card READY hiện hành; mỗi commit nhỏ, một ý nghĩa, message Conventional Commit kèm Task ID (xem [CONTRIBUTING.md](CONTRIBUTING.md)).
- Chạy đủ `required_commands` của card; chỉ được báo "pass" khi lệnh đã chạy thật và exit code/artifact được lưu vào `evidence_path`.
- Test theo pyramid §13.3; invariant test không thay bằng coverage; fixture pin seed/UTC/Decimal context.
- Kết thúc task: báo cáo theo format §16.5 — việc đã làm, lệnh đã chạy + kết quả, path/hash artifact, đề xuất trạng thái (tối đa REVIEW), blocker còn lại.

## 5. Lối thoát an toàn

Gặp bất kỳ điều nào sau đây → dừng ngay, ghi BLOCKED kèm lý do, không tiếp tục: yêu cầu ngoài scope card; tài liệu mâu thuẫn; cần quyết định owner chưa có; phát hiện secret/leak; test/command fail không rõ nguyên nhân; nghi ngờ đụng safety invariant.

## Code Review Rules

- Ưu tiên correctness, safety invariant, contract compatibility, auditability và recovery; không đánh đổi các mục này lấy tốc độ hoặc độ ngắn của diff.
- Mọi thay đổi phải truy được tới task card READY, requirement/ADR/contract liên quan và evidence command; diff ngoài allowlist là lỗi chặn merge.
- Không phê duyệt thay đổi chỉ vì test “đang xanh”; phải kiểm tra negative path, secret boundary, unknown outcome, idempotency và trạng thái gate.
- Không dùng review để tự thay đổi status `APPROVED`, `READY`, `DONE`, waiver hoặc gate. Những quyết định đó cần đúng human role và evidence riêng.
- Không dành review cho việc sửa format/lint tự động; các vấn đề đó phải do command quality gate báo. Review tập trung vào behavior, scope, safety và regression.
