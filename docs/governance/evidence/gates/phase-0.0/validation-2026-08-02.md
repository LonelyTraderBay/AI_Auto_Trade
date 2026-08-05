# EV-GATE-0.0-2026-08-02-01 — Local technical validation (hậu tái cấu trúc + audit chéo)

| Thuộc tính | Giá trị |
|---|---|
| Evidence ID | EV-GATE-0.0-2026-08-02-01 |
| Loại | Local technical validation — **LOCAL_PASS, không phải approval** |
| Ngày chạy (UTC) | 2026-08-02 |
| Runner | Technical Operator (AI-assisted, validator script Python: jsonschema Draft 2020-12 + PyYAML) |
| Phạm vi | Toàn bộ contracts/, tasks/active/, và relative Markdown links trên toàn repo theo đường dẫn HIỆN HÀNH (hậu tái cấu trúc GOV-CLASS-001) |
| Thay thế | [EV-0.0.6-2026-07-30-01](../../tasks/0.0.6/validation-2026-07-30.md) — record cũ tự vô hiệu vì hash keyed theo đường dẫn trước tái cấu trúc (RAID I-007) |
| Gate liên kết | GATE-0.0-001 ([gate-record.md](gate-record.md)) |

> Record này chỉ chứng minh artifact parse/validate/link đúng về mặt kỹ thuật tại thời điểm chạy. Nó không phê duyệt nội dung, không đổi trạng thái gate, không thay thế review của Account Owner. Mọi thay đổi substantive vào artifact được liệt kê dưới đây sẽ làm hash stale và cần record mới trước gate review.

## Kết quả

| Hạng mục | Lệnh/procedure | Kết quả |
|---|---|---|
| JSON Schema Draft 2020-12 | `jsonschema.Draft202012Validator.check_schema` trên toàn bộ `contracts/**/*.schema.json` | PASS — 14/14 schema |
| Task card vs schema | validate từng `tasks/active/*.yaml` với `contracts/config/task-card.v1.schema.json` (format checker bật) | PASS — 8/8 card (gồm `0.1-bootstrap.yaml` BLOCKED) |
| OpenAPI 3.1 | YAML parse + kiểm version/paths/components | PASS — openapi=3.1.0, 28 paths, 45 component schemas |
| Fixture parse | YAML (2) + JSON (14) trong `contracts/fixtures/` | PASS — 16/16 |
| Relative Markdown links | regex extract + resolve trên mọi `.md` toàn repo | PASS — 201 link kiểm, 0 gãy |
| Secret pattern scan (light) | regex AKIA/private-key/api_key-value trên 143 file md/yaml/json | PASS — 0 hit |

## SHA-256 (đường dẫn hiện hành)

~~~text
5F33A5E93AA516BD5919B7A652D1C4B10C16E5DD8F3764346B7DEA6FE1519204  AI_AUTO_TRADE_MASTER_SPEC.md (v2.2.1)
E1C40ACB7816C5E67B79F0C95C28E9732CAB8DA6B8A88797487E1B67BD9C8702  AGENTS.md
9B73ACB9E3A831C9C79E0EE1D558279B0A6AD097BE04179722E5874B8C7A22B6  contracts/api/openapi.yaml
FD26AD8AB9DF3405F5D01198E04F01A85C1AAAC9F74FCD700605C2F24C19F62F  contracts/config/task-card.v1.schema.json
D92F100E36CDDC9E99D2CF0FDE201CCFBBF54DC20AFB2CA903D6CA81711B083E  docs/governance/DOCS_INDEX.md (v0.7.0)
466D0C0C628F247F767A92FF7D57C02C3CF6E2AE8587AAF64497CCEFDD2C6AFD  docs/backend/engineering/coding-standards-python.md (v1.3.1)
8E81E0D14116ADB96990DD23F73EF73286C41438848430C2B68154775DF236DB  docs/backend/engineering/repository-conventions.md (v1.1.1)
0223399C8286DDF67844A809185EF919DD5E933FB62D3B46C1750BB53E847004  tasks/active/0.1-bootstrap.yaml
~~~

## Giới hạn

- Secret scan là pattern nhẹ (chưa phải detect-secrets đầy đủ — tool đó thuộc profile Task 0.1/0.2).
- Không kiểm semantic consistency giữa các tài liệu (đó là việc review của con người theo checklist GATE-0.0-CHECK-001).
- Script validator lưu tại scratchpad phiên làm việc; lệnh và output đầy đủ được ghi trong record này.
