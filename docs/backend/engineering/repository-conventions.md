# ENG-REPO-001 — Quy ước repository và ownership

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.2 / IN_REVIEW |
| Owner / Approver | Technical Operator / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | NFR-OPS-001, NFR-SEC-001; ADR-0001, ADR-0002, ADR-0014; Phase 0.0.5 |
| Change summary | 1.0.2 (2026-07-31, Technical Operator, Pending): đổi title ID ENG-001 -> ENG-REPO-001 khớp DOCS_INDEX; bổ sung `chaos/` vào topology tests/ theo master §4.6 v2.2.0. 1.0.1: cập nhật bảng ownership §3 theo cấu trúc docs/ mới (GOV-CLASS-001). 1.0.0: thiết lập topology, naming, ownership và quy tắc review trước khi tạo application code. |

## 1. Mục đích và authority

Tài liệu này chuẩn hóa nơi đặt artifact và cách review thay đổi. Nó triển khai §4.6, §4.8, §13.2 và §16 của `AI_AUTO_TRADE_MASTER_SPEC.md`; nếu mâu thuẫn, master và ADR đã `APPROVED` có quyền ưu tiên cao hơn.

Ở Phase 0.0, repository chỉ được có hồ sơ thiết kế, contract, task và evidence. Không tạo `src/`, migration, runtime config, container image, endpoint hoặc adapter cho đến khi Task 0.1 `READY` và Phase 0.0 gate `PASS`.

## 2. Topology chuẩn sau Task 0.1

~~~text
AI_Auto_Trade/
  README.md                 # onboarding; không thay master
  AGENTS.md                 # bản thực thi rút gọn của master §16
  CONTRIBUTING.md
  CODEOWNERS
  pyproject.toml
  uv.lock
  .editorconfig
  .github/workflows/
  docs/                     # controlled documents, ADR, evidence, templates
  contracts/                # OpenAPI, JSON Schema, error catalog, fixture
  tasks/{active,completed}/ # machine-readable task cards
  configs/                  # instance input đã validate; không chứa secret
  infra/                    # bootstrap/deployment, sau Task 0.1
  src/ai_auto_trade/
    apps/
    contexts/
    adapters/
    shared/
    bootstrap/
  tests/{unit,property,state_machine,chaos,architecture,contract,integration,replay,golden,e2e,fixtures,factories}/
  migrations/
  generated/
~~~

`generated/` chỉ chứa output có source link và không được sửa tay. `docs/`, `contracts/` và `tasks/` không phải chỗ để đặt runtime secret hoặc source implementation trá hình.

## 3. Ownership và boundaries

| Khu vực | Owner | Quy tắc chính |
|---|---|---|
| `docs/governance/`, `docs/shared/`, `docs/backend/` (gồm `adr/`), evidence | Owner được nêu trong header | Có ID, version, status, link requirement/ADR/task. |
| `contracts/` | Technical Operator | Versioned; fixture và compatibility evidence bắt buộc. |
| `tasks/` | Technical Operator | YAML là authority cho allowed paths; trạng thái và expiry phải hợp lệ. |
| `src/.../contexts/<context>` | Context owner | Không import framework/vendor vào domain. |
| `src/.../adapters` | Technical Operator | Chỉ triển khai ports đã được contract/ADR chấp thuận. |
| `migrations/` | Technical Operator | Immutable; cần data dictionary, task card và review. |
| `configs/` / `infra/` | Technical + Security/Backup Owner khi sensitive | Không có secret raw; manifest immutable. |
| `tests/` | Owner của capability | Mirror source/capability; fixture phải redacted và pinned. |

Không có cross-context ORM relationship, foreign key hoặc direct SQL. Cross-context đi qua immutable ID, event contract hoặc read projection theo master §7.4.

## 4. Naming và versioning

- Python package/module/file dùng `snake_case`; type/class dùng `PascalCase`; function, field và contract key dùng `snake_case`; wire enum dùng `SCREAMING_SNAKE_CASE`.
- JSON Schema dùng `<name>.v<major>.schema.json`; breaking change tạo major mới, không overwrite v1.
- Event type dùng dạng past tense `<context>.<event_name>.v<major>`; command type là động từ (`SUBMIT_ORDER`, `REQUEST_RECONCILIATION`).
- Fixture dùng `<contract>.v<major>.valid.<ext>` hoặc suffix được registry đăng ký; không dùng fixture tự làm mới từ venue.
- Alembic revision (sau Phase 0) immutable, message chứa Task ID và intent. Không rename/sửa migration đã apply.
- ID nội bộ là UUIDv7; Decimal đi qua API dưới dạng string; timestamp là UTC ISO-8601 có `Z`.

## 5. Branch, commit và review

- `main` là protected. Mọi thay đổi dùng branch ngắn khớp `branch_pattern` của task card và đi qua PR/review record, kể cả dự án một người.
- Commit dùng Conventional Commit hoặc chuẩn sau này trong `CONTRIBUTING.md`; phải nhỏ, một ý nghĩa và link Task ID/REQ/ADR nếu áp dụng.
- Diff chỉ được chạm `allowed_globs` của task YAML. `forbidden_globs` luôn thắng allowlist.
- Contract, migration, risk, OMS, ledger, security, deployment cần reviewer role tương ứng trong master §11.4. Safety/security/live không được một người/AI tự phê duyệt.
- Không force-push để xóa evidence review; không sửa evidence đã dùng cho gate. Bổ sung record superseding mới thay vì rewrite lịch sử.

## 6. Quy tắc artifact và bí mật

- Secret chỉ là `secret_ref`/path được schema cho phép; không xuất hiện trong Git, fixture, screenshot, Markdown, log, test assertion hoặc OpenAPI example.
- Không đặt venue thật, account thật, endpoint private, key, token, IP allowlist hoặc dữ liệu khách hàng trong baseline artifact.
- Mọi output contract/config/deployment phải canonicalize, hash và trace được về task/gate khi runtime được tạo.
- Public contract, DDL và config key không được thay đổi chỉ bằng prose. Cập nhật canonical schema/OpenAPI/migration trong approved task và bổ sung compatibility evidence.

## 7. Definition of Ready cho thay đổi repository

Một thay đổi được mở khi task card có requirement/ADR/contract liên quan, owner/reviewer, expiry, allowed/forbidden globs, acceptance command và evidence path. Thiếu một phần thì trạng thái là `BLOCKED`, không suy đoán để tạo file hoặc dependency mới.

