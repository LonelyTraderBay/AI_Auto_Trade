# ENG-REPO-001 — Quy ước repository và ownership

| Trường | Giá trị |
|---|---|
| Version / Status | 1.1.1 / IN_REVIEW |
| Owner / Approver | Technical Operator / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-08-02 |
| Related | NFR-OPS-001, NFR-SEC-001; ADR-0001, ADR-0002, ADR-0014; Phase 0.0.5; ENG-PY-001 §5a; master §4.3/§4.6 |
| Change summary | 1.1.1 (2026-08-02, Technical Operator, Pending): audit chéo — bỏ dòng điều kiện `tests/__init__.py` khỏi manifest §2b (vi phạm cam kết danh sách đóng; cấu hình pytest §5a-ref không cần); bổ sung SECURITY.md/.gitignore/.env.example/docker-compose.yml/scripts//data/catalog/ vào cây §2 cho khớp nguyên văn master §4.6; ghi chú 4 file gốc đã tồn tại không đụng ở 0.1; ghi chú test function `-> None`; đổi chú thích infra "bootstrap" -> "provisioning" tránh nhầm thư mục src. 1.1.0 (2026-08-01): sửa mâu thuẫn topology §2; thêm §2a layout module + §2b manifest skeleton Task 0.1. 1.0.2: đổi title ID; thêm chaos/. 1.0.1: ownership §3 theo GOV-CLASS-001. 1.0.0: baseline. |

## 1. Mục đích và authority

Tài liệu này chuẩn hóa nơi đặt artifact và cách review thay đổi. Nó triển khai §4.6, §4.8, §13.2 và §16 của `AI_AUTO_TRADE_MASTER_SPEC.md`; nếu mâu thuẫn, master và ADR đã `APPROVED` có quyền ưu tiên cao hơn.

Ở Phase 0.0, repository chỉ được có hồ sơ thiết kế, contract, task và evidence. Không tạo `src/`, migration, runtime config, container image, endpoint hoặc adapter cho đến khi Task 0.1 `READY` và Phase 0.0 gate `PASS`.

## 2. Topology chuẩn sau Task 0.1

~~~text
AI_Auto_Trade/
  README.md                 # onboarding; không thay master
  AGENTS.md                 # bản thực thi rút gọn của master §16
  SECURITY.md
  CONTRIBUTING.md
  CODEOWNERS
  .editorconfig
  .gitignore
  .env.example              # chỉ placeholder, không secret (Task 0.1)
  pyproject.toml
  uv.lock
  docker-compose.yml        # Task 0.3 (database) — không thuộc 0.1
  .github/workflows/
  docs/                     # controlled documents, ADR, evidence, templates
  contracts/                # OpenAPI, JSON Schema, error catalog, fixture
  tasks/{active,completed}/ # machine-readable task cards
  configs/                  # instance input đã validate; không chứa secret
  infra/                    # provisioning/deployment, sau Task 0.1
  scripts/                  # helper idempotent; chỉ tạo khi có script thật
  src/ai_auto_trade/
    __init__.py             # docstring 1 dòng; py.typed đặt cạnh
    py.typed
    shared_kernel/
    contexts/<context>/{domain,application,ports}/   # 10 context theo master §4.2; ai_memory chỉ Phase 6
    adapters/<kind>/<provider>/                      # venues, persistence, notifications; llm Phase 6, nautilus sau ADR-0006
    apps/{control_api,trading_node,workers,cli}/     # secret_ingress chỉ Phase 6 (ADR-0016)
  tests/{unit,property,state_machine,chaos,architecture,contract,integration,replay,golden,e2e,fixtures,factories}/
  migrations/
  data/catalog/             # Parquet catalog, Phase 2
  generated/
~~~

Cây trên là bản triển khai đúng nguyên văn master §4.3/§4.6 — **không có** thư mục `bootstrap/` hoặc `shared/` cấp src (shared kernel tên là `shared_kernel/`); composition root nằm trong từng app dưới `apps/`, không phải thư mục riêng. Mỗi context chỉ có `domain/application/ports`; adapter và test **không** nằm trong context (master §4.3 — "topology duy nhất").

`generated/` chỉ chứa output có source link và không được sửa tay. `docs/`, `contracts/` và `tasks/` không phải chỗ để đặt runtime secret hoặc source implementation trá hình.

## 2a. Layout module chuẩn trong context (DRAFT)

> DRAFT — cần Account Owner phê duyệt. Mục tiêu: AI không phải (và không được) tự phát minh tên file/module từ dòng code đầu tiên.

Quy tắc đặt module bên trong mỗi context:

- `domain/`: mỗi aggregate, cụm value object hoặc policy là **một module đặt tên theo khái niệm nghiệp vụ** trong `docs/shared/glossary.md` và tài liệu domain (ví dụ `order.py`, `reservation.py`, `kill_switch.py`). `errors.py` chứa exception gốc của context theo ENG-PY-001 §4a; `events.py` chứa domain event của context. Không tách file khi khái niệm chưa vượt ngân sách kích thước ENG-PY-001 §5a.
- `application/`: mỗi use case là một module tên động từ `<verb>_<object>.py` (ví dụ `submit_order.py`, `resolve_reconciliation.py`). DTO boundary sống cùng module use case của nó cho đến khi rule-of-three (ENG-PY-001 §5) buộc tách.
- `ports/`: mỗi nhu cầu ra ngoài là một module `<capability>_port.py` chứa đúng một Protocol `<Capability>Port` (ví dụ `order_submission_port.py` -> `OrderSubmissionPort`).
- `adapters/<kind>/<provider>/`: module đặt tên theo port mà nó implement; adapter không định nghĩa khái niệm domain mới.
- **Cấm tên module generic không có owner nghiệp vụ**: `models.py`, `types.py`, `base.py`, `interfaces.py`, `schemas.py`, `core.py` — cùng nhóm với `utils.py`/`helpers.py`/`common.py`/`misc.py` đã cấm ở master §4.8. Reviewer từ chối không cần lý do thêm.

Chính sách package:

- Mọi package bắt buộc có `__init__.py` **rỗng** (0 byte). Cấm re-export hub, cấm `__all__`, cấm logic/import trong `__init__.py`. Public surface của một module là đường import đầy đủ của chính nó. Ngoại lệ duy nhất: `src/ai_auto_trade/__init__.py` được phép chứa đúng một docstring giới thiệu package.
- Import luôn **absolute** từ `ai_auto_trade.` — cấm relative import (`from .x import y`). Ruff `I` sắp xếp import; thứ tự do formatter quyết, không sắp tay.
- `py.typed` chỉ có một file duy nhất tại `src/ai_auto_trade/py.typed`.

Quy tắc chống sinh file thừa (over-generation guard):

- Chỉ được tạo file thuộc một trong ba nhóm: (a) topology §2 ở trên, (b) manifest của task card hiện hành (với Task 0.1 là §2b), (c) module được acceptance criteria của card yêu cầu trực tiếp.
- `allowed_globs` là **trần cho phép**, không phải giấy phép sinh file tự do bên trong glob. File ngoài ba nhóm trên là out-of-scope kể cả khi khớp glob — reviewer từ chối diff.
- Không tạo trước thư mục/module "để dành" cho phase sau (`ai_memory/`, `adapters/llm/`, `adapters/nautilus/`, `apps/secret_ingress/` chỉ xuất hiện khi phase/ADR tương ứng mở).

## 2b. Manifest skeleton Task 0.1 (DRAFT)

> DRAFT — cần Account Owner phê duyệt. Đây là danh sách file **đóng và đầy đủ** mà Task 0.1 được tạo/sửa; hai AI tuân thủ phải sinh ra cùng một danh sách. Không file nào khác, kể cả khi `allowed_globs` cho phép.

~~~text
# Sửa nếu acceptance yêu cầu: README.md, AGENTS.md, .gitignore.
# Các file gốc khác đã tồn tại (SECURITY.md, CONTRIBUTING.md, CODEOWNERS, .editorconfig)
# KHÔNG đụng ở 0.1 dù nằm trong allowed_globs — globs là trần, manifest là danh sách đóng.
# Tạo mới:
pyproject.toml              # theo khối chuẩn ENG-PY-001 §5a-ref
uv.lock                     # sinh bởi uv, không sửa tay
.env.example                # chỉ placeholder, không secret
src/ai_auto_trade/__init__.py            # docstring 1 dòng
src/ai_auto_trade/py.typed
src/ai_auto_trade/shared_kernel/__init__.py
src/ai_auto_trade/contexts/__init__.py
src/ai_auto_trade/contexts/<ctx>/__init__.py                    # 9 context: reference, market_data,
src/ai_auto_trade/contexts/<ctx>/domain/__init__.py             # strategy, risk, execution,
src/ai_auto_trade/contexts/<ctx>/application/__init__.py        # portfolio_ledger, research,
src/ai_auto_trade/contexts/<ctx>/ports/__init__.py              # operations, platform (ai_memory Phase 6)
src/ai_auto_trade/adapters/__init__.py
src/ai_auto_trade/adapters/venues/__init__.py
src/ai_auto_trade/adapters/persistence/__init__.py
src/ai_auto_trade/adapters/notifications/__init__.py
src/ai_auto_trade/apps/__init__.py
src/ai_auto_trade/apps/control_api/__init__.py
src/ai_auto_trade/apps/trading_node/__init__.py
src/ai_auto_trade/apps/workers/__init__.py
src/ai_auto_trade/apps/cli/__init__.py
tests/unit/test_bootstrap.py             # suite tối thiểu chạy thật: import package, assert version;
                                         # test function khai báo -> None (ANN áp dụng cho tests)
~~~

Ghi chú chốt biên:

- Mọi `__init__.py` trong manifest là file rỗng theo §2a — đó là cách Git track thư mục "rỗng"; không dùng `.gitkeep` trong `src/`.
- Các thư mục `tests/` còn lại (property, state_machine, ...) tạo **khi test đầu tiên xuất hiện** ở task tương ứng — không tạo 12 thư mục rỗng trước.
- `docker-compose.yml` mặc dù nằm trong `allowed_globs` nhưng **không** thuộc deliverable 0.1 (database là Task 0.3); `scripts/` chỉ tạo khi có script thực sự được acceptance yêu cầu.
- `migrations/`, `configs/`, `infra/`, `.github/` nằm trong `forbidden_globs` của card 0.1 — phần cây §4.6 tương ứng thuộc các task sau (0.2 CI, 0.3 database).
- Dependency đóng cho Task 0.1: `[project].dependencies = []` (không runtime dependency); `[dependency-groups].dev` đúng 3 package `ruff`, `pyright`, `pytest` pinned exact version qua `uv.lock`. Hypothesis (Phase 1), pytest-cov và mọi plugin khác chưa được phép ở 0.1 — thêm sau qua task card tương ứng.

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
