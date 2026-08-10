# AGENTS.md — Quy tắc bắt buộc cho AI Coding Agent

> Bản rút gọn **có thể thực thi** của [AI_AUTO_TRADE_MASTER_SPEC.md](AI_AUTO_TRADE_MASTER_SPEC.md) §16 và [docs/backend/engineering/ai-coding-protocol.md](docs/backend/engineering/ai-coding-protocol.md) (ENG-AI-001). Nếu file này mâu thuẫn với master hoặc ENG-AI-001, master và ENG-AI-001 thắng. File này không cấp thêm quyền nào — nó chỉ tóm tắt.

## 0. Trạng thái hiện tại — đọc trước tiên

- Phase hiện tại: **Phase 0 — Foundation (IN_PROGRESS)**. Gate Phase 0.0: **PASSED 2026-08-06**.
- Task hiện hành: **Task 0.1 — Bootstrap** (`tasks/active/0.1-bootstrap.yaml`, status: READY).
- Trong Phase 0, Task 0.1: AI **chỉ được** tạo skeleton repo theo manifest ENG-REPO-001 §2b. **Cấm** viết business/domain/risk/execution logic, tạo migration, database instance, runtime config, venue/LLM integration, CI workflows (.github/**).
- Trạng thái sống luôn ở master §0 control panel — kiểm tra lại mỗi phiên làm việc, đừng tin file này nếu hai bên lệch nhau.

## 1. Thủ tục bắt buộc trước MỌI task

Thực hiện đủ, theo thứ tự — thiếu bước nào thì trạng thái là BLOCKED, không "đoán tốt nhất rồi làm tiếp":

1. `git status` / `git diff` — xác nhận working tree sạch và branch đúng `branch_pattern` của task card.
2. Đọc master §0 control panel — xác nhận phase/gate hiện tại và blocker.
3. Đọc **task card YAML** trong `tasks/active/` — chỉ card có `status: READY` mới cho phép thực thi. Card là authority phạm vi duy nhất: `allowed_globs` cho phép, `forbidden_globs` thắng khi xung đột.
4. Đọc mọi ADR/contract/schema được card tham chiếu. Nếu một tham chiếu không tồn tại → BLOCKED.
5. Kiểm tra locked version của thư viện định dùng so với tài liệu chính thức; không thêm dependency ngoài card.
6. Mọi giả định về architecture/risk/security/database → dừng, escalate thành ADR hoặc Open Decision, không tự quyết.

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
