# Ghi chú commit — Hoàn thiện hồ sơ Phase 0.0

> **Addendum 2026-07-31 (sau tái cấu trúc GOV-CLASS-001):** File này là hồ sơ lịch sử; các đường dẫn trong đó phản ánh cấu trúc `docs/` CŨ (trước tái cấu trúc Backend/Frontend/Shared/Governance). Đường dẫn hiện hành: gate record tại `docs/governance/evidence/gates/phase-0.0/gate-record.md`, chỉ mục tại `docs/governance/DOCS_INDEX.md`. File `COMMIT_MESSAGE.txt` được nhắc ở §6 chưa từng được commit vào repo — commit message đã được nhập trực tiếp. Không sửa nội dung gốc bên dưới để giữ tính lịch sử. **Mọi đường dẫn/chỉ dẫn dạng quy phạm trong phần lịch sử bên dưới (kể cả §5) không còn được duy trì — chỉ tra cứu theo đường dẫn hiện hành nêu trên.**
>
> **Đính chính attribution (audit 2026-08-02):** các con số kiểm tra ở §2/§4 (6 schema, 6 fixture, 6 task card, 15 ADR 0001–0015) khớp với tree tại commit `d99d32d`, KHÔNG khớp tree tại `15fc81a` (thời điểm đó đã có 8 config schema, 16 fixture, 7 task card active và ADR-0016). Hồ sơ này vì vậy được gán đúng cho `d99d32d`; commit `15fc81a` (dùng lại nguyên văn message) bổ sung thêm gói BYOK: ADR-0016, task 0.0.6, schema + fixture AI. Không sửa nội dung gốc để giữ tính lịch sử.

| Thuộc tính | Giá trị |
|---|---|
| Phạm vi commit | Hồ sơ tiền triển khai (pre-code) cho Phase 0.0 |
| Ngày lập ghi chú | 2026-07-31 |
| Trạng thái hồ sơ | `IN_REVIEW` |
| Trạng thái gate | `NOT PASSED` — chờ phê duyệt quyết định bắt buộc |
| Thay đổi runtime | Không có |
| Thay đổi migration / schema DB thực thi | Không có |
| Thay đổi tích hợp sàn hoặc giao dịch thật | Không có |

## 1. Tiêu đề commit đề xuất

```text
docs(phase-0): hoàn thiện hồ sơ governance, architecture và delivery baseline
```

## 2. Nội dung commit đề xuất

Sao chép nguyên khối nội dung sau khi tạo commit nhiều dòng:

```text
docs(phase-0): hoàn thiện hồ sơ governance, architecture và delivery baseline

- cập nhật master spec về trạng thái Documentation Closure của Phase 0.0;
- bổ sung chỉ mục tài liệu chính thức và document-control cho toàn bộ artifact;
- bổ sung product charter, functional/non-functional requirements, glossary,
  RACI, RAID register và requirements traceability;
- bổ sung C4 context/container, runtime sequence, policy công nghệ và quy ước
  repository/coding/testing/CI-CD/AI coding;
- bổ sung canonical domain model, OMS state machine, risk/accounting policy,
  data architecture, ERD, data dictionary, transaction/concurrency,
  database operation và migration/backfill playbook;
- bổ sung 15 ADR bắt buộc (0001-0015), tất cả giữ DRAFT để Account Owner
  phê duyệt theo đúng authority workflow;
- bổ sung threat model, access control, auth/session, secrets, SLO/alert và
  runbook cho các tình huống vận hành trọng yếu;
- bổ sung contract registry, OpenAPI 3.1, JSON Schema cho config/command/event,
  error catalog và fixture hợp lệ;
- bổ sung task card Phase 0.0, evidence placeholder, review checklist và gate record.

Đã kiểm tra:
- 85/85 artifact Phase 0.0 bắt buộc có mặt;
- 6 JSON Schema hợp lệ theo Draft 2020-12;
- 6 fixture và 6 task card hợp lệ với schema registry cục bộ;
- YAML, Markdown fence/trailing whitespace, relative links và tham chiếu
  section của master đều đạt.

Gate Phase 0.0 vẫn IN_REVIEW / NOT PASSED. Commit này chỉ tạo documentation
baseline; không cho phép bắt đầu code application, migration, endpoint,
runtime config hay venue integration trước khi các ADR/gate bắt buộc được duyệt.
```

## 3. Tóm tắt thay đổi theo nhóm

### 3.1 Master và kiểm soát tài liệu

- Cập nhật `AI_AUTO_TRADE_MASTER_SPEC.md` để control panel phản ánh đúng:
  - Phase hiện tại là `Phase 0.0 — Documentation Closure (IN_REVIEW)`.
  - Blocker là việc review/phê duyệt ADR và artifact bắt buộc.
  - Gate gần nhất là `Phase 0.0 — IN_REVIEW`.
  - Pre-Phase 0 và Phase 0.0 không được tạo application code, migration,
    endpoint, runtime configuration hoặc tích hợp venue.
- Tạo `docs/DOCS_INDEX.md` làm điểm vào duy nhất cho toàn bộ hồ sơ.
- Tạo document-control, RACI, RAID register và requirements traceability.

### 3.2 Product, kiến trúc và domain

- Xác định scope MVP, yêu cầu chức năng, yêu cầu phi chức năng/bảo mật và glossary.
- Mô tả kiến trúc C4 cấp context/container, trình tự runtime, policy ngôn ngữ
  và công nghệ.
- Chuẩn hóa domain model, trạng thái OMS, policy risk và policy accounting.

### 3.3 Dữ liệu và database design

- Mô tả data architecture, ERD, data dictionary và database standards.
- Xác định quy tắc transaction, concurrency, outbox/inbox, idempotency,
  migration, backfill, backup/restore và retention.
- Những tài liệu này là design authority ở trạng thái `DRAFT`; chưa phải DDL
  hoặc migration có thể triển khai.

### 3.4 ADR và các quyết định cần phê duyệt

- Bổ sung ADR `0001` đến `0015`, cùng ADR register.
- Các ADR đều được giữ `DRAFT`, không tự gắn `APPROVED`.
- Nhóm ADR phải được Account Owner phê duyệt trước khi mở Phase 0:
  `0001`, `0002`, `0003`, `0004`, `0005`, `0007`, `0011`, `0012`, `0014`.
- ADR `0015` về authentication/session/machine identity vẫn là điểm cần quyết
  định trước khi khởi động control plane thật.

### 3.5 Engineering, security và vận hành

- Bổ sung quy ước repository, Python coding standards, test strategy,
  thiết kế CI/CD và AI coding protocol.
- Bổ sung threat model, access-control matrix, secrets/key-management,
  auth/session policy, SLO/SLI/alert policy.
- Bổ sung runbook cho unknown order, stream gap, reconciliation mismatch,
  kill switch, restart trading node, database unavailable, credential rotation
  và backup/restore.

### 3.6 Contract, task và gate controls

- Bổ sung contract registry làm nguồn tra cứu contract chính thức.
- Bổ sung OpenAPI 3.1, error catalog, schema cho task card/deployment manifest,
  control command, submit order, integration event envelope và order event.
- Bổ sung fixture hợp lệ cho từng schema và quy tắc resolve `$ref` hoàn toàn
  offline từ registry `$id` trong repository.
- Bổ sung sáu task card cho các workstream `0.0.0` đến `0.0.5`, kèm evidence
  directory, review checklist và gate record Phase 0.0.

## 4. Kết quả kiểm tra đã thực hiện

| Hạng mục | Kết quả | Ghi chú |
|---|---|---|
| Inventory artifact Phase 0.0 | PASS | Có đủ 85/85 artifact bắt buộc. |
| JSON Schema Draft 2020-12 | PASS | Đã kiểm tra 6 schema. |
| Fixture contract | PASS | Đã xác thực 6 fixture với registry `$id` cục bộ. |
| Task card schema | PASS | Đã xác thực 6 task card active. |
| YAML và OpenAPI | PASS | YAML parse thành công; OpenAPI có cấu trúc 3.1 hợp lệ. |
| Markdown quality | PASS | Không lỗi fence hoặc trailing whitespace. |
| Relative links | PASS | Không có liên kết nội bộ bị hỏng. |
| Master section references | PASS | Không có tham chiếu section không tồn tại. |
| Stale references | PASS | Không còn đường dẫn cũ như `docs/03-data` hoặc `configs/schemas`. |

## 5. Trạng thái gate sau commit

Commit này **không** là bằng chứng để mở Phase 0.

`docs/evidence/gates/phase-0.0/gate-record.md` phải tiếp tục giữ:

```text
Phase status: IN_REVIEW
Gate decision: NOT PASSED
```

Lý do: các quyết định kiến trúc/domain/accounting/delivery bắt buộc vẫn đang
chờ Account Owner review và phê duyệt. Chỉ thay đổi trạng thái gate khi có:

1. Quyết định phê duyệt được ghi nhận với người phê duyệt và thời gian UTC.
2. ADR liên quan chuyển trạng thái đúng quy trình.
3. Document register và gate record được cập nhật trong cùng thay đổi review.
4. Bằng chứng kiểm tra được lưu ở đường dẫn evidence phù hợp.

## 6. Kiểm tra trước khi commit

Thực hiện các bước sau trước khi tạo commit thật:

```powershell
git status --short
git diff --check
git diff -- AI_AUTO_TRADE_MASTER_SPEC.md
git add AI_AUTO_TRADE_MASTER_SPEC.md docs contracts tasks COMMIT_NOTES.md COMMIT_MESSAGE.txt
git diff --cached --stat
git diff --cached --check
```

Xác nhận rằng staged changes chỉ gồm tài liệu, schema, fixture, task và evidence
của Phase 0.0. Không stage secret, file `.env`, credential, binary lớn, database
dump, output test tạm thời hoặc thay đổi source code ngoài phạm vi.

Sau khi kiểm tra, tạo commit bằng:

```powershell
git commit -F COMMIT_MESSAGE.txt
```

`COMMIT_MESSAGE.txt` là file message sẵn sàng dùng trực tiếp cho Git;
`COMMIT_NOTES.md` là hồ sơ diễn giải chi tiết và checklist. Commit cả hai file
để người review có thể đối chiếu phạm vi thay đổi với quyết định gate.

## 7. Phạm vi không thay đổi trong commit này

- Không có Python application source, Flutter source hoặc service runtime mới.
- Không có migration, DDL production, seed data hoặc kết nối database thật.
- Không có API chạy thực tế, broker, scheduler, CI pipeline thực thi hoặc hạ tầng cloud.
- Không có credential, API key, private key, token, dữ liệu khách hàng hoặc dữ liệu giao dịch.
- Không có venue adapter, lệnh giao dịch, paper execution hay live execution.

## 8. Bước tiếp theo sau commit

1. Review tài liệu theo thứ tự trong `docs/DOCS_INDEX.md`.
2. Account Owner phê duyệt hoặc yêu cầu sửa các ADR bắt buộc.
3. Hoàn thiện evidence review và quyết định gate Phase 0.0.
4. Chỉ khi gate Phase 0.0 `PASSED`, mới tạo task card Phase 0 và bắt đầu
   foundation implementation theo master.
