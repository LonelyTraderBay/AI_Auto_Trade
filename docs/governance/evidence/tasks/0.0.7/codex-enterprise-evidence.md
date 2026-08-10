# Evidence — Task 0.0.7 Codex Enterprise documentation

| Trường | Giá trị |
|---|---|
| Task | `0.0.7` |
| Branch | `task/0.0.7-codex-enterprise-docs` |
| Runner | Technical Operator (AI-assisted) |
| Date | 2026-08-10T19:31:42Z (2026-08-11 Asia/Bangkok) |
| Task status đề xuất | `DONE` — Account Owner revalidated gate và mở Task 0.5.1 |
| Runtime impact | Không có; không sửa `src/`, `tests/`, `migrations/`, `configs/`, `.github/` hoặc public contract |
| Gate impact | Gate Phase 0.0 `APPROVED — REVALIDATED` tại 2026-08-10T20:07:02Z; evidence này là technical input, approval nằm trong gate record |

## Instruction provenance

- Đã đọc `AGENTS.md` ở repository root và task card canonical `tasks/active/0.0.7-codex-enterprise-docs.yaml`.
- Đã đọc master control panel phiên bản 2.2.4, ENG-AI-001 phiên bản 1.2.0, ENG-CI-001 phiên bản 1.2.0, REG-001 phiên bản 1.1.3, gate record Phase 0.0 và ADR-0001/0002/0014.
- Codex discovery rule được ghi rõ trong AGENTS/ENG-AI-001; không tạo `CODEX.md` và không thêm OpenAI SDK/API runtime.

## Changed files and allowlist review

Mọi file dưới đây đều khớp `allowed_globs` của task 0.0.7; không có file nào thuộc `forbidden_globs`:

- `AGENTS.md`
- `AI_AUTO_TRADE_MASTER_SPEC.md`
- `README.md`
- `docs/backend/contracts/contract-registry.md`
- `docs/backend/engineering/ai-coding-protocol.md`
- `docs/backend/engineering/ci-cd-design.md`
- `docs/governance/DOCS_INDEX.md`
- `docs/governance/evidence/gates/phase-0.0/gate-record.md`
- `docs/governance/evidence/tasks/0.0.7/codex-enterprise-evidence.md`
- `scripts/validate_contracts.py`
- `tasks/active/0.0.7-codex-enterprise-docs.yaml`

## Required command results

| Command | Exit | Kết quả |
|---|---:|---|
| `uv sync --locked` | 0 | Resolved/checked 31 packages |
| `uv run ruff format --check .` | 0 | 171 files already formatted |
| `uv run ruff check .` | 0 | All checks passed |
| `uv run pyright` | 0 | 0 errors, 0 warnings, 0 informations |
| `uv run pytest` | 0 | 14 passed, 1 skipped; integration DB test skip vì `DATABASE_URL` chưa được cấp |
| `uv run python scripts/validate_contracts.py` | 0 | 14 JSON Schema files valid |
| `git diff --check` | 0 | Không có whitespace error; Git chỉ cảnh báo line-ending LF/CRLF trên Windows |

## Validation scope and limitations

`validate_contracts.py` trong change set này chỉ xác nhận JSON Schema Draft 2020-12. Nó **không** claim đã validate OpenAPI, YAML fixture, task-card YAML, cross-file links hoặc CI enforcement. Các hạng mục đó vẫn là trách nhiệm của Task 0.2/contract procedure tương ứng và được ghi rõ trong ENG-CI-001/REG-001. Automated YAML task-card parsing được ghi thành dependency bắt buộc của Task 0.0.8 trước khi safe auto-runner được mở.

Task card `0.5.1` đã `READY`; `0.5.2` vẫn `BLOCKED` phụ thuộc 0.5.1. Task 0.0.7 đã đóng `DONE` sau Account Owner revalidation; automated YAML parser/runner là follow-up Task 0.0.8.

## SHA-256 evidence

Hash được tạo bằng `Get-FileHash <path> -Algorithm SHA256` sau khi hoàn tất
change set trước review. Hash của chính file evidence không được đưa vào bảng
để tránh vòng lặp; gate record có thể chốt lại hash bundle khi ký.

| Path | SHA-256 |
|---|---|
| `AGENTS.md` | `45DC9E75F3070462E3CBB436406327B18691FA937B0B506812A0FECFAE71DAF2` |
| `AI_AUTO_TRADE_MASTER_SPEC.md` | `88C2752715B62A2F56E09AE617F637990E70D0BF355FF309BC7285B2C40DE17D` |
| `README.md` | `B2569AB30C7CD23B518FA537A1AD88C83EF924E0C2CDDBE51E874CC65AF852EF` |
| `docs/backend/contracts/contract-registry.md` | `CF3C59A9C3F6E6EECFE0B846D31535B05491E67A5106368986E54602BE926822` |
| `docs/backend/engineering/ai-coding-protocol.md` | `7430F483FCBC5BCD02B58ED2FE729363029DD673CD7F3E85EB52A54D0F3318CE` |
| `docs/backend/engineering/ci-cd-design.md` | `90862AA53FDEEB7A2E32AC26A600724EF2A53C83DDAB5135057CA7E9FCB7AC34` |
| `docs/governance/DOCS_INDEX.md` | `0A0756C01642CE145C16A528E03B3E6CA4AD341E41929AD99518DC1BA1370E75` |
| `docs/governance/evidence/gates/phase-0.0/gate-record.md` | `F724ACDB3C2430A5F57C105E25276220E01845075B325F39F176757D86B657CF` |
| `scripts/validate_contracts.py` | `706B4F2FFC13DED6180CC32220716467C307C14ECDD749F8CB17C1AD8AE402DF` |
| `tasks/active/0.0.7-codex-enterprise-docs.yaml` | `CD3DF25698802CE3FD7545B1A0C59690DC4CBDF9104AA8F042643AEEF7557159` |
| `tasks/active/0.5.1-config-audit-envelope.yaml` | `2BD920DDE7C2CB7ED8E9F2B4A5E4DA3D4FF3CDC0E23FE91F7EFE3B1A74C5CAB2` |

Technical Operator không dùng self-report thay cho hash/actor/UTC sign-off;
Account Owner vẫn là người duy nhất quyết định revalidation và gate status.
