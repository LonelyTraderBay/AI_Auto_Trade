# CONTRIBUTING — AI Auto Trade

Quy tắc đóng góp áp dụng cho cả người và AI coding agent, kể cả khi dự án chỉ có một người vận hành. Nguồn chuẩn đầy đủ: master §13.2 và [docs/backend/engineering/repository-conventions.md](docs/backend/engineering/repository-conventions.md) (ENG-REPO-001).

## 1. Branch và PR

- `main` là protected branch. Mọi thay đổi đi qua short-lived branch + PR/review record — không commit thẳng vào main.
- Tên branch phải khớp `branch_pattern` của task card hiện hành: `task/<TASK_ID>-<slug>` (ví dụ `task/0.1-bootstrap-skeleton`).
- Một PR chỉ phục vụ một task card; diff phải nằm trong `allowed_globs` của card đó (`forbidden_globs` thắng khi xung đột).
- Reviewer theo vùng được khai báo trong [CODEOWNERS](CODEOWNERS); thay đổi safety/security/live cần approver độc lập theo [docs/governance/raci.md](docs/governance/raci.md).

## 2. Commit

- Chuẩn **Conventional Commits**: `type(scope): mô tả` — `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `build`.
- Commit nhỏ, một ý nghĩa; thân commit link Task ID/REQ/ADR khi áp dụng (ví dụ `Task: 0.1`, `Refs: ADR-0014, NFR-OPS-001`).
- Không sửa migration đã áp dụng, không force-push lên main, không rewrite lịch sử approval.

## 3. Dependency

Dependency mới cần: Task ID cho phép, lý do ghi rõ, license/security review, locked version trong `uv.lock`, và test đi kèm. Không `pip install` tự phát — mọi package ngoài danh sách §3.5 master là forbidden by default và cần ADR.

## 4. Chất lượng trước khi mở PR (từ Task 0.1 trở đi)

```bash
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

Command profile mở rộng theo phase (contracts validate từ Task 0.2, db verify từ Task 0.3 — master §13.2). Chỉ được báo "pass" khi lệnh đã chạy thật và kết quả được lưu vào evidence path của task.

## 5. Thay đổi tài liệu

- Tài liệu được kiểm soát theo [docs/governance/document-control.md](docs/governance/document-control.md): mỗi thay đổi substantive tăng version + một dòng changelog; cập nhật [DOCS_INDEX](docs/governance/DOCS_INDEX.md) trong cùng thay đổi.
- Không tự gắn `APPROVED` — chỉ approver theo RACI được chuyển trạng thái, kèm actor/UTC/evidence.
- Evidence đã ký và journal/audit append-only là bất biến — sai thì tạo bản ghi mới, không sửa lịch sử.

## 6. CHANGELOG và release

Không duy trì CHANGELOG viết tay. Release note được sinh từ lịch sử Conventional Commits tại thời điểm gắn tag, theo [docs/backend/engineering/versioning-release-policy.md](docs/backend/engineering/versioning-release-policy.md). Định danh release/deployment gắn với immutable deployment manifest (master §6.6), không gắn với tên branch.
