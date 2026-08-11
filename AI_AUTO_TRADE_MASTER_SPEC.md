# AI Auto Trade — Đặc tả triển khai chuẩn

> **Hiến pháp kỹ thuật và chỉ mục nguồn sự thật của dự án.** Mọi quyết định kỹ thuật, vận hành, an toàn và phase delivery phải tuân theo tài liệu này. Với các chi tiết có thể thực thi, ADR đã phê duyệt và machine-readable contract được tài liệu này chỉ định là nguồn sự thật ở phạm vi hẹp của chúng; nếu có mâu thuẫn, dừng triển khai và xử lý theo §1.5.

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 2.3.1 |
| Trạng thái | Phase 0 — Foundation (IN_PROGRESS) |
| Chủ sở hữu | Chủ tài khoản giao dịch / người vận hành |
| Phạm vi đầu tiên | Một sàn crypto spot, một account, paper/testnet trước |
| Ngôn ngữ chính | Python 3.12.x |
| Mục tiêu | Xây một nền tảng giao dịch có thể kiểm thử, audit, phục hồi và nâng cấp từng phần |
| Nguyên tắc an toàn | Không có lệnh live trước khi vượt toàn bộ Go/No-Go gate |
| Lần rà soát gần nhất | 2026-08-11 |
| Thay đổi chính v2.1 | Bổ sung thiết kế DRAFT cho AI đa provider/BYOK: user chọn provider/model đã duyệt, secret ingress write-only, provider catalog, egress/budget và zero-execution boundary |
| Thay đổi chính v2.1.1 | Cập nhật §1.5 artifact pack tree và các tham chiếu đường dẫn docs/ theo tái cấu trúc lớp Backend/Frontend/Shared/Governance (GOV-CLASS-001); không đổi quyết định kiến trúc/domain/risk/security nào |
| Thay đổi chính v2.2.0 | Sửa mâu thuẫn nội bộ do audit sâu phát hiện: §8.11 deadline accounting policy thống nhất "trước Phase 1" (khớp §7.8); §7.6 bổ sung `outbox_delivery_state` vào platform inventory; §4.6 bổ sung `tests/state_machine/`; §4.7 bổ sung `apps/secret_ingress` (Phase 6) và làm rõ ai_worker binding lease; §4.8 chốt fixture format theo registry. Chỉ sửa nhất quán, không thêm capability mới |
| Thay đổi chính v2.2.1 | Audit chéo hậu bổ sung: §1.5 cây frontend phản ánh 8 artifact FE-* (hết placeholder); §14.2 Task 0.1 output trỏ manifest ENG-REPO-001 §2b và ghi nhận README/AGENTS đã tồn tại; §16.1 bỏ "Từ Task 0.1" cho AGENTS.md; §0.3 thêm OD-009 (vị trí repo frontend + Dart gates) và OD-010 (đóng GAP OpenAPI cho mandatory ops views). Chỉ sửa nhất quán/registry, không thêm capability |
| Thay đổi chính v2.2.2 | Audit toàn diện 2026-08-02: §14.2 đăng ký Task 0.0.6 (AI BYOK baseline) và sửa mô tả 0.0.0 thành "0.0.1–0.0.6"; đồng bộ owner/reviewer 0.0.3/0.0.4 với card YAML; gỡ deadlock nghiệm thu Phase 0.0 ↔ precondition card 0.1 (card đủ điều kiện chuyển READY khi gate ký, không yêu cầu READY trước gate); recap ADR bổ sung "0016 trước Phase 6"; §3.1 thống nhất deadline ADR Nautilus với §15.1; §1.5 bổ sung waiver-register/compliance-register/incident-record/versioning-release-policy/logging-standard vào cây; §4.6 bổ sung .gitignore, COMMIT_NOTES.md; §16.2 sửa `expiry` thành `expiry_at` khớp schema; control panel cập nhật validation record hiện hành. Chỉ sửa nhất quán/registry, không thêm capability |
| Thay đổi chính v2.2.3 | Đồng bộ state sau khi Task 0.1–0.4 DONE (Account Owner approve 2026-08-06): control panel §0 phản ánh Phase 0 IN_PROGRESS, việc kế tiếp là Task 0.5 — Operations skeleton (chưa có task card); §4.6 gỡ COMMIT_NOTES.md (xóa khỏi repo theo quyết định Account Owner 2026-08-10, nội dung nằm trong git history); ghi nhận `.kiro/` hooks (tool-specific, không thuộc artifact pack) đã xóa. Chỉ sửa nhất quán/registry, không thêm capability |
| Thay đổi chính v2.2.4 | Đồng bộ Enterprise-Grade cho OpenAI Codex theo task 0.0.7: đăng ký task tài liệu Codex, đồng bộ trạng thái Task 0.5.1/0.5.2, làm rõ AGENTS.md là instruction source chính, bổ sung revalidation evidence sau substantive change và phân biệt local validation với CI enforcement. Không mở runtime AI/API/venue và không thêm capability giao dịch |
| Thay đổi chính v2.2.5 | Account Owner revalidate Phase 0.0 tại 2026-08-10T20:07:02Z; Task 0.0.7 DONE; mở Task 0.5.1 READY với allowlist sample manifest rõ ràng; Task 0.5.2 vẫn BLOCKED phụ thuộc 0.5.1. Safe auto mode chỉ tự động preflight/implementation trong card, không bỏ checkpoint human |
| Thay đổi chính v2.2.6 | Account Owner approve Task 0.5.1 tại 2026-08-11T00:30:47Z; chuyển card completed và mở Task 0.5.2 READY trên branch `task/0.5.2-*`; vẫn giữ local-only/no-auth/no-venue/no-DB scope |
| Thay đổi chính v2.2.7 | Account Owner xác định DONE Task 0.5.2 tại 2026-08-11T02:14:42Z; chuyển card vào `tasks/completed/`, đồng bộ evidence/control references; Task 0.6 vẫn BLOCKED vì OD-001 OPEN và chưa có card READY |
| Thay đổi chính v2.2.8 | Account Owner xác nhận tiếp tục local simulator/no venue tại 2026-08-11T02:26:26Z; mở Task 0.6 Capability draft ở trạng thái READY trên branch `task/0.6-*`; OD-001 vẫn OPEN và external venue vẫn bị cấm |
| Thay đổi chính v2.2.9 | Bắt đầu thực thi Task 0.6 lúc 2026-08-11T02:29:48Z; card chuyển READY → IN_PROGRESS sau khi tạo capability matrix draft, vẫn docs-only/local simulator/no venue |
| Thay đổi chính v2.3.0 | Hoàn tất phần operator của Task 0.6 lúc 2026-08-11T02:32:26Z; chuyển card IN_PROGRESS → REVIEW, giữ OD-001 OPEN và không mở application/runtime code |
| Thay đổi chính v2.3.1 | Account Owner xác định DONE Task 0.6 tại 2026-08-11T19:16:45Z; chuyển card vào `tasks/completed/`; Phase 1 tiếp theo chỉ được mở bằng task card code riêng, vẫn không venue bên ngoài |

---

## Mục lục

1. [Start here — control panel](#0-start-here--control-panel)
2. [Cách dùng và quản trị tài liệu](#1-cách-dùng-và-quản-trị-tài-liệu)
3. [Mục tiêu, phạm vi MVP và phần hoãn](#2-mục-tiêu-phạm-vi-mvp-và-phần-hoãn)
4. [Các quyết định kiến trúc đã chốt](#3-các-quyết-định-kiến-trúc-đã-chốt)
5. [Kiến trúc, ranh giới và luật phụ thuộc](#4-kiến-trúc-ranh-giới-và-luật-phụ-thuộc)
6. [Hợp đồng domain chuẩn](#5-hợp-đồng-domain-chuẩn)
7. [Mode, môi trường, cấu hình và release](#6-mode-môi-trường-cấu-hình-và-release)
8. [Eventing, persistence và quyền sở hữu dữ liệu](#7-eventing-persistence-và-quyền-sở-hữu-dữ-liệu)
9. [Trading core: strategy, risk, OMS, ledger và reconciliation](#8-trading-core-strategy-risk-oms-ledger-và-reconciliation)
10. [Market data, catalog lịch sử và backtest](#9-market-data-catalog-lịch-sử-và-backtest)
11. [Adapter và tích hợp bên ngoài](#10-adapter-và-tích-hợp-bên-ngoài)
12. [Control plane, API, UI và phân quyền](#11-control-plane-api-ui-và-phân-quyền)
13. [Bảo mật, quan sát và vận hành](#12-bảo-mật-quan-sát-và-vận-hành)
14. [Chất lượng, kiểm thử và kỷ luật delivery](#13-chất-lượng-kiểm-thử-và-kỷ-luật-delivery)
15. [Roadmap và Go/No-Go gates](#14-roadmap-và-gono-go-gates)
16. [ADR, quyết định của owner và Definition of Done](#15-adr-quyết-định-của-owner-và-definition-of-done)
17. [Quy tắc bắt buộc cho AI Coding Agent](#16-quy-tắc-bắt-buộc-cho-ai-coding-agent)

---

## 0. Start here — control panel

Đây là phần duy nhất cần đọc trước khi bắt đầu một ngày làm việc. Các phần kỹ thuật phía sau là chuẩn tham chiếu; bảng này là trạng thái vận hành hiện tại và phải được cập nhật mỗi khi hoàn thành gate, thay đổi owner hoặc phát hiện blocker.

| Field | Giá trị hiện tại | Owner | Evidence / ghi chú |
|---|---|---|---|
| Current phase | Phase 0 — Foundation (IN_PROGRESS) | Account Owner | Code chỉ trong `allowed_globs` của task card READY |
| Việc kế tiếp | Phase 1 — tạo task card code đầu tiên cho deterministic primitives (UUIDv7/Decimal/UTC Clock/RandomSource); hiện chưa có card `READY` | Account Owner | §14 Phase 1; không code trước khi card và allowlist được mở |
| Môi trường đang chạy | Chưa có | Technical Operator | Không dùng credential venue |
| Deployment manifest | Chưa có | Technical Operator | Chỉ tạo từ Phase 2 |
| Gate gần nhất | Phase 0.0 — **APPROVED / REVALIDATED** 2026-08-10T20:07:02Z | Account Owner | Gate record v0.5.0 + evidence Task 0.0.7 |
| Blocker code | Task 0.1–0.4, 0.0.7, 0.5.1, 0.5.2, 0.6 DONE; Phase 1 task card chưa mở; external venue vẫn BLOCKED bởi OD-001 | Account Owner | §14, §16 và task cards |
| Blocker live | Venue, jurisdiction, account, risk cap chưa chốt | Account Owner | §15.2 và Open Decision Register |
| Lần rà soát | 2026-08-12 | Account Owner | v2.3.1; Task 0.6 DONE lúc 2026-08-11T19:16:45Z; Phase 1 task card code chưa mở; OD-001 vẫn OPEN |

### 0.1 Cách bắt đầu đúng

1. Đọc bảng control panel.
2. Xác định phase hiện tại và chỉ làm task nhỏ kế tiếp ở §14.
3. Kiểm tra Open Decision Register và ADR bắt buộc cho task đó.
4. Thực hiện Definition of Ready trước khi code.
5. Lưu test/artifact/evidence vào gate record trước khi đánh dấu phase hoàn tất.

Không được tự suy luận rằng một phase đã qua chỉ vì code chạy được. Một gate chỉ pass khi có evidence, actor, ngày chạy và approver theo mẫu ở §14.2.

### 0.2 Definition of Ready cho mọi task

Một task chỉ được bắt đầu khi:

- phase và mục tiêu task được nêu rõ;
- dependency/ADR liên quan đã có hoặc được ghi là blocker;
- input contract/config/fixture cần thiết đã tồn tại;
- owner và reviewer đã xác định;
- acceptance test/evidence đầu ra được nêu trước khi code.

Nếu thiếu một điều kiện, task ở trạng thái BLOCKED, không “code trước rồi tính sau”.

### 0.3 Open Decision Register

Không đặt tham số live bằng phỏng đoán. Mọi quyết định mở dùng bảng này và được cập nhật trong tài liệu:

| ID | Quyết định / blocker | Phase bị chặn | Owner | Hạn chốt | Evidence cần có | Trạng thái |
|---|---|---|---|---|---|---|
| OD-001 | Venue/testnet đầu tiên | Phase 3 | Account Owner | Trước Phase 3 | Capability matrix + terms | OPEN |
| OD-002 | Jurisdiction, thuế và quyền dùng API | Phase 3/4 | Account Owner | Trước Phase 3 | Ghi nhận kiểm tra | OPEN |
| OD-003 | Account/sub-account và instrument universe | Phase 3 | Account Owner | Trước Phase 3 | Approval record | OPEN |
| OD-004 | Risk cap canary và shutdown policy | Phase 4 | Risk Approver | Trước Phase 4 | Signed policy | OPEN |
| OD-005 | Alert channel, backup location, live topology | Phase 3/4 | Security/Backup Owner | Trước Phase 3 | Runbook + drill | OPEN |
| OD-006 | Control-plane authentication provider and session model | Phase 3 | Security/Backup Owner | Trước Phase 3 | ADR + permission matrix | OPEN |
| OD-007 | Legal/compliance applicability and data-retention obligations | Phase 2/3 | Account Owner | Trước Phase 2 | Assessment record | OPEN |
| OD-008 | AI BYOK: provider/model catalog, owner scope, secret ingress, data-egress/privacy, budget và fallback policy | Phase 6 | Account Owner + Security/Backup Owner | Trước Phase 6 | ADR-0016 + catalog/policy + security review | OPEN |
| OD-009 | Vị trí repo frontend (monorepo `frontend/` vs repo riêng) và Dart quality-gate baseline (FE-ARC-001 §8–§9) | Phase 5 | Account Owner | Trước Phase 5 task card đầu tiên | Decision record + cập nhật FE-ARC-001 §8/§9, ENG-REPO-001 | OPEN |
| OD-010 | Đóng GAP register OpenAPI (FE-SCREEN-001 §4): route cho mandatory ops views + đồng bộ terminal_reason enum với DOM-002 | Phase 5 (view 1–6 cũng là testnet gate evidence theo OPS-SLO-001 — title OPS-001 — §4.2) | Technical Operator + Account Owner | Trước Phase 5 task card đầu tiên | openapi.yaml version mới + fixture + contract review record | OPEN |

Một record OPEN chặn phase được nêu. Chỉ chuyển sang RESOLVED khi có evidence URI/path và actor đã phê duyệt.

---

## 1. Cách dùng và quản trị tài liệu

### 1.1 Quy ước bắt buộc

- **MUST**: bắt buộc. Không được bỏ qua.
- **SHOULD**: mặc định phải làm. Nếu bỏ qua phải có ADR được owner chấp thuận.
- **MAY**: tùy chọn, chỉ làm khi có nhu cầu đã đo được.
- Mỗi task chỉ triển khai đúng phase đã được giao. Không tự làm trước phần của phase sau.
- Nếu code khác tài liệu, dừng lại, nêu khác biệt và tạo đề xuất ADR. Không âm thầm sửa kiến trúc.
- Mọi thay đổi kiến trúc, persistence, risk, order lifecycle, credential hoặc live deployment phải có ADR.

### 1.2 Thước đo thành công

Mục tiêu đầu tiên **không phải PnL**. Hệ thống được coi là tiến bộ khi:

1. Cùng input, cùng phiên bản code/config/data/seed cho cùng kết quả trong replay/backtest.
2. Một quyết định giao dịch truy vết được từ market event đến risk verdict, order, fill và ledger.
3. Crash hoặc mất kết nối không tạo lệnh trùng.
4. Reconciliation phát hiện và chặn giao dịch khi state nội bộ khác sàn.
5. Paper/testnet hoạt động ổn định trước khi bàn đến live.

### 1.3 Quy tắc thay đổi

- Mọi public contract có version.
- Không sửa migration đã áp dụng.
- Không đổi chữ ký public port đã phát hành; tạo version hoặc port mới khi cần.
- Không đổi trực tiếp config của deployment đang chạy. Tạo config/deployment manifest mới.
- Không dùng biến môi trường kiểu LIVE=true để biến process paper thành live.

### 1.4 Kiểm soát phiên bản tài liệu

- Mỗi thay đổi substantive tăng phiên bản tài liệu và ghi một dòng changelog ở đầu.
- Thay đổi architecture/risk/security/live gate cần ADR và Account Owner phê duyệt.
- Thay đổi trạng thái control panel, gate record hoặc Open Decision Register không làm đổi specification version nhưng phải có ngày và actor.
- Không copy một phần tài liệu này sang prompt rồi xem bản copy là source of truth; prompt phải trỏ lại file này.

### 1.5 Authority hierarchy, artifact pack và traceability

Master này quy định policy, ranh giới, gate và các lựa chọn architecture. Nó không cho phép AI tự suy luận chi tiết có thể thực thi. Authority theo thứ tự:

~~~text
1. Regulatory/legal constraint
2. Master specification này + ADR đã APPROVED, gồm non-waivable safety invariant
3. Explicit owner decision trong phạm vi mà (1) và (2) cho phép
4. Versioned DDL, OpenAPI, JSON Schema, config schema và contract registry
5. Approved task card / gate record
6. Code và generated artifact
7. Test fixture, log và report
~~~

Nếu artifact cấp thấp mâu thuẫn cấp cao hơn, trạng thái là BLOCKED. Nếu contract machine-readable mâu thuẫn với master ở field chi tiết, không tự sửa code: tạo issue/ADR hoặc cập nhật master và contract trong cùng approved change. Explicit owner decision chỉ được chốt scope/capital/venue/risk parameter trong quyền của owner; nó không được override regulatory constraint, non-waivable safety invariant, credential rule hoặc audit requirement.

| Câu hỏi cần trả lời | Source of truth thực thi sau khi được phê duyệt |
|---|---|
| Scope, phase, risk/security policy, dependency rule | Master + ADR `APPROVED` |
| Physical database table/index/constraint | Alembic migration đã apply + schema snapshot; dictionary giải thích nhưng không thay DDL |
| HTTP path/payload/status/error | `contracts/api/openapi.yaml` |
| Command, event, config payload | JSON Schema versioned trong `contracts/` |
| Effective runtime config / deployment identity | validated immutable deployment manifest + effective config hash |
| Financial/audit facts | append-only journal/posting/event/audit record đã commit |
| Gate result | signed gate record và evidence hash |

Pre-Phase 0 phải tạo artifact pack sau; chưa cần implementation code, nhưng từng artifact phải có owner, version và review:

Kể từ v2.1.1, artifact pack được tổ chức theo lớp Backend/Frontend/Shared/Governance thay vì theo số thứ tự 00–06 (xem `docs/governance/documentation-layer-classification.md`, GOV-CLASS-001, cho lý do phân loại từng artifact):

~~~text
docs/
  governance/
    DOCS_INDEX.md
    document-control.md
    raci.md
    raid-register.md
    requirements-traceability.md
    documentation-layer-classification.md
    waiver-register.md
    compliance-register.md
    adr/
      README.md
    templates/{adr,task-card,gate-record,incident-record}.md
    evidence/{gates,tasks}/
  shared/
    glossary.md
    product/non-functional-requirements.md
  backend/
    product/{product-charter,functional-requirements}.md
    architecture/{c4-context,c4-container,runtime-sequences,language-and-technology-policy,ai-provider-byok-architecture}.md
    domain/{canonical-domain-model,oms-state-machine,risk-policy,accounting-policy}.md
    data/{data-architecture,erd,data-dictionary,database-standards,transaction-and-concurrency,db-operations,migration-backfill-playbook}.md
    engineering/{repository-conventions,coding-standards-python,test-strategy,ci-cd-design,ai-coding-protocol,versioning-release-policy,logging-standard}.md
    security-ops/{threat-model,access-control-matrix,auth-session-policy,secrets-and-key-management,slo-sli-alert-policy,runbook-index,ai-byok-security-policy}.md
    security-ops/runbooks/
    adr/0001-…0016-*.md
    contracts/contract-registry.md
  frontend/
    README.md  # FE-INDEX-001 — chỉ mục bộ tài liệu frontend (input Phase 5/6, không cho phép code trước gate)
    {product,architecture,design,security,engineering}/  # FE-CHARTER/SCREEN/API/ARC/DS/SEC/TEST-001
contracts/
  api/openapi.yaml
  commands/
  events/
  config/
    task-card.v1.schema.json
  errors/error-catalog.md
  fixtures/
tasks/
  active/
  completed/
~~~

Mỗi functional requirement dùng ID dạng FR-<DOMAIN>-<NNN>; mỗi non-functional requirement dùng NFR-<DOMAIN>-<NNN>; mỗi security/control requirement dùng SEC-<DOMAIN>-<NNN>. Requirements traceability phải liên kết Requirement -> ADR -> contract/schema -> module -> test -> gate evidence. Không có traceability thì feature chưa được phép vào implementation task.

### 1.6 Document control, RACI và phân loại thay đổi

Mỗi artifact trong pack phải có: ID/tên, version, status (`DRAFT`, `IN_REVIEW`, `APPROVED`, `SUPERSEDED`), owner, approver, ngày hiệu lực, link requirement/ADR và lịch sử thay đổi. `APPROVED` là trạng thái duy nhất có thể mở gate hoặc làm input cho code. `SUPERSEDED` được giữ read-only cùng link tới artifact thay thế.

| Artifact / quyết định | Responsible (soạn/chạy) | Accountable (chịu trách nhiệm cuối) | Consulted | Phê duyệt tối thiểu |
|---|---|---|---|---|
| Master, scope, roadmap, ADR kiến trúc | Technical Operator | Account Owner | Risk + Security Owner khi ảnh hưởng | Account Owner |
| Risk policy, kill switch, manual approval | Risk Approver | Risk Approver | Technical Operator | Account Owner nếu canary cap/scope |
| Data dictionary, ERD, migration, contract | Technical Operator | Technical Operator | Context owner, Security Owner nếu sensitive | reviewer theo task card |
| Security/auth/secrets/backup/runbook | Security/Backup Owner | Security/Backup Owner | Technical Operator | Account Owner cho canary/live scope |
| Gate record và evidence | Technical Operator | role nêu ở gate | Risk/Security Owner khi áp dụng | gate approver ở §14.2 |

Phân loại thay đổi:

- **Editorial:** không đổi meaning/contract; review thường, không cần ADR.
- **Compatible contract/config:** thêm field optional hoặc capability không ảnh hưởng consumer cũ; cần schema compatibility test.
- **Breaking/domain/data:** thay state, semantic, public wire contract, DDL hoặc migration; cần ADR/task card, migration/rollback plan và versioning.
- **Safety/security/live:** ảnh hưởng risk, ledger, credential, execution, authorization hoặc canary; cần ADR, đúng role phê duyệt và gate evidence mới.

Không một người/AI được tự phê duyệt thay đổi safety/security/live mà không có evidence và role độc lập được nêu ở task/gate. Trong Phase 0 đến paper/testnet, một người có thể thực hiện nhiều role nhưng phải ghi từng role action, re-auth và evidence riêng. Trước canary/live, approval safety/security/risk phải có một reviewer human thứ hai, không giữ role vận hành của thay đổi đó; nếu không có reviewer này, canary/live là BLOCKED và không được waiver.

---

## 2. Mục tiêu, phạm vi MVP và phần hoãn

### 2.1 MVP chính thức

MVP là một vertical slice hoàn chỉnh:

~~~text
market event
  -> strategy mẫu
  -> deterministic risk
  -> simulated/testnet execution
  -> order/fill events
  -> double-entry ledger
  -> reconciliation
  -> audit, replay và alert
~~~

Phạm vi ban đầu bị giới hạn bắt buộc:

- 1 venue crypto spot.
- 1 account.
- 1 hoặc vài instrument đã được owner phê duyệt.
- 1 strategy mẫu đơn giản, nhằm kiểm chứng hệ thống chứ không nhằm tối ưu lợi nhuận.
- Backtest, replay, paper và testnet trước.
- Một người phát triển/vận hành; modular monolith, không microservice.

### 2.2 Mục tiêu chức năng

Đây là baseline requirement có thể trace trước khi tách đầy đủ vào `docs/backend/product/`. Task implementation phải tham chiếu ID, không chỉ tham chiếu một câu mô tả.

| ID | Requirement baseline | Acceptance source chính |
|---|---|---|
| FR-MKT-001 | Chuẩn hóa market data, lưu lineage/history và kiểm tra chất lượng dữ liệu. | §5.3, §9, dataset/golden evidence |
| FR-STR-001 | Chạy strategy theo cùng contract ở backtest, replay, paper và testnet/canary theo scope. | §8.1–§8.3, replay/golden test |
| FR-EXEC-001 | Tạo OrderIntent, kiểm tra risk, submit/cancel, xử lý fill/fee và outcome không rõ. | §5.4–§5.5, §8.4–§8.10 |
| FR-LED-001 | Lưu ledger, position, balance và PnL có thể đối soát. | §7.8, §8.11, ledger property/rebuild test |
| FR-REC-001 | Khôi phục sau crash, phát hiện unknown outcome và không gửi trùng lệnh. | §8.6–§8.9, chaos/reconciliation evidence |
| FR-RSK-001 | Áp dụng risk, reservation và kill switch theo global, venue, account, strategy, instrument. | §8.4–§8.5, §8.10 |
| FR-OPS-001 | Cung cấp API/CLI cho vận hành, audit, reconciliation và deployment. | §11, OpenAPI/command contract |
| NFR-DET-001 | Cùng code/config/data/seed phải cho cùng result trong replay/backtest. | §1.2, §9.7, §13.5 |
| NFR-AUD-001 | Quyết định giao dịch phải truy vết market event → risk → order → fill → ledger. | §1.2, §7.8, audit evidence |
| NFR-SAFE-001 | Không duplicate order, không risk bypass, không imbalance ledger và fail closed khi state không tin cậy. | §6.3, §13.4, Phase 1 gate |
| NFR-SEC-001 | Credential least-privilege; AI/UI không có đường đặt lệnh trực tiếp. | §10.6, §11, §12 |
| NFR-OPS-001 | Runtime có health, alert, restore/reconciliation và runbook có evidence. | §12, §14 gate |

`docs/backend/product/functional-requirements.md` và `docs/shared/product/non-functional-requirements.md` phải mở rộng bảng này bằng acceptance criteria cụ thể, priority, owner và trạng thái. Không được đổi ID/meaning đã được implementation dùng; thay vào đó tạo requirement version/supersession rõ ràng.

### 2.3 Không nằm trong phạm vi giai đoạn đầu

Không xây các phần dưới đây trước khi vertical slice paper chứng minh ổn định:

- HFT, colocation hoặc tối ưu sub-millisecond.
- Futures, margin, leverage, short selling, multi-leg arbitrage.
- Nhiều sàn, MT5, Interactive Brokers hoặc nhiều account.
- Kafka, NATS, Redis, Kubernetes hoặc microservices.
- Full Flutter dashboard.
- MLflow, vector memory, graph database, LLM-generated code hoặc self-learning.
- Tự deploy strategy/model lên live.
- Rút tiền, chuyển tiền tự động hoặc quyền withdrawal.

### 2.4 Quy tắc mở rộng phạm vi

Mỗi capability mới phải được thêm qua:

1. ADR mô tả mục tiêu, ảnh hưởng và rollback.
2. Capability contract/adapter test.
3. Risk policy và runbook tương ứng.
4. Gate paper/testnet riêng trước khi được phép dùng live.

---

## 3. Các quyết định kiến trúc đã chốt

| Chủ đề | Quyết định chuẩn | Lý do |
|---|---|---|
| Kiến trúc | Modular monolith, hexagonal, event-driven có chọn lọc | Đủ rõ ranh giới, ít chi phí vận hành cho một người |
| Runtime language | Python 3.12.x | Một ngôn ngữ cho domain, application, adapter, worker, CLI và test trong MVP |
| Domain | Python thuần + shared kernel | Tránh framework/vendor xâm nhập logic giao dịch |
| DTO/config | Pydantic v2 ở API, adapter và config boundary | Validation/serialization tốt, không làm bẩn domain |
| API | FastAPI + OpenAPI | Control plane rõ contract |
| Persistence | PostgreSQL 16.x là system of record từ Phase 0 | Transaction, concurrency, audit và recovery đáng tin cậy |
| Historical data | Parquet phân vùng + DuckDB/research reader | Không làm phình OLTP database |
| TimescaleDB | DEFERRED; chỉ đánh giá sau khi đo nhu cầu time-series và có ADR | Không bắt buộc domain phụ thuộc extension |
| pgvector | Chỉ từ Phase AI/memory | Không mang độ phức tạp vào MVP |
| Migration | SQLAlchemy 2 + Alembic | Version hóa schema có kiểm soát |
| Package/env | uv + pyproject.toml + lock file | Build tái lập |
| Trading kernel | NautilusTrader DEFERRED đến ADR 0006, không dependency Phase 0–4 | Không cho AI tự thêm kernel trước khi boundary/mapping được chốt |
| CCXT | Chỉ prototype, discovery hoặc read tooling | Không là execution core mặc định cho live |
| Event delivery | In-process typed bus + PostgreSQL outbox/inbox | Gọn nhưng có delivery semantics rõ |
| UI | API/CLI trước; Flutter ở phase sau | UI không được chặn trading path |
| LLM/BYOK | AI worker provider-neutral, proposal-only; user chọn provider/model đã được duyệt và tự cấp key qua connection bảo mật | Không bắt buộc OpenAI, không có đường trực tiếp đến execution, không có arbitrary endpoint |
| Observability | Structured logs + OpenTelemetry-compatible tracing + metrics | Debug/audit xuyên suốt |
| Type checking | Pyright strict | Một tool duy nhất, không cho AI chọn mypy thay thế |
| Internal ID | UUIDv7 | Có thứ tự thời gian, chuẩn duy nhất trong PostgreSQL |
| Financial number | Decimal domain + NUMERIC(38,18) DB | Không dùng float; adapter từ chối instrument vượt scale v1 |
| Canonical hash | UTF-8 canonical JSON v1 + SHA-256 | Hash reproducible cho config/request/audit, không hash JSON tùy serializer |

### 3.1 Quyết định về NautilusTrader

NautilusTrader **không sở hữu canonical domain**. Hệ thống này vẫn sở hữu:

- order intent và risk decision;
- OMS state machine;
- portfolio ledger;
- canonical event contracts;
- audit và reconciliation.

NautilusTrader chỉ được dùng sau adapter cho backtest/runtime khi phù hợp. Một logic không được triển khai hai lần. Phải có ADR xác định rõ mapping và phần nào Nautilus thực sự đảm nhiệm trước khi Nautilus được đưa vào runtime, và không muộn hơn khi mở Phase 5 (khớp deadline ADR-0006 tại §15.1).

### 3.2 Các lựa chọn kỹ thuật đã đóng

AI không được chọn lại các giá trị sau:

| Chủ đề | Chuẩn bắt buộc |
|---|---|
| Internal identifier | UUIDv7, PostgreSQL UUID type; không dùng ULID/string UUID mới |
| Domain finance | Decimal; không dùng float/fixed-point tự phát |
| Database finance | NUMERIC(38,18); scale của instrument phải nhỏ hơn hoặc bằng 18, nếu không capability bị REJECTED đến khi có ADR/migration |
| Timestamp | TIMESTAMPTZ UTC; serialize ISO-8601 có Z |
| Type check | Pyright strict; không thêm mypy |
| Canonical JSON | UTF-8, key sort lexicographic, không whitespace, Decimal/string timestamp canonical, không NaN/Infinity |
| Hash | SHA-256 của canonical JSON bytes |
| OS/runtime target | Linux container cho testnet/canary; Windows chỉ là local development supported |
| Research context name | research ở database, module và event namespace; không dùng research_backtest |

Hash request chỉ dùng cho audit/phát hiện thay đổi payload. Idempotency order được bảo đảm bởi client_order_id trong scope venue/account, không đặt UNIQUE toàn cục cho request hash vì hai order hợp lệ có thể có payload giống nhau.

### 3.3 Quyết định về event sourcing

Không event-source mọi bảng.

- Order lifecycle/audit events: append-only và replay được.
- Journal entries/postings: append-only, là nguồn accounting nội bộ.
- Projection: rebuild được từ event/ledger tương ứng.
- Config, reference data, deployment metadata: persistence thông thường có audit event; không bắt buộc event-sourced.

### 3.4 Quyết định về UI

- Phase đầu: CLI và FastAPI control endpoints.
- Flutter là dashboard mục tiêu ở phase sau.
- Streamlit, nếu dùng, chỉ là công cụ research/read-only tạm thời; không là control plane production.
- Dashboard không chứa secret, không gọi sàn trực tiếp và không chứa business logic.

### 3.5 Ngôn ngữ, định dạng và vùng được phép dùng

| Công nghệ / định dạng | Được dùng ở đâu | Không được dùng ở đâu |
|---|---|---|
| Python 3.12.x | domain, application, ports, adapters, FastAPI, worker, CLI, test, migration helper | không thay bằng TypeScript/Go/Rust cho MVP nếu chưa có ADR |
| SQL (PostgreSQL) | Alembic migration, repository/query đã review, DB validation được ADR cho phép | không nhét risk/domain policy tùy tiện vào SQL; không gọi SQL trực tiếp từ strategy/UI |
| YAML | config không secret, deployment manifest input, CI declaration | không giữ secret hoặc dùng như kênh override risk/business không qua schema |
| JSON / JSON Schema | OpenAPI, command/event/config schema, fixture, wire payload | không dùng JSONB thay cho domain/financial state có cấu trúc |
| Markdown | specification, ADR, runbook, gate evidence, task card | không phải runtime configuration |
| Shell / PowerShell | bootstrap, lint/test/CI helper có idempotency | không chứa business/risk/execution logic |
| Dart / Flutter | dashboard Phase 5 trở đi, chỉ qua Control API | không trước gate Phase 5; không venue/DB/secret/direct trading logic |

Mọi package/runtime khác (bao gồm Node.js, TypeScript, Go, Rust, Java, Redis, Kafka, NATS, Kubernetes, additional database hay orchestration framework) là **forbidden by default**. Muốn thêm phải có ADR, owner, threat/operations impact, dependency review và phase gate tương ứng.

---

## 4. Kiến trúc, ranh giới và luật phụ thuộc

### 4.1 Sơ đồ cấp cao

~~~text
                         +----------------------+
                         | Flutter / CLI / API  |
                         +----------+-----------+
                                    |
                         +----------v-----------+
                         | Control application  |
                         +----------+-----------+
                                    |
+----------------+       +----------v-----------+       +------------------+
| Market adapter | ----> | Trading applications | ----> | Venue adapter    |
+----------------+       | strategy/risk/OMS    |       +------------------+
                         | ledger/reconciliation|
                         +----------+-----------+
                                    |
              +---------------------+----------------------+
              |                                            |
   +----------v-----------+                    +-----------v----------+
   | PostgreSQL / outbox   |                    | Parquet data catalog |
   +----------------------+                    +----------------------+

AI worker chỉ đọc sanitized projection và ghi proposal/memory.
AI worker không có venue trade credential.
~~~

### 4.2 Bounded contexts

| Context | Sở hữu | Không được làm |
|---|---|---|
| reference | venue, instrument, symbol mapping, constraints | Không submit order |
| market_data | normalized ticks/trades/quotes/candles, quality | Không quyết định risk |
| strategy | strategy definition, state, signal, order intent | Không gọi network/sàn/DB trực tiếp |
| risk | policy, reservation, verdict, limit state | Không tự gửi order |
| execution | OMS, venue submission, order/fill state | Không tự bypass risk |
| portfolio_ledger | journal, postings, projections, PnL | Không overwrite lịch sử để khớp sàn |
| research | dataset, backtest, validation, report | Không ghi live state |
| operations | deployment, lease, health, incident, kill switch | Không chứa secret trong API response |
| platform | outbox, inbox, dead letter, idempotency key, contract delivery metadata | Không chứa business/risk decision hoặc thành context ẩn |
| ai_memory | LLM requests, proposal, memory | Không có credential trade hoặc quyền execution write |

### 4.3 Các layer trong mỗi context

~~~text
context/
  domain/        entities, value objects, policies, commands, events
  application/   use cases, handlers, services, DTO boundary
  ports/         interfaces/protocols cần từ bên ngoài
~~~

Adapter không nằm trong context directory. Tất cả implementation vendor/framework nằm tại src/ai_auto_trade/adapters/<kind>/<provider>/ và phải khai báo context/port mà nó implement. Điều này là topology duy nhất; không tạo adapter context-local song song.

### 4.4 Luật phụ thuộc

- Domain chỉ dùng Python standard library và shared kernel.
- Application phụ thuộc domain và ports.
- Ports mô tả nhu cầu của application/domain, không lộ vendor DTO.
- Adapter triển khai ports và được phép dùng FastAPI, SQLAlchemy, Nautilus, SDK venue, OpenAI SDK.
- Composition root/app là nơi duy nhất được wire implementation cụ thể.
- Context A không import private implementation hoặc ORM model của context B.
- Không có thư mục utils chung tùy tiện. Chỉ đưa vào shared kernel khái niệm ổn định mà ít nhất ba context cùng dùng.

### 4.5 Cấm tuyệt đối

- Domain import FastAPI, SQLAlchemy, Pydantic, CCXT, NautilusTrader, OpenAI SDK hoặc HTTP client.
- Strategy import adapter, đọc file/env/network/database trực tiếp.
- UI gọi sàn hoặc database trực tiếp.
- LLM gọi execution.
- Một context update table do context khác sở hữu, trừ transaction orchestrator được whitelist ở §7.7 và chỉ qua owner repository/port.

### 4.6 Cấu trúc repository chuẩn

~~~text
ai-auto-trade/
  README.md
  SECURITY.md
  AGENTS.md
  CONTRIBUTING.md
  CODEOWNERS
  .editorconfig
  .gitignore
  pyproject.toml
  uv.lock
  docker-compose.yml
  .env.example
  .github/workflows/
  contracts/
    api/openapi.yaml
    commands/
    events/
    config/
      task-card.v1.schema.json
    errors/error-catalog.md
    fixtures/
  tasks/
    active/
    completed/
  docs/
    governance/
      DOCS_INDEX.md
      document-control.md
      raci.md
      raid-register.md
      requirements-traceability.md
      documentation-layer-classification.md
      adr/
      evidence/{gates,tasks}/
      templates/
    shared/
      glossary.md
      product/
    backend/
      product/
      architecture/
      domain/
      data/
      engineering/
      security-ops/
      adr/
      contracts/
        contract-registry.md
    frontend/
  src/ai_auto_trade/
    shared_kernel/
    contexts/
      reference/
      market_data/
      strategy/
      risk/
      execution/
      portfolio_ledger/
      research/
      operations/
      platform/
      ai_memory/                 # Phase 6 only
    adapters/
      venues/
      persistence/
      notifications/
      llm/                       # Phase 6 only
      nautilus/                  # only after ADR 0006
    apps/
      control_api/
      trading_node/
      workers/
      cli/
  migrations/
  configs/
    base.yaml
    environments/
    services/
    venues/
    strategies/
    risk/
    deployments/
  infra/
  data/catalog/
  generated/
  scripts/
  tests/
    architecture/
    unit/
    property/
    state_machine/
    contract/
    integration/
    replay/
    golden/
    chaos/
    e2e/
    fixtures/
    factories/
~~~

### 4.7 Process, entry point và quyền runtime

Một process chỉ có một responsibility và một machine identity. Composition root của process là nơi duy nhất được import concrete adapter; không import app khác để tái sử dụng runtime state.

| Process / entry point chuẩn | Mục đích | Quyền / credential tối đa | Không được làm |
|---|---|---|---|
| `apps/control_api` | FastAPI control plane, command intake, read projection | DB control role; không có venue trade key | không chạy strategy/submit trực tiếp |
| `apps/trading_node` | strategy scheduler, risk, OMS, execution, ledger/reconciliation | DB trading role; venue credential theo manifest/mode | không expose public HTTP management surface |
| `apps/workers/data_worker` | market/reference ingest, catalog/quality | DB data role; public/testnet read credential nếu cần | không execution/risk/ledger write |
| `apps/workers/research_worker` | replay/backtest/report | catalog/research role; network disabled mặc định | không đọc trade credential hoặc OLTP write model |
| `apps/workers/ai_worker` | proposal/memory Phase 6 | sanitized read + ai_memory write; binding lease ngắn hạn theo owner/connection/revision/job — không wholesale provider key | không execution tool, venue credential hoặc config promotion |
| `apps/cli` | operator command có audit/authorization path | caller identity; không bypass Control API policy | không truy cập DB/venue trực tiếp ngoài command port được duyệt |
| `apps/secret_ingress` | BYOK secret ingress write-only, Phase 6 (ADR-0016) | secret-provider write path riêng; không đọc lại secret, không DB role khác | không expose read/list secret, không log payload, không chạy trước Phase 6 gate |

`trading_node` được phép chạy ở SHADOW, PAPER_SIMULATOR, TESTNET và CANARY; chỉ process này mới được wire `ExecutionVenuePort`. Ở SHADOW, port execution phải là disabled/fail-closed adapter và không có permission submit; ở PAPER_SIMULATOR, nó chỉ wire simulator adapter. Venue execution adapter chỉ được wire ở TESTNET/CANARY theo manifest. Testnet/canary phải chạy Linux container image đã pin digest; Windows chỉ được hỗ trợ cho local developer tooling.

### 4.8 Quy ước tên và tổ chức file

- Thư mục/module Python dùng `snake_case`; class/type dùng `PascalCase`; function/field/contract key dùng `snake_case`; enum value wire dùng `SCREAMING_SNAKE_CASE`.
- Mỗi aggregate/policy/port có module rõ nghĩa. Không dùng `utils.py`, `helpers.py`, `common.py` hay `misc.py` như nơi chứa logic không có owner.
- `domain/` chỉ chứa logic thuần; `application/` đặt use case theo capability; `ports/` đặt Protocol/interface. Concrete adapter đặt đúng `adapters/<kind>/<provider>/`.
- Test mirror source/capability: ví dụ `tests/unit/contexts/risk/...`, `tests/contract/adapters/venues/...`; fixture dùng định dạng đã đăng ký trong contract registry (`<name>.v<major>.valid.<ext>` là định dạng đã đăng ký hiện hành).
- File contract/config mang version rõ ràng (`<name>.v1.schema.json`); breaking change tạo major version mới, không overwrite v1.
- Migration dùng Alembic revision immutable, message chứa Task ID và intent; không rename/sửa migration đã apply.
- Generated artifact vào `generated/` hoặc đường dẫn task chỉ định, có banner/source link; không dùng generated file làm nơi sửa tay.

---

## 5. Hợp đồng domain chuẩn

### 5.1 Quy tắc chung

- Money, price, quantity, fee và PnL không dùng float.
- Domain dùng Decimal; database dùng NUMERIC(38,18); API serialize thành string.
- Timestamp luôn UTC, timezone-aware và ISO-8601 có Z.
- Domain không gọi current wall clock; dùng Clock được inject.
- Randomness trong strategy/simulator phải dùng RandomSource inject và seed được lưu.
- Domain objects/public events immutable.
- Tất cả public contract có schema_version.

Timestamp physical contract:

| Field | Nghĩa | Bắt buộc khi |
|---|---|---|
| occurred_at | thời điểm sự kiện xảy ra tại nguồn/domain | mọi event |
| received_at | thời điểm adapter nhận input | market/private venue event |
| processed_at | thời điểm normalize/handler hoàn tất | processed event |
| recorded_at | thời điểm PostgreSQL ghi record | audit/event/ledger |
| effective_at | thời điểm rule/reference/config có hiệu lực | versioned reference/policy |
| created_at | thời điểm tạo aggregate/command | mutable control record |
| updated_at | thời điểm state projection thay đổi | mutable projection, không dùng cho append-only record |

Tất cả các field trên là TIMESTAMPTZ UTC ở database. Domain/API dùng hậu tố _at; không dùng đồng thời event_time/received_time cho cùng nghĩa.

### 5.2 Identifier

Không truyền raw string tự do giữa các context. Dùng immutable value object cho:

- VenueId, AccountId, InstrumentId.
- StrategyDefinitionId, StrategyVersionId, StrategyInstanceId.
- RiskPolicyId, OrderIntentId, OrderId, ClientOrderId, VenueOrderId, FillId.
- JournalEntryId, DatasetVersionId, DeploymentId.
- CorrelationId, CausationId, TraceId.

ID nội bộ MUST dùng UUIDv7. ID của venue phải được lưu riêng, không làm primary key nội bộ.

ClientOrderId được execution application sinh một lần trước khi queue submission; không được strategy hoặc venue adapter tự tạo lại. ClientOrderId không bao giờ reuse trong cùng venue/account, kể cả order đã terminal.

### 5.3 Instrument và market data

Instrument phải chứa tối thiểu:

- venue và canonical symbol;
- base/quote asset;
- tick size, lot size, min/max quantity, min notional;
- precision;
- trạng thái giao dịch;
- effective_at, valid_from và valid_to của thay đổi filter/precision;
- source snapshot/checksum và adapter version tạo reference data.

Normalized market event phải có:

- event_id, schema_version, venue, instrument_id;
- occurred_at, received_at, processed_at, recorded_at;
- source sequence/trade ID khi venue có;
- price/quantity/side phù hợp;
- quality flags và correlation metadata.

### 5.4 Order contracts

Strategy chỉ tạo `ProposedOrderIntent` qua action `ProposeOrderIntent`; proposal này **không** có ClientOrderId và không phải aggregate được submit. Execution application validate/canonicalize proposal thành `OrderIntent`, sinh `OrderIntentId` và đúng một ClientOrderId trước khi gọi risk. Risk chỉ trả `RiskDecision`; chỉ execution được gửi lệnh.

OrderIntent phải có tối thiểu:

- order_intent_id và client_order_id duy nhất theo venue/account;
- account_id, venue_id, instrument_id;
- strategy_instance_id, deployment_id, correlation_id;
- side, type, quantity, limit_price/trigger_price khi phù hợp;
- time_in_force, reduce_only, post_only khi capability cho phép;
- created_at, expires_at;
- strategy/config version và input snapshot reference.
- canonical request hash dùng cho idempotency/audit.

Capability không được hỗ trợ phải bị từ chối rõ ràng trước submission; không fallback âm thầm.

#### Manual approval contract

Khi RiskDecision là REQUIRE_MANUAL_APPROVAL, OrderIntent chuyển sang trạng thái PENDING_MANUAL_APPROVAL, không tạo submission queue. Pending approval phải lưu approver role cần thiết, reason, decision expiry, input snapshot hash và policy version.

Approval không bypass risk. Khi người có quyền approve, hệ thống chạy lại full risk evaluation với snapshot mới. Nếu policy/input/state đã stale hoặc hết hạn, intent bị REJECTED/EXPIRED và cần intent mới.

### 5.5 OMS state machine chuẩn

Order state là contract triển khai, không chỉ là sơ đồ. EXTERNAL là classification về ownership/reconciliation, không phải order state.

| State hiện tại | Event hoặc guard | State kế tiếp | Side effect bắt buộc |
|---|---|---|---|
| CREATED | risk reject | RISK_REJECTED | audit reason |
| CREATED | risk requires manual approval | PENDING_MANUAL_APPROVAL | persist approval request, no submission queue |
| PENDING_MANUAL_APPROVAL | valid approver approves + fresh risk approves | RISK_APPROVED | persist approval/audit and reservation |
| PENDING_MANUAL_APPROVAL | approval expiry | EXPIRED | audit reason; no submission |
| PENDING_MANUAL_APPROVAL | fresh risk re-review fails/reject | RISK_REJECTED | audit reason; no submission |
| CREATED | risk approve + reservation thành công | RISK_APPROVED | persist RiskDecision |
| RISK_APPROVED | transaction commit | SUBMISSION_QUEUED | persist order, submission queue và outbox cùng transaction |
| SUBMISSION_QUEUED | execution leader claim | SUBMITTING | persist SubmissionAttempt/request hash trước HTTP |
| SUBMITTING | venue ack | OPEN | persist venue order ID, event |
| SUBMITTING | fill-before-ack | PARTIALLY_FILLED hoặc FILLED | persist fill/ledger first; late ack chỉ enrich venue metadata |
| SUBMITTING | business rejection | REJECTED | release reservation theo policy |
| SUBMITTING | timeout/disconnect/outcome unknown | UNKNOWN | không retry blind |
| OPEN | partial fill | PARTIALLY_FILLED | persist immutable fill + ledger event |
| OPEN/PARTIALLY_FILLED | full fill | FILLED | final ledger/projection |
| OPEN/PARTIALLY_FILLED | cancel requested | CANCEL_REQUESTED | persist cancel attempt |
| CANCEL_REQUESTED | venue confirms cancel | CANCELLED | release remaining reservation |
| OPEN/PARTIALLY_FILLED/CANCEL_REQUESTED | venue expiry | EXPIRED | release remaining reservation |
| OPEN/PARTIALLY_FILLED/CANCEL_REQUESTED | cancel timeout/outcome unknown | UNKNOWN | pending_operation=CANCEL; reconcile, no blind retry |
| CANCELLED | late fill with venue evidence | CANCELLED nếu cumulative quantity chưa đủ; FILLED nếu đã đủ | append terminal_correction; retain terminal_reason=CANCELLED khi chưa filled |
| EXPIRED | late fill with venue evidence | EXPIRED nếu cumulative quantity chưa đủ; FILLED nếu đã đủ | append terminal_correction; retain terminal_reason=EXPIRED khi chưa filled |
| UNKNOWN | reconciliation started | RECONCILING | block conflicting intent |
| RECONCILING | venue evidence found | OPEN/PARTIALLY_FILLED/FILLED/CANCELLED/REJECTED/EXPIRED | persist evidence and canonical state |
| RECONCILING | SLA elapsed, evidence insufficient | LOST | critical incident + manual handling |
| LOST | late venue evidence proves a terminal outcome | FILLED/CANCELLED/EXPIRED/REJECTED as proven | append approved terminal_correction; retain immutable LOST incident/evidence history |
| LOST | late venue evidence reports open/partial state | LOST | create EXTERNAL reconciliation case, block exposure and resolve/cancel through auditable external-order procedure; never reopen this aggregate to a non-terminal state |

- Terminal states là RISK_REJECTED, REJECTED, CANCELLED, EXPIRED, FILLED và LOST.
- Terminal state không được quay về non-terminal state.
- `executed_quantity` luôn được derive từ immutable fills. Partial late fill không được đổi terminal reason CANCELLED thành EXPIRED hoặc ngược lại; chỉ cumulative quantity đầy đủ mới cho phép terminal correction sang FILLED.
- Fill immutable; duplicate fill không được book lần hai.
- Timeout sau submit không có nghĩa order thất bại.
- Lệnh có ở venue nhưng không có order nội bộ mang classification EXTERNAL và bắt buộc mở reconciliation case.
- Direct venue replace không thuộc MVP. Replace được biểu diễn bằng CancelIntent rồi một OrderIntent mới với ClientOrderId mới. Adapter capability replace chỉ được bật qua ADR/state-machine v2.

### 5.6 RiskDecision

RiskDecision phải chứa:

- APPROVE, REJECT hoặc REQUIRE_MANUAL_APPROVAL;
- approved quantity;
- policy ID/version;
- portfolio/reference/market snapshot version;
- reservation ID nếu có;
- lý do machine-readable;
- input hash, decision time và expiry.

### 5.7 Event envelope

Mọi integration event dùng envelope có version:

~~~json
{
  "id": "uuidv7",
  "type": "execution.order_acknowledged.v1",
  "schema_version": 1,
  "source": "execution",
  "occurred_at": "2026-07-31T00:00:00Z",
  "correlation_id": "…",
  "causation_id": "…",
  "trace_id": "…",
  "subject_id": "canonical-order-id",
  "data": {}
}
~~~

Event tên ở thì quá khứ. Command tên động từ. Query tên Get/List/Search.

### 5.8 Compatibility

- Thêm optional field có default là compatible.
- Không xóa/đổi nghĩa field đã public trong cùng major version.
- Khi bắt buộc đổi, tạo v2 + upcaster/adapter trong thời gian migration.
- Consumer không được crash chỉ vì gặp event version chưa hỗ trợ; phải DLQ/alert theo policy.

---

## 6. Mode, môi trường, cấu hình và release

### 6.1 Run mode và execution target

Run mode, execution target, account class và credential class là bốn field riêng trong deployment manifest. Không dùng một field mơ hồ kiểu paper để chỉ cả simulator và testnet.

Credential classes được đóng nghĩa:

| Credential class | Quyền |
|---|---|
| NONE | không có venue credential |
| TESTNET_READ_ONLY | chỉ đọc testnet |
| TESTNET_TRADE_ONLY | đọc/giao dịch testnet, không withdrawal |
| LIVE_READ_ONLY | chỉ đọc live account/market data, không trade/withdraw |
| LIVE_TRADE_ONLY | đọc/giao dịch live account, không withdrawal |

Account class được đóng nghĩa và không suy ra từ tên environment:

| Account class | Nghĩa |
|---|---|
| SIMULATED | không có venue account; simulator sở hữu balance/position |
| TESTNET | account do venue testnet cung cấp |
| LIVE | account live ở venue, dù credential hiện thời chỉ read-only |

| Run mode | Data source | Execution target | Credential class được phép | Mục đích |
|---|---|---|---|---|
| BACKTEST | historical deterministic | internal simulator | NONE | nghiên cứu |
| REPLAY | recorded event stream | internal simulator | NONE | debug/tái hiện |
| SHADOW | live/replay | disabled | NONE, TESTNET_READ_ONLY hoặc LIVE_READ_ONLY | so sánh decision |
| PAPER_SIMULATOR | live/replay | internal simulator | NONE hoặc LIVE_READ_ONLY | kiểm thử toàn luồng không gửi lệnh |
| TESTNET | venue testnet | venue testnet | TESTNET_TRADE_ONLY | kiểm thử venue thật |
| CANARY | venue live | venue live | LIVE_TRADE_ONLY | xác minh vốn/risk cực nhỏ |
| FULL_LIVE | venue live | venue live | LIVE_TRADE_ONLY | ngoài phạm vi tài liệu này, cần ADR/gate mới |

- PAPER_SIMULATOR không gửi request đặt lệnh đến venue.
- TESTNET gửi request đến môi trường test của venue; nó không là bằng chứng rằng live sẽ giống hệt.
- TESTNET_READ_ONLY chỉ được dùng ở SHADOW/discovery, không có execution permission và không được nâng thành TESTNET_TRADE_ONLY khi process đang chạy.
- LIVE_READ_ONLY chỉ được inject vào SHADOW/PAPER_SIMULATOR trên host/environment đã được owner duyệt, bị network allowlist và không có execution permission.
- CANARY và FULL_LIVE chỉ được dùng khi manifest nêu rõ account_class=LIVE và credential_class=LIVE_TRADE_ONLY.
- Không đổi bất kỳ field nào trong bốn field trên khi process đang chạy.

Config schema phải từ chối mọi tuple không nằm trong ma trận này:

| Run mode | Account class | Credential class | Execution target |
|---|---|---|---|
| BACKTEST / REPLAY | SIMULATED | NONE | internal simulator |
| SHADOW | SIMULATED | NONE | disabled |
| SHADOW | TESTNET | TESTNET_READ_ONLY | disabled |
| SHADOW | LIVE | LIVE_READ_ONLY | disabled |
| PAPER_SIMULATOR | SIMULATED | NONE | internal simulator |
| PAPER_SIMULATOR | LIVE | LIVE_READ_ONLY | internal simulator |
| TESTNET | TESTNET | TESTNET_TRADE_ONLY | venue testnet |
| CANARY / FULL_LIVE | LIVE | LIVE_TRADE_ONLY | venue live |

`venue_id`, `account_id`, environment endpoint class và capability profile phải khớp tuple trên. Ngoại lệ capability hoặc account model chỉ được thêm qua ADR 0009 và schema version mới.

### 6.2 Ma trận môi trường và topology

| Environment | Host/network | Database/account | Process cho phép | Credential/command |
|---|---|---|---|---|
| local | máy phát triển, bind local | DB dev riêng | CLI, test, simulator | không venue live |
| CI | sandbox ephemeral | DB test ephemeral | test/migration/contract | không secret thật |
| paper | host dev hoặc non-production | DB paper riêng | trading-node, data worker, control API | read-only hoặc không venue credential |
| testnet | isolated non-production host | DB testnet/account testnet riêng | trading-node, reconciliation, control API | testnet read-only cho SHADOW; trade-only chỉ ở run mode TESTNET |
| canary | dedicated monitored host | DB live riêng, sub-account nếu có | production processes tối thiểu | live trade-only, no withdrawal |
| live | chưa được phê duyệt | không dùng trước ADR mới | không áp dụng | không áp dụng |

Không trộn database, endpoint, queue, account hoặc credential giữa environment. Trước khi kết nối bất kỳ venue bên ngoài nào, control plane phải có actor định danh, authorization, immutable audit log và re-auth cho action nguy hiểm.

### 6.3 Invariant bắt buộc

1. LLM không trực tiếp gọi API đặt lệnh.
2. Risk engine deterministic và không gọi LLM.
3. Chỉ execution context mới được submit/cancel order. Direct venue replace không thuộc MVP (§5.5).
4. Không retry submit order khi outcome chưa biết.
5. Không enable strategy trước khi reconciliation hoàn tất.
6. Không mở exposure mới khi balance, position, open order, market data, reference data hoặc lease không đáng tin.
7. Không dùng LIVE_TRADE_ONLY credential ngoài CANARY/FULL_LIVE; LIVE_READ_ONLY chỉ được phép ở SHADOW/PAPER_SIMULATOR theo manifest approved.
8. Không có lệnh canary nếu deployment manifest chưa được owner phê duyệt.
9. Không hard-delete financial/audit history.
10. Không được có bypass im lặng cho risk gate, kill switch, approval hoặc audit.
11. Một request đang bay khi mất lease phải được xem là UNKNOWN; fencing token không chứng minh venue đã từ chối request cũ.

### 6.4 Configuration contract

Config là input được version hóa, validate và hash; secret là reference chứ không phải giá trị trong config.

~~~text
configs/
  base.yaml
  environments/{local,ci,paper,testnet,canary}.yaml
  services/{control-api,trading-node,data-worker}.yaml
  venues/{venue-id}.yaml
  ai/
    provider-catalogs/{catalog-id}.yaml
    endpoint-profiles/{endpoint-profile-id}.yaml
    data-egress-policies/{data-egress-policy-id}.yaml
    usage-policies/{usage-policy-id}.yaml
    policy-profiles/{policy-profile-id}.yaml
  strategies/{strategy-version}.yaml
  risk/{policy-id-version}.yaml
  deployments/{deployment-id}.yaml
~~~

`contracts/config/<kind>.v1.schema.json` là **nguồn schema config duy nhất**. `configs/` chỉ chứa instance/reference config đã validate và không được có bản sao schema, generated schema hay rule validation thứ hai. Nếu cần generated code/cache từ schema, nó phải nằm ở `generated/`, có source link và không được sửa tay.

Precedence hợp lệ:

~~~text
base -> environment -> service -> approved venue/strategy/risk reference
     -> immutable deployment manifest
~~~

- Map merge recursively only when schema declares the map mergeable.
- List không merge/append ngầm; layer sau thay toàn bộ list và effective config phải hiển thị diff.
- Null chỉ hợp lệ cho field schema nullable; null không có nghĩa delete/inherit.
- Unknown key, duplicate semantic key hoặc type coercion tự động là validation failure.
- Environment variable chỉ dùng cho secret injection/ref và bootstrap path được allowlist; không được override business/risk/strategy config.
- Strategy không được override hard risk cap.
- Environment config không được nâng PAPER_SIMULATOR thành TESTNET/CANARY.
- Secret chỉ được tham chiếu qua secret_ref/path; không xuất hiện trong YAML, DB dump, log hoặc UI.
- Config schema có version; unknown field hoặc missing required field là startup failure.
- Mọi effective config được canonicalize, hash và lưu cùng deployment/audit record.
- Config diff cho canary cần Risk Approver phê duyệt; config diff cho credential/topology cần Security/Backup Owner phê duyệt.

Config tối thiểu phải tách:

| Nhóm | Nội dung |
|---|---|
| runtime | environment, run mode, instance ID, timezone |
| venue/account | adapter, endpoint class, account ID, secret_ref, capability profile |
| risk | policy ID/version, caps, freshness, reservation, kill-switch policy |
| strategy | artifact/version, instrument scope, parameter schema |
| data | retention, quality threshold, catalog location |
| ai | provider/model catalog đã duyệt, endpoint/data-egress/usage/policy profile versioned; connection metadata active/candidate opaque, không có raw key hoặc secret_ref public |
| operations | lease, retry, alert, backup, log redaction |
| deployment | manifest hash, approval, image/artifact digest |

Khi CLI đã được tạo, command chuẩn là: uv run ai-auto-trade config validate --manifest path/to/manifest. Trước khi CLI tồn tại, validation phải được chạy qua test/CI tương đương và được ghi trong gate record.

### 6.5 Operational policy values

Các giá trị dưới đây không được để thành câu chữ mơ hồ như fresh hoặc theo chu kỳ. Chúng là field bắt buộc của risk/operations policy:

- market_data_max_age_ms và private_stream_max_age_ms;
- reconciliation_interval_s;
- unknown_order_sla_s;
- lease_ttl_s và heartbeat_interval_s;
- retry_max_attempts, retry_max_elapsed_s và circuit-breaker threshold;
- alert_deadline_s theo severity;
- backup cadence, retention và restore-drill cadence;
- data retention/partition policy;
- daily-loss reset timezone.

Nếu field cần thiết thiếu hoặc không validate, runtime fail closed và gate liên quan không thể pass.

### 6.6 Deployment manifest và release protocol

Mỗi PAPER_SIMULATOR, TESTNET hoặc CANARY deployment lưu immutable manifest:

~~~text
deployment_id
environment + run_mode + execution_target
account_class + credential_class + venue/account scope
code commit + runtime image digest + dependency lock checksum
strategy artifact/version + config hash + risk policy version
dataset/feature/model/prompt version nếu có
capability profile checksum
approved_by + approved_at + approval reason
created_at + rollback_target_manifest_id
~~~

Release protocol:

1. Build artifact từ locked dependency và ghi digest.
2. Chạy CI, migration/replay/contract suite bắt buộc.
3. Generate effective config và manifest; review diff.
4. Lấy approval đúng role.
5. Deploy process nhưng chưa enable strategy.
6. Kiểm tra health, lease, config hash và startup reconciliation.
7. Chỉ enable strategy sau khi các check pass.
8. Rollback dùng manifest đã biết tốt; không sửa nóng manifest hiện tại.

---

## 7. Eventing, persistence và quyền sở hữu dữ liệu

### 7.1 Command, event và query

- **Command** yêu cầu thay đổi state và có thể thất bại. Ví dụ: SubmitOrder, ActivateStrategy.
- **Event** là sự thật immutable đã xảy ra. Ví dụ: OrderAcknowledged, RiskOrderRejected.
- **Query** chỉ đọc state. Ví dụ: GetOrderTimeline, ListOpenOrders.

Không dùng event như command. Không dùng query để thay đổi state.

### 7.2 Delivery semantics

Hệ thống dùng at-least-once delivery, không hứa exactly-once.

1. Trong một PostgreSQL transaction: persist aggregate state, domain event và outbox record.
2. Outbox publisher publish event sau commit.
3. Consumer ghi inbox record với unique key gồm consumer và event_id trước hoặc cùng lúc xử lý.
4. Consumer phải idempotent.
5. Retry có bounded backoff/jitter; event lỗi vào DLQ với payload đã redaction.
6. Internal in-process bus chỉ dispatch event đã commit; nó không thay thế outbox cho worker/process khác.

### 7.3 Ordering và backpressure

- Thứ tự chỉ được đảm bảo theo aggregate/partition key đã xác định, không phải toàn hệ thống.
- Order lifecycle dùng order_id làm partition key.
- Consumer phải xử lý duplicate và event đến sai thứ tự theo transition rule hoặc reconciliation.
- Queue/backlog có metric và ngưỡng alert.
- Không drop event tài chính/audit để giảm tải.

### 7.4 Database ownership và physical conventions

- PostgreSQL 16.x là system of record cho control state, execution state, ledger, audit và outbox/inbox.
- Mỗi environment có PostgreSQL database/credential riêng. Environment không được biểu diễn bằng cột để trộn local, testnet và canary trong cùng database.
- MVP là single tenant/single account scope; mọi record execution, risk, ledger và reconciliation phải mang account_id và venue_id khi áp dụng.
- Mỗi context sở hữu schema/table của nó. Không có ORM relationship, foreign key hoặc direct SQL xuyên context; cross-context dùng immutable ID, contract event hoặc read projection.
- Foreign key chỉ được dùng trong cùng schema/context. Cross-context integrity được kiểm qua application contract/reconciliation.
- Internal ID dùng UUID; timestamp dùng TIMESTAMPTZ UTC; money/price/quantity dùng NUMERIC(38,18); boolean không dùng integer giả.
- JSONB chỉ dùng cho vendor payload, evidence metadata hoặc versioned extension đã hash. Không giấu business state, money hoặc lifecycle state trong JSONB.
- Append-only record gồm fill, order_event, journal_entry, posting, command_event, approval, audit_log, integration_event, outbox/inbox result. Runtime role không có UPDATE/DELETE quyền trên các bảng này.

### 7.5 Data dictionary và DDL gate

AI không được tạo migration đầu tiên, bảng mới hoặc index mới nếu chưa có data dictionary entry và task card được duyệt.

Mỗi table entry trong docs/backend/data/data-dictionary.md phải có:

| Thuộc tính | Bắt buộc |
|---|---|
| Schema/context owner và mục đích | ai được viết, vì sao bảng tồn tại |
| Primary key và business key | UUIDv7 và uniqueness business |
| Column contract | tên, PostgreSQL type, nullability, default, semantics |
| Integrity | enum, CHECK, UNIQUE, FK cùng schema, aggregate version |
| Access | writer role, reader roles, query/index pattern |
| Time/data | timestamp semantics, classification, retention/archive |
| Change impact | requirement/ADR, migration/backfill/rollback plan |
| Tests | fixture, constraint/integration/property test path |

Alembic migration đã apply là physical schema source of truth. Data dictionary/OpenAPI/schema phải được cập nhật trong cùng approved change; nếu drift, deployment BLOCKED.

### 7.6 Database inventory v1

| Schema owner | Bảng v1 bắt buộc | Ghi chú |
|---|---|---|
| reference | venues, accounts, assets, instruments, instrument_rule_versions, capability_profiles | rule/filter phải có valid/effective range, không overwrite history |
| strategy | definitions, versions, instances, checkpoints | checkpoint lưu watermark/offset/schema hash |
| risk | policies, decisions, reservations, pending_approvals, limit_state | policy/version immutable sau activation |
| execution | orders, order_events, submission_attempts, fills, reconciliation_cases, reconciliation_evidence | order/fill lifecycle và evidence |
| portfolio_ledger | chart_of_accounts, journal_entries, postings, balance_projections, position_projections, projection_checkpoints | journal/posting là append-only accounting truth |
| market_data | catalog_partitions, ingestion_checkpoints, feed_health, data_quality_issues | raw tick lớn nằm ở Parquet, DB chỉ metadata/control |
| research | dataset_versions, feature_definitions, backtest_runs, evaluation_reports | research không query trực tiếp OLTP write model |
| operations | deployments, runtime_leases, kill_switches, commands, command_events, approvals, audit_log, incidents, ai_provider_connections, ai_connection_events | connection chỉ lưu metadata/internal active-candidate binding opaque; không lưu raw API key hoặc secret blob |
| platform | outbox, outbox_delivery_state, inbox, dead_letters, idempotency_keys | platform là bounded context infrastructure, không phải context ẩn |
| ai_memory | memory_items, retrieval_runs, inference_runs, proposals, post_mortems | chỉ Phase 6; không tạo sớm; raw prompt/response theo policy riêng |

#### Ownership của control command và approval

- `operations.commands` là source of truth mutable duy nhất cho lifecycle command ở §11.2. Nó chứa tối thiểu command_id, type/schema_version, actor_id, subject context/id, idempotency key/hash, status, requested_at, completed_at, correlation_id và result/error reference.
- `operations.command_events` là lịch sử append-only của mọi transition command, có `UNIQUE(command_id, sequence)`; terminal result không bị overwrite.
- `operations.approvals` là evidence append-only, domain-neutral cho action approve/reject. Nó chứa approval_id, actor/role, subject_context/subject_id, decision, reason, re-auth evidence, occurred_at và command_id khi có.
- `risk.pending_approvals` là source of truth cho trạng thái chờ approval của risk intent (expiry, required role, snapshot/policy hash). Chỉ risk application được đổi trạng thái này sau khi nhận command hợp lệ; `operations.approvals` không được tự mutate risk state. Liên kết cross-context chỉ bằng immutable UUID/event, không foreign key xuyên schema.
- Control API chỉ tạo command/approval evidence theo authorization; owner application handler thực hiện transition rồi persist outbox/audit trong transaction phù hợp. Mọi callback/retry phải dựa vào command_id/idempotency contract, không dùng UI state.

Các bảng contract tối thiểu phải có thêm các key/constraint sau:

~~~text
execution.orders:
  UNIQUE (venue_id, account_id, client_order_id)
  UNIQUE (venue_id, account_id, venue_order_id) WHERE venue_order_id IS NOT NULL
  CHECK quantity > 0
  CHECK aggregate_version >= 0

execution.fills:
  UNIQUE (venue_id, account_id, venue_fill_id) WHERE venue_fill_id IS NOT NULL
  fallback UNIQUE (venue_id, account_id, source_event_id/fingerprint)
  CHECK quantity > 0

execution.order_events:
  UNIQUE (order_id, sequence)

execution.submission_attempts:
  UNIQUE (order_id, attempt_no)
  CHECK attempt_no > 0

risk.reservations:
  CHECK reserved_amount >= 0
  UNIQUE (order_intent_id, reservation_kind)

platform.inbox:
  UNIQUE (consumer_id, event_id)

platform.idempotency_keys:
  UNIQUE (actor_id, route_scope, idempotency_key)

operations.command_events:
  UNIQUE (command_id, sequence)

portfolio_ledger.postings:
  UNIQUE (journal_entry_id, line_no)
~~~

Canonical request hash không được UNIQUE toàn cục. Nó chỉ phát hiện payload thay đổi trong idempotency scope và cung cấp audit evidence.

### 7.7 Transaction, concurrency và cross-context orchestration

Context vẫn sở hữu table của mình. Ngoại lệ duy nhất là application workflow whitelist dưới đây, dùng public owner repository/port chứ không direct SQL/ORM xuyên context:

| Unit of Work | Table owner được điều phối atomically | Mục đích |
|---|---|---|
| TradingSubmissionUnitOfWork | risk.decisions/reservations, execution.orders/submission_attempts, platform.outbox | approve, reserve và queue submission |
| FillLedgerUnitOfWork | execution.fills/order_events, portfolio_ledger.journal_entries/postings/projections, platform.outbox | book fill chính xác một lần |
| ReconciliationResolutionUnitOfWork | execution.reconciliation_cases/evidence, risk.reservations, portfolio_ledger adjustment qua owner command, platform.outbox | giải quyết mismatch có audit |

Quy tắc bắt buộc:

1. Pre-submit transaction chạy SERIALIZABLE, chỉ thao tác PostgreSQL, không gọi venue/network.
2. Serialization/deadlock failure được retry tối đa theo operations policy và phải chạy lại risk evaluation; không retry external submit.
3. Lock order cố định: risk limit/reservation -> execution order -> platform outbox.
4. Queue/outbox publisher claim bằng SELECT FOR UPDATE SKIP LOCKED, lock timeout và batch size theo policy/metric.
5. Aggregate mutable có aggregate_version; update phải optimistic-concurrency compare-and-swap.
6. Venue HTTP/WebSocket call luôn sau commit. Nếu outcome không rõ, state là UNKNOWN và flow chuyển sang reconciliation.
7. Không dùng distributed transaction, 2PC hoặc in-memory mutex làm safety boundary.

### 7.8 Accounting và audit enforcement

Accounting policy phải được ADR 0011 chốt **trước Phase 1**, gồm chart of accounts, debit/credit hoặc commodity convention, asset scale, fee/rebate/transfer/adjustment, cost basis, valuation source/time, rounding và locked/reserved balance.

- Mọi journal entry có source_type/source_id/source_event_id, accounting_policy_version, effective_at và recorded_at.
- Write path và database phải kiểm tính cân bằng entry theo asset. Dùng deferred constraint trigger hoặc stored write procedure đã được ADR chấp thuận; property test chỉ là lớp kiểm tra bổ sung.
- Projection là derived state; không là accounting source of truth.
- audit_log ghi actor/machine identity, action, reason, subject, command/idempotency/correlation ID, before/after hash, request/result hash, recorded_at.
- DB grants và append-only trigger phải chặn UPDATE/DELETE vào financial/audit/event history. Retention chỉ archive immutable; không hard delete.

### 7.9 Database roles, access và index contract

| Database role | Quyền |
|---|---|
| db_migrator | DDL/migration duy nhất; không dùng làm runtime user |
| db_control_api | operations/config read-write qua application scope; projection read |
| db_trading_node | risk/execution/ledger write cần thiết; không DDL, không audit delete |
| db_data_worker | market_data/reference write; không execution/ledger |
| db_research_worker | catalog/research write; read snapshot/projection, không OLTP write |
| db_ai_worker | sanitized projection read, ai_memory write; không execution/risk/ledger |

Dashboard không có database role ở production; nó chỉ gọi Control API. Index/query budget phải được ghi trong data dictionary cho ít nhất: open order theo account/venue/state, order timeline, fill dedupe, active reconciliation, unpublished outbox, inbox dedupe, journal/posting theo source/account, audit theo actor/correlation và projection watermark. Query không có index/access pattern được phê duyệt không vào hot path.

### 7.10 Migration, backfill và schema evolution

Dùng expand -> migrate -> contract:

1. Thêm field/table/index tương thích ngược.
2. Deploy code đọc được old/new.
3. Backfill có checkpoint, rate limit, lock/lag metric và resume token.
4. Chuyển reader sang new representation.
5. Chỉ drop/rename ở release sau khi xác minh không còn reader cũ.

Mỗi migration có owner, requirement/ADR link, risk note, forward-fix plan, rollback/restore assessment, upgrade test từ snapshot cũ và expected execution time. Financial/audit schema không tự downgrade phá dữ liệu; recovery mặc định là forward-fix hoặc restore đã diễn tập.

### 7.11 Data lifecycle, partition và retention

ADR 0013 và retention matrix phải được chốt **trước Phase 2**, không chờ Phase 3 vì Phase 2 đã ghi Parquet/dataset.

| Data class | Hot store | Archive/retention rule | Owner |
|---|---|---|---|
| Bronze raw market data | Parquet catalog | append-only, checksum/quarantine, retention theo policy | market_data |
| Silver/gold dataset | Parquet + manifest | reproducible từ input/transform version | market_data/research |
| Order/fill/journal/audit | PostgreSQL | archive immutable, không hard delete | execution/ledger/operations |
| Outbox/inbox/DLQ | PostgreSQL | purge chỉ sau dedupe/replay window được duyệt | platform |
| Logs/traces | observability store | redaction, retention theo severity/data class | operations |
| Evidence/config/manifest | encrypted artifact store | đủ cho replay/audit/gate | operations |

Parquet writer phải có temporary path + checksum + commit marker; catalog chỉ publish partition sau khi write/validation hoàn tất. Late/revised data tạo partition/version mới, không sửa âm thầm dữ liệu bronze. Schema evolution, compaction, partition size, quarantine và evidence URI là field bắt buộc của catalog metadata.

### 7.12 Backup, restore và consistency set

- Dev: backup/restore test trong mỗi milestone quan trọng.
- Canary: daily base backup, WAL/PITR, encrypted offsite copy, retention policy và restore drill.
- Consistency set gồm PostgreSQL + WAL, Parquet/catalog manifests, evidence artifact, config/deployment manifest, ADR/gate record cần cho replay/audit.
- Restore drill phải xác minh journal balance, projection rebuild, outbox/inbox behavior, catalog checksum rồi chạy reconciliation trước khi enable strategy.
- Mục tiêu mặc định trước canary: RPO không quá 15 phút, RTO không quá 60 phút.
- Backup chưa từng restore thành công được coi là chưa có backup.

### 7.13 Public contract registry

Public contract dùng OpenAPI 3.1 cho HTTP và JSON Schema 2020-12 cho command/event/config:

~~~text
contracts/
  api/openapi.yaml
  commands/<context>/<command>.v1.schema.json
  events/<context>/<event>.v1.schema.json
  config/<kind>.v1.schema.json
  errors/error-catalog.md
  fixtures/
docs/backend/contracts/contract-registry.md
~~~

Mỗi registry entry phải có Contract ID/version, owner context, canonical path, producer, consumer, partition key, sensitive-data classification, compatibility rule, fixture/test path, migration/retirement plan.

Không implement HTTP endpoint trước khi route tồn tại trong OpenAPI. Không publish/consume public command/event trước khi schema, fixture và compatibility test tồn tại. CI phải validate schema, fixture và backward compatibility; documentation khác schema/code phải được cập nhật trong cùng task.

---

## 8. Trading core: strategy, risk, OMS, ledger và reconciliation

### 8.1 Strategy SDK

Strategy nhận canonical events/state và chỉ trả domain action:

~~~text
on_start(context) -> actions
on_market_event(event, state, context) -> actions
on_order_event(event, state, context) -> actions
snapshot() -> strategy_snapshot
~~~

Action hợp lệ gồm ProposeOrderIntent, CancelIntent, UpdateTarget, EmitSignal, ScheduleTimer và NoAction.

Strategy không được:

- import venue SDK;
- đọc database/file/env/network;
- dùng current time/random global;
- tự tính balance từ dữ liệu không thuộc context;
- bypass risk hoặc execution.

Mỗi strategy version phải có version, code SHA, artifact hash, dependency lock hash, config schema, feature contract và metadata người tạo.

### 8.2 Strategy checkpoint và recovery

Strategy checkpoint không chỉ được tạo lúc shutdown sạch. Checkpoint phải chứa:

- strategy instance/version và deployment manifest ID;
- state blob có schema version và checksum;
- last processed event ID/offset, market watermark và timestamp;
- config/feature contract hash;
- trạng thái restore compatibility.

Checkpoint được persist theo boundary đã định nghĩa trong strategy runtime. Khi restart, runtime phải validate version/contract, restore checkpoint rồi replay event từ offset. Nếu checkpoint không tương thích hoặc thiếu event cần thiết, strategy không được enable cho đến khi operator xử lý.

### 8.3 Backtest, paper và live parity

Cùng strategy code chạy trên:

| Abstraction | Backtest/replay | Paper simulator | Testnet/canary |
|---|---|---|---|
| Clock | simulated | live | live |
| DataFeed | historical/recorded | live/replay | live |
| Execution | simulator | simulator | venue adapter |

Parity không chỉ là interface. Simulator phải version hóa fee, slippage, latency, partial fill và rejection model. Testnet/canary data phải được lưu để so sánh assumption với thực tế.

### 8.4 Risk engine

Risk là synchronous gate trước execution. Input gồm immutable intent, policy version, portfolio snapshot, market/reference snapshot, reservation state, runtime health và injected time.

Pre-trade checks tối thiểu:

- strategy, venue, account, instrument được enable;
- kill switch inactive;
- deployment/strategy/model được phê duyệt;
- market/reference/portfolio data fresh;
- tick size, lot size, min/max quantity và min notional hợp lệ;
- price sanity/deviation;
- available và reserved balance;
- max order notional;
- max position, gross/net exposure, concentration;
- leverage/margin nếu capability được bật sau này;
- max open order và rate limit;
- daily loss, drawdown, order intent expiry;
- duplicate/conflicting intent;
- leadership lease hợp lệ.

Nếu thiếu dữ liệu hoặc trạng thái không chắc chắn: reject/fail closed. Chỉ reduce-only emergency policy riêng mới có thể giảm exposure trong lúc degraded.

Risk policy là immutable, versioned artifact và phải định nghĩa:

- policy currency/asset scale và rounding rule;
- price source/worst-case price cho market order;
- fee/slippage buffer và cách reserve BUY/SELL;
- max order notional, position, gross/net exposure, open order, concentration và rate;
- daily loss/drawdown, timezone reset và valuation source;
- market/reference/private-account freshness threshold;
- manual approval condition, expiry và kill-switch behavior.

RiskDecision và reservation phải dùng portfolio/reference snapshot version. Cùng transaction/optimistic concurrency phải phát hiện snapshot đã stale trước commit; không được approve dựa trên snapshot cũ rồi submit sau khi exposure đã thay đổi.

REQUIRE_MANUAL_APPROVAL chỉ tạo pending approval. Khi người có quyền approve, intent phải chạy lại toàn bộ risk check với snapshot mới; approval không phải bypass.

### 8.5 Reservation

Risk phải reserve balance/exposure trước submit và release reservation khi:

- order bị reject/cancel/expired;
- fill làm reservation chuyển thành exposure thực;
- reconciliation kết luận order không tồn tại.

Reservation stale phải alert và được reconcile; không silently clear.

### 8.6 Durable submit protocol

Không giữ PostgreSQL transaction mở trong lúc gọi venue HTTP/WebSocket. Flow submission bắt buộc:

1. Validate intent, chạy risk, tạo reservation, order state SUBMISSION_QUEUED, SubmissionAttempt đầu và outbox record trong **một** transaction.
2. Chỉ execution leader có lease hợp lệ mới atomically claim submission queue item.
3. Persist attempt ID, client_order_id, canonical request hash và thời điểm trước request ra venue.
4. Gửi đúng một attempt; không submit lại chỉ vì không nhận response.
5. Persist ack/reject/fill khi có evidence. Nếu outcome không chắc chắn, chuyển UNKNOWN và reconcile.

Fencing token chỉ bảo vệ claim/write nội bộ; nó không thể fence API của venue. Mất lease phải dừng claim lệnh mới. Request đã bay có thể đã đến venue, nên chỉ client_order_id duy nhất và reconciliation mới bảo vệ khỏi duplicate.

### 8.7 Unknown order và recovery

Khi timeout/mất kết nối sau submit:

1. Chuyển order sang UNKNOWN.
2. Không submit lại.
3. Query theo client_order_id nếu venue hỗ trợ.
4. Query order history, open orders và recent fills.
5. Nếu thấy, gắn venue order ID và tiếp tục lifecycle.
6. Nếu chưa kết luận, giữ RECONCILING và chặn intent xung đột.
7. Quá SLA thì chuyển LOST, alert critical và mở reconciliation case cần operator xử lý.
8. Evidence đến muộn sau LOST xử lý theo terminal-correction/EXTERNAL procedure ở §5.5; không submit lại order cũ.

Venue port bắt buộc phải hỗ trợ đủ query/recovery để thực hiện flow này, hoặc capability phải bị từ chối cho testnet/canary.

### 8.8 Reconciliation

Reconcile ít nhất:

- startup;
- theo chu kỳ đã cấu hình khi paper/canary/live;
- sau disconnect/private stream gap;
- khi có unknown order;
- theo yêu cầu operator.

Đối soát balance, position, open order, recent fill, fee và trạng thái order. Mismatch tạo case có evidence và audit. Không overwrite local history để “khớp” sàn.

Reconciliation case state:

~~~text
CLEAN -> DETECTED -> INVESTIGATING -> BLOCKED -> RESOLVED
                                         -> APPROVED_ADJUSTMENT
~~~

- Case lưu external snapshot, internal snapshot, time window, tolerance theo asset, adapter version và actor.
- Lệnh/transfer thủ công ở venue phải được classify rõ; không tự coi chúng là lỗi hay tự xóa.
- BLOCKED chặn exposure mới trong scope ảnh hưởng.
- APPROVED_ADJUSTMENT chỉ khi không thể reconstruct original event, có evidence và approval. Lịch sử gốc không bị sửa.

### 8.9 Startup, lease và shutdown

Startup:

~~~text
BOOTING -> LEASE_ACQUIRED -> CONFIG_VALIDATED -> LOCAL_STATE_LOADED
-> VENUE_CONNECTED -> RECONCILING -> MARKET_HEALTH_CHECK
-> READY -> STRATEGIES_ENABLED
~~~

- Mỗi venue/account chỉ có một execution leader.
- Lease có TTL, heartbeat và fencing token tăng đơn điệu.
- Mất lease phải dừng claim/gửi lệnh mới; request đang bay được đánh dấu UNKNOWN khi chưa có outcome.
- Shutdown chặn intent mới, drain theo timeout, flush outbox/checkpoint, persist snapshot và audit event.
- Không mặc định cancel tất cả open order; hành vi đó là policy có cấu hình.

### 8.10 Kill switch

Hierarchy:

~~~text
GLOBAL
  -> VENUE
      -> ACCOUNT
          -> STRATEGY
              -> INSTRUMENT
~~~

Kill switch scope cha vô hiệu scope con. Kích hoạt phải nhanh, idempotent, audit được và chặn exposure mới.

Action policy mặc định:

- FREEZE: cấm lệnh làm tăng exposure; đây là default cho MVP.
- CANCEL_OPEN_ORDERS: chỉ áp dụng nếu policy scope đã bật và venue capability hỗ trợ.
- FLATTEN: không tự động trong MVP; chỉ có ADR/risk policy riêng mới được phép.

Mỗi runtime node phải ghi applied/failed status. Release cần explicit approval, re-auth, reconciliation sạch và health check; không chỉ là bấm một nút.

### 8.11 Double-entry ledger

Ledger là accounting truth nội bộ:

~~~text
immutable journal entries -> postings -> balance/position/PnL projections
~~~

Mọi fill, fee, funding, interest, rebate, transfer hoặc verified adjustment đều tạo journal entry cân bằng theo asset/quy tắc định giá đã công bố.

- Projection có thể rebuild.
- Duplicate fill không được double-book.
- Adjustment chỉ khi không thể phục hồi original event, có evidence và approval.
- Sàn là external truth cho state tức thời; ledger là internal accounting truth. Hai bên được đối soát, không ghi đè lẫn nhau.

Accounting policy cũng là immutable/versioned artifact. Trước Phase 1 (thống nhất với §7.8 và DOM-004; bản trước ghi "Trước Phase 3" là mâu thuẫn đã được sửa ở v2.2.0), owner phải chốt asset/currency scale, fee asset treatment, cost-basis cho realized PnL, valuation source/timestamp cho unrealized PnL, rounding, locked balance/reservation và xử lý external transfer. Tax engine không thuộc MVP, nhưng hệ thống không được để các quy tắc accounting này ngầm định trong code.

---

## 9. Market data, catalog lịch sử và backtest

### 9.1 Data layers

~~~text
bronze/raw     dữ liệu gần nguyên bản từ venue
silver/clean   normalized, deduplicated, ordered, quality flags
gold/features  feature/dataset point-in-time correct
~~~

Raw tick/order-book lớn không ghi lâu dài vào PostgreSQL OLTP. Lưu Parquet phân vùng:

~~~text
data/catalog/
  venue=example/
    data_type=trades/
      instrument=BTC-USDT/
        date=YYYY-MM-DD/
          part-0001.parquet
~~~

### 9.2 Dataset manifest

Mỗi dataset dùng cho backtest/training phải lưu immutable manifest gồm:

- dataset/version ID và created_at;
- source venue/adapter/schema version;
- time range;
- partition URI và checksum;
- quality report;
- point-in-time rule/available_at column;
- manifest checksum.

### 9.3 Data quality gates

Phải phát hiện và lưu evidence cho:

- duplicate ID/event;
- sequence gap và out-of-order;
- missing partition/checksum mismatch;
- negative quantity/invalid price;
- crossed/invalid book khi áp dụng;
- clock skew;
- candle mismatch với trade aggregation;
- symbol/precision change;
- data staleness.

Bad data không được âm thầm xóa. Gắn quality flag và chặn/giới hạn strategy theo risk policy.

### 9.4 Feed health và gap recovery

Mỗi public/private stream phải duy trì health record gồm:

- last source sequence/trade ID nếu venue cung cấp;
- last_occurred_at, last_received_at, last_processed_at và measured_lag_ms;
- stream connection state, reconnect count và last successful snapshot;
- watermark/backfill range;
- adapter version và capability profile.

Khi phát hiện sequence gap, clock divergence, silent stall hoặc stale feed:

1. Đánh dấu feed UNHEALTHY và publish quality/operations event.
2. Risk chặn exposure mới trong scope bị ảnh hưởng.
3. Reconnect; lấy snapshot rồi đồng bộ delta hoặc backfill lịch sử theo contract venue.
4. Validate sequence, checksum/quality và watermark.
5. Chỉ clear UNHEALTHY khi validation pass; mọi khoảng dữ liệu phải có evidence.

Private order/account stream cũng theo rule này. REST polling fallback không tự chứng minh stream đã sạch; nó là evidence bổ sung cho reconciliation.

### 9.5 Point-in-time correctness

Feature hoặc memory tại time t chỉ được dùng dữ liệu có available_at nhỏ hơn hoặc bằng t.

- Không dùng close candle trước lúc candle đóng.
- Không dùng revised historical data trước khi bản revised tồn tại.
- Lưu observed_at, available_at và validity range khi cần.

### 9.6 Backtest manifest và metrics

Mỗi run phải lưu:

- code commit, strategy/config/risk version;
- dataset/feature version;
- engine, fee, slippage, latency model version;
- seed, time range, created_at;
- metrics và artifact report.

Metrics tối thiểu:

- return, volatility, drawdown/duration;
- fees, slippage, funding, turnover, exposure;
- hit rate, expectancy, profit factor;
- number of trades, tail loss;
- performance theo fold/regime;
- capacity/liquidity assumption.

Không promotion chỉ vì Sharpe hoặc PnL đẹp.

### 9.7 Validation research

Trước bất kỳ promotion nào, strategy/model cần:

- out-of-sample evaluation;
- walk-forward đúng train/test boundaries;
- cost/slippage/latency stress;
- parameter perturbation;
- missing/duplicate/out-of-order data simulation;
- partial fill/rejection/disconnect scenarios;
- fixed golden backtest fixture.

---

## 10. Adapter và tích hợp bên ngoài

### 10.1 Tách port

Không có một ExchangePort quá lớn. Tách ít nhất:

| Port | Trách nhiệm |
|---|---|
| MarketDataPort | fetch/stream public market data, backfill và health |
| ExecutionVenuePort | submit/cancel, query theo venue/client order ID, order history và recent fill; replace chỉ là extension sau ADR/state-machine v2 |
| AccountPort | balance, position, account snapshot |
| ReferenceDataPort | instrument, trading rules, capability |
| NotificationPort | alert/operator notification |
| ClockPort | time nguồn và simulated clock |
| EventBusPort | publish/subscribe abstraction |
| AIInferencePort | structured generation ngoài hot path; không tool execution |
| EmbeddingProviderPort | embedding/retrieval ngoài hot path khi Phase 6 cần |
| AIProviderCatalogPort | capability/provider/model profile đã duyệt; không suy đoán từ tên provider |
| AIConnectionValidationPort | validate connection qua probe tối thiểu, không gửi dữ liệu trading |

### 10.2 Venue capability contract

Mỗi venue adapter phải khai báo:

- supported order type, time-in-force, post-only, reduce-only;
- client order ID/idempotency support;
- cancel semantics và việc direct replace có được hỗ trợ hay bị reject;
- spot/margin/futures support;
- tick/lot/min notional;
- timestamp/sequence guarantees;
- rate limit/batch limit;
- testnet/private stream/REST fallback;
- history lookup window;
- supported account/position model.

Không đoán capability từ tên sàn hay fallback im lặng.

### 10.3 Capability matrix record

Mỗi venue/account profile có một capability matrix versioned trong repository. Matrix không chứa secret và tối thiểu ghi:

| Dimension | Giá trị/giới hạn | Source/effective time | Test evidence | Status |
|---|---|---|---|---|
| Market/instrument | spot, symbol, tick/lot/min notional | venue reference snapshot | fixture/contract test | supported/rejected |
| Order | type, TIF, post-only, reduce-only | venue docs + discovery | adapter test | supported/rejected |
| Recovery | client ID, history window, private stream | venue capability | unknown-order drill | supported/rejected |
| Rate/availability | rate limit, testnet, endpoint class | adapter config | reconnect test | supported/rejected |
| Account | balance/position model, settlement asset | account profile | reconciliation test | supported/rejected |

Không có matrix có test evidence thì adapter chỉ được dùng ở fake/prototype mode, không vào Phase 3 gate.

### 10.4 Adapter contract suite

Một adapter chỉ được dùng cho paper/live sau khi pass:

- instrument mapping và precision rounding;
- capability discovery;
- client ID preservation;
- submit/cancel response mapping; direct replace bị reject rõ ở MVP;
- partial fill, fill-before-ack, duplicate/out-of-order event;
- disconnect ngay sau submit;
- unknown outcome/recovery query;
- recent fill pagination;
- reconnect/backfill, rate limit và auth error redaction.

### 10.5 CCXT và venue native SDK

- CCXT MAY dùng cho prototype, data collection, read-only discovery và research.
- Live execution ưu tiên venue-native/Nautilus adapter đủ contract.
- Core không phụ thuộc unified model của CCXT.

### 10.6 AI đa provider và BYOK (Bring Your Own Key)

AI là optional và chỉ bắt đầu sau paper/canary core ổn định. **OpenAI không phải provider bắt buộc hay default.** Người dùng có thể dùng API key của mình với provider/model và `AIPolicyProfile` trong catalog đã được phê duyệt, ví dụ provider cloud, gateway tương thích hoặc gateway private. BYOK v1 chỉ hỗ trợ profile `API_KEY`; provider dùng workload identity/OAuth cần credential-flow/ADR riêng, không được nhận API key theo đường BYOK này. “Đa provider” nghĩa là thêm adapter/capability profile được review; không có nghĩa UI được nhập URL, provider, model, endpoint hoặc policy ID tùy ý.

`AIProviderCatalog`, endpoint profile, data-egress policy, usage/budget policy và `AIPolicyProfile` là artifact versioned, immutable khi `ACTIVE`; thay adapter artifact digest, provider/model terms, hostname/SNI/route, retention/residency, egress projection, budget hoặc retry/fallback phải tạo version mới, capability/security review và evidence mới. Khi provider/model drift/deprecate/retire, connection bị revalidate, suspend hoặc expire theo policy; không “continue silently” trên capability chưa pin.

Mỗi `AIProviderConnection` có owner scope, provider/model profile, policy-profile đã resolve, status/revision và binding opaque. Metadata nội bộ tách `active_binding` và `candidate_binding`: `PENDING_SECRET` chưa có binding, candidate chỉ dùng validation/rotation, và chỉ `active_binding` mới được inference. Public API/UI/event không trả binding nào; fixture chỉ có thể dùng UUID opaque tổng hợp để test schema, không có mapping/reference đến secret provider. Raw API key chỉ đi qua secret-enrollment write-only, một lần, qua transport bảo vệ; nó không được ghi vào PostgreSQL, YAML, deployment manifest, browser storage, command/event/audit payload, log, trace, fixture, backup hay response. Database/API chỉ dùng ID/reference opaque; không role nào, kể cả owner, được đọc lại key.

Lifecycle chuẩn:

~~~text
DRAFT -> PENDING_SECRET -> PENDING_VALIDATION -> ACTIVE
         |                    |                  |
         |                    -> VALIDATION_FAILED -> PENDING_SECRET (explicit retry)
ACTIVE -> ROTATION_PENDING_SECRET -> ROTATION_PENDING_VALIDATION -> ACTIVE
                         |                    (candidate failure: discard candidate, remain ACTIVE)
any non-terminal state -> SUSPENDED | EXPIRED | REVOKED
(SUSPENDED, EXPIRED and REVOKED are terminal in BYOK v1; recovery requires a new,
 separately reviewed connection lifecycle, never an implicit resume of this connection.)
~~~

Rotation bắt đầu bằng command durable không chứa key, tạo candidate binding/revision qua secret ingress, validate độc lập rồi chuyển active atomically; active binding cũ vẫn phục vụ AI trong rotation states. Candidate fail bị hủy và active binding cũ giữ nguyên. Revoke/disable chặn issuance/resolution binding mới ngay; worker dùng lease ngắn theo owner/connection/revision/job, re-check state/revision ngay trước outbound call, zeroize sau call và bỏ output của request bị revoke in-flight. Disconnect chỉ ngừng sử dụng key trong platform; upstream revoke chỉ được khẳng định khi provider capability/procedure chứng minh.

Một terminal connection có thể giữ opaque binding ID chỉ để retention/audit, nhưng binding đó không còn eligible hoặc resolvable cho inference. BYOK v1 không có API “unsuspend/reactivate” trên cùng `connection_id`; user chỉ có thể tạo một lifecycle mới có review đầy đủ.

Ai-worker:

- chỉ đọc sanitized projection/query API theo data-egress policy;
- chỉ ghi ai_proposal, memory item hoặc post-mortem;
- resolve credential binding just-in-time cho đúng connection/job, không nhận trade key hoặc inject toàn bộ user key vào environment;
- outbound chỉ qua approved endpoint profile và egress gateway: hostname/SNI allowlist, TLS validation, redirect deny, DNS resolution tại gateway và deny private/link-local address trừ private route đã approve;
- không có execution write permission, risk/config/deployment promotion hoặc tool/file/network/SQL capability ngoài adapter allowlist;
- không ở hot path;
- kiểm provider/model/adapter artifact/catalog capability, owner scope, policy profile, egress policy, quota/budget reservation, timeout, rate limit và circuit breaker trước request.

LLM được phép phân tích, tóm tắt, tìm memory, tạo hypothesis và proposal. LLM không được place order, change risk limit, deploy live, disable audit, change credential hoặc withdraw. Tool/function calling mặc định disabled; không có direct LLM -> execution/venue path.

Output phải qua structured schema validation. Prompt injection, provider response và memory là untrusted data, không phải instruction. Raw prompt/response không vào telemetry mặc định; audit lưu metadata/hash, provider/model/catalog/adapter artifact/prompt-policy version, timing, usage/cost và normalized status theo retention policy. Free-text `reason`/note/audit input phải bị secret-like-input detection/reject/redact trước persistence; không ai được dán API key vào reason để “giải thích” action.

BYOK v1 có fallback `DISABLED`: không có silent fallback sang provider/model/key khác. Khi AI provider timeout/outage/invalid output/budget exhausted/revoked key, capability AI fail closed hoặc bị disable; trading/risk/OMS/ledger vẫn hoạt động. Retry/fallback chỉ có thể xuất hiện ở contract/profile tương lai đã approve, cùng owner scope, egress classification/capability tương đương và provider biết request chưa rời hệ thống hoặc hỗ trợ idempotency.

### 10.7 Memory contract

Memory là optional. Khi được bật, phân tách:

| Loại | Mục đích | Quy tắc |
|---|---|---|
| Working | context của một job hiện tại | có TTL, không là source of truth |
| Episodic | trade/incident/backtest cụ thể | phải có provenance/evidence |
| Semantic | lesson tổng hợp | có confidence, review/supersede status |
| Procedural | quy trình đã duyệt | cần human approval trước ảnh hưởng vận hành |

Memory item tối thiểu phải có ID, type, content hash, source type/ID, observed_at, available_at, validity range, confidence, scope strategy/instrument, review status, creator/model/prompt version và provenance.

Trong replay/backtest tại time t, retrieval chỉ được trả item có available_at nhỏ hơn hoặc bằng t và valid tại t. Không tự biến raw LLM output hoặc external text thành approved procedural memory. Retrieval phải trả provenance/confidence; content có instruction độc hại được xử lý như data.

### 10.8 Candidate và controlled learning

Candidate có thể đến từ human-authored strategy, parameter optimization, supervised model hoặc LLM hypothesis. Nguồn không thay đổi tiêu chuẩn an toàn.

~~~text
candidate
  -> unit/contract/security validation
  -> backtest
  -> out-of-sample/walk-forward
  -> stress
  -> shadow
  -> paper
  -> canary
  -> explicit owner approval
~~~

- Candidate registry lưu code/data/config/model/prompt/risk lineage và rollback target.
- Không tự sửa code live, risk limit, deployment manifest hoặc strategy đang chạy.
- LLM-generated code chạy trong sandbox, qua review/test như mọi code khác.
- Không có auto-promotion từ PnL hoặc status DB.

---

## 11. Control plane, API, UI và phân quyền

### 11.1 Control plane

Control plane chịu trách nhiệm:

- config/reference/strategy/risk/deployment registry;
- health/readiness, incident và audit;
- activate/stop strategy;
- reconciliation request;
- kill switch;
- approval workflow;
- read projection cho dashboard/API.

Control plane không xử lý market tick hot path và không trả secret raw.

### 11.2 HTTP/API contract

contracts/api/openapi.yaml là canonical HTTP wire contract. Không implement route, request field, response field hay status code trước khi OpenAPI và fixture tương ứng được duyệt.

- Prefix /api/v1.
- Async POST command trả 202, command_id và Location của command status resource.
- Command lifecycle: ACCEPTED -> RUNNING -> SUCCEEDED | FAILED | CANCELLED. Terminal command record là append-only audit evidence.
- POST command có Idempotency-Key. Scope là actor_id + route_scope + key; payload canonical hash phải khớp. Same key/same payload trả original command/response; same key/different payload trả 409 IDEMPOTENCY_KEY_REUSED. Exception duy nhất là secret-ingress `credential-enrollments`: nó không nhận Idempotency-Key, không hash/fingerprint/persist body `api_key`, và dùng enrollment session một lần do secret boundary quản lý.
- idempotency retention là operations policy field, tối thiểu 24 giờ với control command; exchange order idempotency vẫn dùng ClientOrderId, không dùng HTTP key.
- Optimistic concurrency dùng resource version/If-Match; mismatch trả 412 PRECONDITION_FAILED.
- Cursor pagination phải có sort key ổn định, opaque cursor và filter schema trong OpenAPI; không offset pagination cho audit/order/feed lớn.
- Decimal là string; timestamp UTC ISO-8601 Z; UUID là UUIDv7 string.
- Error envelope bắt buộc có code, message an toàn, details schema, correlation_id, retryable và remediation_hint. Không trả stack trace, secret, vendor raw payload hoặc PII không cần thiết.

Endpoint tối thiểu:

~~~text
GET   /api/v1/health
GET   /api/v1/readiness
GET   /api/v1/runtime
POST  /api/v1/commands/reconciliations
GET   /api/v1/orders/{order_id}
GET   /api/v1/orders/{order_id}/timeline
GET   /api/v1/fills
GET   /api/v1/portfolio/snapshot
POST  /api/v1/commands/strategy-activations
POST  /api/v1/commands/strategy-stops
POST  /api/v1/commands/kill-switch-activations
POST  /api/v1/commands/kill-switch-releases
POST  /api/v1/commands/backtests
GET   /api/v1/commands/{command_id}
GET   /api/v1/incidents
GET   /api/v1/audit-events
GET   /api/v1/deployments/{deployment_id}
GET   /api/v1/ai/providers
GET   /api/v1/ai/providers/{provider_id}/models
GET   /api/v1/ai/policy-profiles
POST  /api/v1/ai/provider-connections
GET   /api/v1/ai/provider-connections
GET   /api/v1/ai/provider-connections/{connection_id}
POST  /api/v1/ai/provider-connections/{connection_id}/rotations
POST  /api/v1/ai/provider-connections/{connection_id}/credential-enrollments
POST  /api/v1/ai/provider-connections/{connection_id}/validations
POST  /api/v1/ai/provider-connections/{connection_id}/activations
POST  /api/v1/ai/provider-connections/{connection_id}/suspensions
POST  /api/v1/ai/provider-connections/{connection_id}/revocations
~~~

Route chỉ được tạo ở phase có quyền tương ứng: health/read-only từ Phase 0, backtest/reconciliation theo Phase 2–3, action strategy/kill switch theo phase runtime và AI provider connection từ Phase 6. Manual order endpoint không có trong MVP. Nếu thêm sau này phải đi qua exact risk flow, `ClientOrderId`, approval và quyền high-risk riêng.

`credential-enrollments` là exception hẹp cho secret ingress, không phải Control API request path hay command/event durable: route phải được isolate tới `secret_ingress` ghi trực tiếp approved secret provider. Body chứa `api_key` write-only qua TLS, `Cache-Control: no-store`, không có example/fixture/log/audit payload và không được hash/fingerprint để idempotency. Ingress dùng server-side enrollment session một lần bind actor/owner scope/connection/revision; nếu client mất response, client chỉ query metadata status an toàn, không auto-resubmit key. Receipt chỉ trả status/revision opaque. `rotations` là command durable riêng không chứa key; candidate được enroll/validate rồi activate atomically. Create/validate/activate/suspend/revoke connection tạo audit/command metadata không chứa raw secret. Endpoint này chỉ mở sau khi ADR-0016, secret topology và auth/RBAC Phase 6 được APPROVED.

Error catalog tối thiểu:

~~~text
VALIDATION_FAILED
AUTHENTICATION_REQUIRED
AUTHORIZATION_DENIED
IDEMPOTENCY_KEY_REUSED
PRECONDITION_FAILED
COMMAND_NOT_FOUND
COMMAND_STATE_CONFLICT
RISK_REJECTED
RUNTIME_NOT_READY
RECONCILIATION_BLOCKED
KILL_SWITCH_ACTIVE
EXTERNAL_OUTCOME_UNKNOWN
AI_PROVIDER_NOT_ALLOWED
AI_MODEL_NOT_ALLOWED
AI_CONNECTION_SCOPE_DENIED
AI_CREDENTIAL_NOT_CONFIGURED
AI_CREDENTIAL_VALIDATION_FAILED
AI_ENROLLMENT_NOT_PERMITTED
AI_EGRESS_POLICY_DENIED
AI_BUDGET_EXCEEDED
AI_PROVIDER_UNAVAILABLE
AI_OUTPUT_INVALID
AI_OUTCOME_UNKNOWN
SENSITIVE_INPUT_REJECTED
INTERNAL_ERROR
~~~

### 11.3 Authentication và authorization gate

- Local Phase 0 có thể bind Control API chỉ vào loopback để bootstrap, nhưng không được có venue credential hoặc external command.
- Trước khi kết nối testnet/paper live-data/venue bên ngoài, API phải xác thực actor, phân quyền action, audit immutable và rate limit.
- Worker dùng machine identity riêng; không dùng shared human token.
- Mọi command nguy hiểm phải có idempotency key, actor, reason, correlation ID và audit before/after hash.
- Release kill switch, approve canary, thay risk policy, đổi credential/topology và promotion deployment cần re-auth.

Auth provider/session model là OD-006 và ADR bắt buộc trước Phase 3. Bất kể provider nào, API phải thực thi permission matrix dưới đây:

| Action | Role tối thiểu | Re-auth | Audit reason |
|---|---|---|---|
| đọc health/projection | Viewer | không | không |
| request reconciliation | Technical Operator | không | có |
| activate kill switch | Technical Operator | không, nhưng actor xác thực | có |
| release kill switch | Risk Approver + Account Owner | có | có |
| activate/stop paper strategy | Technical Operator | không | có |
| approve pending risk intent | Risk Approver | có | có |
| change risk policy/deployment | Risk Approver + Account Owner theo scope | có | có |
| approve canary | Account Owner + Risk Approver | có | có |
| rotate credential/topology | Security/Backup Owner | có | có |
| xem AI provider/model catalog đã duyệt | Viewer trong owner scope | không | không |
| tạo/enroll/rotate/revoke AI connection của scope mình | Account Owner | có | có |
| validate/activate AI connection hoặc thay egress/budget policy | Account Owner + Security/Backup Owner | có | có |
| emergency suspend/revoke AI connection không thuộc scope đang thao tác | Security/Backup Owner | có | có; Account Owner notification/review bắt buộc sau containment |

### 11.4 Ownership và decision rights

Một người có thể giữ nhiều vai trong dự án solo ở Phase 0 đến paper/testnet, nhưng audit record vẫn phải ghi role hành động. Validate/activate AI connection cần record cả Account Owner và Security/Backup Owner; nếu cùng cá nhân giữ hai role ở pre-canary, phải có record hai role và waiver/approval theo policy, không được giả vờ là independent review. Quy tắc reviewer human thứ hai cho canary/live ở §1.6 vẫn áp dụng và không được thay bằng cùng actor đổi role trên UI.

| Role | Quyền/quy trách nhiệm |
|---|---|
| Account Owner | sở hữu account/capital, phê duyệt venue, canary cap, legal/terms, live scope và AI connection của scope mình; không đọc raw API key |
| Technical Operator | triển khai, chạy CI, vận hành runtime, request reconciliation, activate kill switch |
| Risk Approver | sở hữu risk policy, duyệt override/pending approval/canary risk cap |
| Security/Backup Owner | credential, topology, network allowlist, backup/restore, incident escalation, AI provider catalog/egress approval; có thể emergency suspend/revoke AI connection với re-auth/reason/audit và post-containment Account Owner review; không đọc raw API key |
| Viewer | chỉ đọc sanitized projection/audit phù hợp |
| Worker | machine identity chỉ có permission tối thiểu của process |
| AI Coding Agent | chỉ sửa code theo task/phase; không có production credential hoặc quyền deploy |

| Artifact hoặc action | Owner bắt buộc | Approver/gate |
|---|---|---|
| Risk policy | Risk Approver | Account Owner cho canary cap |
| Venue capability profile | Technical Operator | Account Owner trước Phase 3 |
| Migration/schema | Technical Operator | CI + review theo task |
| Deployment manifest | Technical Operator | Risk Approver + Account Owner theo mode |
| Backup/restore runbook | Security/Backup Owner | Restore drill evidence |
| Gate record | Technical Operator | role quy định ở §14.2 |
| Credential rotation | Security/Backup Owner | audit + verification |
| AI provider connection/profile | Account Owner | Security/Backup Owner review; validate/activate cần hai role record; ADR-0016/gate trước Phase 6 |

Dangerous action gồm release kill switch, approve canary, thay risk policy và credential rotation phải có re-auth, audit và explicit reason. Không có action high-risk nào chỉ dựa vào UI confirmation.

### 11.5 Flutter dashboard

Flutter chỉ là client của Control API:

- hiển thị mode thật, health, order/position/PnL, incident, reconciliation;
- gửi command qua API theo quyền;
- confirm/re-auth action nguy hiểm;
- mất kết nối dashboard không ảnh hưởng trading node;
- không giữ secret hoặc logic risk/execution.

---

## 12. Bảo mật, quan sát và vận hành

### 12.1 Credential policy

- Venue key, AI provider key và control-plane/session credential là ba credential class riêng, không dùng thay thế hoặc chia sẻ quyền.
- Venue key riêng cho mỗi environment/account; paper/testnet/live không dùng chung key; trade key không có withdrawal permission.
- AI provider key thuộc đúng owner scope + provider connection + environment/policy, không có venue/account capability và không được shared cross-owner.
- IP/network allowlist khi provider/venue hỗ trợ; AI egress chỉ tới endpoint profile được catalog phê duyệt.
- Secret ở approved secret provider/injection; không commit, log, trace, UI, browser storage, DB/manifest/fixture/evidence hoặc prompt.
- BYOK enrollment chỉ được phép qua write-only secret ingress; raw key không được read-back sau submit.
- Rotate theo lịch hoặc ngay khi nghi ngờ lộ; rotation/revoke của AI key phải disable binding và preserve audit metadata không chứa secret. Secret ingress, proxy/WAF/APM, request/response cache và browser path phải enforce redaction/no-store; secret-like input ở reason/note/audit bị reject.
- Binding lease của `ai_worker` phải ngắn, scope theo owner/connection/revision/job, không reusable cross-job; revoke/suspend invalidates issuance immediately, worker rechecks state/revision before egress, zeroizes after use và discards an in-flight result if revocation wins. Revocation propagation SLA/cache TTL là policy field và có drill/test trước Phase 6.
- AI worker không nhận trade key.

### 12.2 Supply chain và bảo vệ dữ liệu

- Pin dependency bằng lock file; build/release phải dùng lock đã review.
- Pin container image theo digest ở canary; không deploy tag mutable.
- CI chạy secret scan, dependency vulnerability scan và SAST phù hợp.
- Sinh SBOM cho artifact có khả năng chạy testnet/canary.
- Verify checksum của strategy/model/dataset/artifact trước activation.
- Backup và sensitive dump phải được mã hóa; remote API/telemetry dùng transport được xác thực.
- Không lưu raw secret, private account data không cần thiết hoặc prompt nhạy cảm trong log/trace/evidence.
- Code do LLM tạo phải ở sandbox, qua test/review/approval như code người viết.

### 12.3 Process và database least privilege

| Process | Quyền tối thiểu |
|---|---|
| control-api | control/operations write có kiểm soát; projection read |
| trading-node | market/strategy/risk/execution/ledger cần thiết; trade secret |
| data worker | ingest data; không có trade secret |
| research worker | đọc catalog; ghi research candidate |
| ai worker | đọc sanitized projection; ghi AI/memory proposal |
| secret_ingress | validate one-time enrollment session; direct vault write; safe receipt only; không raw-body log/hash/audit persistence |
| dashboard | chỉ gọi Control API |

Mỗi process có database role riêng. Không chạy ứng dụng bằng DB superuser.

### 12.4 Threat model tối thiểu

Phải model và kiểm thử các threat:

- API key theft, secret/log leakage;
- user-supplied AI key enrollment leak/body hash, cross-owner connection use, arbitrary endpoint/proxy/DNS/redirect/SSRF và unauthorized provider data egress;
- AI quota/billing abuse, model/capability/adapter drift, candidate rotation/revoke race, provider outage/unknown outcome và silent fallback sang provider khác;
- unauthorized deployment hoặc risk bypass;
- prompt injection/memory poisoning;
- poisoned market/reference data;
- replay/duplicate venue event;
- malicious dependency;
- dashboard session theft/CSRF;
- database tampering;
- clock manipulation;
- split-brain execution leader.

### 12.5 Observability

Mọi decision path nên mang trace_id, correlation_id, causation_id, strategy_instance_id, order_intent_id, order_id, account_id, venue_id, instrument_id và deployment_id khi có.

Metrics tối thiểu:

- market lag, gaps, reconnects, duplicate/dropped data;
- submit-to-ack, ack-to-fill, reject rate, unknown orders, slippage;
- risk verdict/reason, exposure, reservation age, stale blocks;
- reconciliation mismatch, projection lag, ledger imbalance attempts;
- DB locks/connections/disk, outbox backlog, worker heartbeat, clock drift;
- AI provider availability/latency/rate limit, initial/rotation connection validation/revocation/lease propagation, quota/budget reservation/actual usage, egress denial, output validation và circuit-breaker state nếu AI được bật.

Alert baseline:

| Severity | Ví dụ |
|---|---|
| Critical | split brain, risk bypass, ledger imbalance, kill switch failure, unknown order quá SLA |
| High | unresolved reconciliation mismatch, private stream mất lâu, daily loss breach, DB gần đầy |
| Medium | latency/reject/outbox lag spike, data-quality issue |
| Low | research/AI failure không ảnh hưởng trading |

### 12.6 Failure handling

| Lỗi | Hành vi |
|---|---|
| Validation/domain conflict | không retry |
| Transient external error | retry theo operational policy, backoff/jitter có giới hạn |
| Unknown outcome | reconcile, không retry blind |
| Permanent external error | alert/stop capability phù hợp, không retry tự động |
| Infrastructure/security error | fail closed, incident và circuit breaker |
| AI provider timeout/unknown outcome | không retry/fallback blind; normalize error, preserve no-secret evidence và disable AI capability nếu policy yêu cầu |

### 12.7 Runbook tối thiểu

Trước paper cần có runbook cho:

1. Unknown order sau timeout.
2. Private/public WebSocket disconnect hoặc stream gap.
3. Reconciliation mismatch.
4. Kill switch activate/release.
5. Trading node crash/restart.
6. Database unavailable/disk full.
7. Credential revoked/rotation.
8. Phase 6: AI connection credential compromise/revoke, provider outage/budget exhaustion và denied data egress.
9. Backup restore và rollback deployment.

Mỗi runbook phải có cùng mẫu:

| Trường | Nội dung bắt buộc |
|---|---|
| Trigger và severity | metric/event nào kích hoạt |
| Scope và owner | venue/account/instrument/process bị ảnh hưởng, ai điều hành |
| Lệnh/endpoint | command chính xác, không ghi secret |
| Expected safe state | ví dụ FREEZE, BLOCKED hoặc strategy disabled |
| Verify | query/metric/evidence chứng minh recovery |
| Rollback/escalation | khi nào dừng tự động và gọi owner |
| Evidence | incident ID, trace/correlation ID, snapshot/log path |

### 12.8 Operational cadence và incident record

| Chu kỳ | Bắt buộc thực hiện |
|---|---|
| Mỗi lần deploy | verify manifest/config hash, health, lease, reconciliation, alert route trước enable strategy |
| Hàng ngày khi paper/testnet/canary chạy | review health, outbox/DLQ, stream gap, unresolved mismatch, risk/kill-switch state |
| Hàng tuần | review capacity/disk, dependency/security alert, config drift và backup age |
| Hàng tháng trước/đang canary | restore drill, credential review/rotation plan, runbook drill, incident trend review |
| Sau critical incident | freeze scope, reconcile, post-mortem, evidence, owner sign-off trước resume |

Incident record tối thiểu gồm incident ID, severity, detection time, affected scope, timeline, correlation IDs, safe state, root cause/evidence, remediation, rollback và approver đóng incident.

---

## 13. Chất lượng, kiểm thử và kỷ luật delivery

### 13.1 Tooling bắt buộc

- Ruff cho format/lint.
- Pyright strict cho domain/application; không thêm mypy.
- Pytest.
- Hypothesis cho property tests.
- Import Linter/architecture tests.
- Alembic migration tests.
- Detect-secrets, dependency scan và container scan khi có image.
- CI trên mỗi push/merge.

Toolchain version thực tế phải được pin trong pyproject.toml, uv.lock, Docker image digest và CI image. Không ghi version range mở cho runtime dependency trong production artifact.

### 13.2 Git, review, dependency và coding standards

- main là protected branch; mọi thay đổi đi qua short-lived branch và PR/review record, kể cả dự án một người.
- Commit dùng Conventional Commit hoặc chuẩn đã ghi trong CONTRIBUTING.md; commit phải nhỏ, một ý nghĩa và link Task ID/REQ/ADR khi áp dụng.
- CODEOWNERS/review matrix: risk, OMS, ledger, migration, contract, security, deployment cần reviewer role tương ứng trong §11.4.
- Dependency mới cần Task ID, lý do, license/security review, locked version và test. Không chạy pip install hoặc thêm package tự phát.
- Python domain/application bắt buộc type hint public, immutable value object, explicit exception; không Any, type: ignore, noqa, broad except, bare except, skip/xfail hoặc TODO trên safety path nếu không có waiver ID/expiry.
- SQL chỉ ở Alembic migration hoặc persistence repository/query đã review; không chứa domain/risk rule tùy tiện.
- Generated code nằm trong generated/ và không sửa tay; source contract/template là nơi được sửa.

Command profile được mở theo phase; không yêu cầu database command trước khi database tooling tồn tại.

**Bootstrap profile — từ Task 0.1:**

~~~text
uv sync --locked
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
~~~

**Contract profile — từ Task 0.2:**

~~~text
uv run ai-auto-trade contracts validate
~~~

**Database profile — từ Task 0.3:**

~~~text
uv run ai-auto-trade db verify
~~~

CI phải gọi cùng command local trong profile mà task/phase yêu cầu. Trước khi Task 0.2 tạo contract command hoặc Task 0.3 tạo database command, gate phải ghi validator/procedure tạm thời đã được Phase 0.0 task card phê duyệt. Sau milestone đó, không được thay bằng command khác không có ADR/task-card amendment. Task report chỉ được nói pass nếu command đã chạy và exit code/artifact được lưu.

### 13.3 Test pyramid

1. Unit: value object, policy, entity.
2. Property: Decimal/rounding, ledger balance, idempotency, state transition.
3. State-machine: OMS, reconciliation, kill switch, lease.
4. Contract: venue/LLM/persistence adapters.
5. Integration: PostgreSQL/migration/outbox.
6. Replay: recorded venue fixtures.
7. Golden: fixed dataset/config/seed/event sequence.
8. Chaos: network, DB, clock, process, disk, duplicate/split-brain.
9. End-to-end: một số vertical-slice flow, không là lớp test duy nhất.

### 13.4 Test isolation, fixture và invariant

Mặc định unit/property/architecture test không có network, clock thật, global random, locale hoặc database thật. Test fixture phải pin UTC, locale, Decimal context, seed và version dataset.

- tests/fixtures chứa fixture immutable/có checksum; tests/factories tạo object hợp lệ minh bạch.
- Integration test dùng PostgreSQL ephemeral/container riêng, không dùng database developer/canary.
- Recorded venue fixture phải redaction secret/account detail, có source/version/checksum và không tự refresh.
- pytest skip/xfail cần reason chứa waiver ID; CI fail nếu waiver hết hạn.
- Requirement traceability test map phải chỉ ra FR/NFR/SEC/ADR/invariant nào được kiểm.

- Không mất precision qua serialize/deserialize.
- Mọi journal entry cân bằng.
- Duplicate fill/event không tạo hiệu ứng lần hai.
- Terminal order state không quay lại non-terminal.
- Risk không approve vượt policy.
- Tick/lot rounding đúng instrument constraint.
- Replay rebuild state giống incremental projection.
- Timeout sau submit không tạo duplicate order.
- Mất lease dừng submission.
- LLM timeout/invalid output không ảnh hưởng trading hot path.

Coverage không thay thế invariant test, nhưng baseline là coverage cho domain core từ 80% trở lên. Risk, OMS và reconciliation phải có test cho toàn bộ decision/state-transition đã hỗ trợ, kể cả khi coverage tổng đã đạt.

### 13.5 Golden backtest

Golden test phải pin:

- dataset checksum;
- code/config/risk version;
- seed;
- execution model version;
- expected event sequence và metrics tolerance.

Không chỉ assert PnL từng số khi mô hình có thành phần stochastic chưa được pin.

### 13.6 CI pipeline

~~~text
format
  -> lint
  -> type check
  -> architecture rules
  -> unit/property/state-machine
  -> schema compatibility
  -> migration upgrade
  -> integration/contract
  -> replay/golden
  -> security scan
  -> build artifact
~~~

CI artifact phải giữ tối thiểu test report, coverage summary, schema compatibility result, migration result, security scan result và digest artifact. Một test bị skip ở risk/OMS/reconciliation cần lý do/waiver được audit; không dùng skip để qua gate.

### 13.7 Release, waiver và quality enforcement

- CI chặn forbidden imports, unpinned dependency, secret, mutable image tag, public contract/schema drift, migration không có data-dictionary link và change ngoài task allowlist.
- Allowlist enforcement phải lấy Task-ID từ PR metadata/branch, validate `tasks/active/<TASK_ID>.yaml` theo schema, kiểm expiry/reviewer rồi so diff với `allowed_globs`/`forbidden_globs`. Không parse prose Markdown hoặc tin AI self-report để quyết định allowlist.
- Release artifact có commit SHA, lock checksum, SBOM, build digest và manifest link.
- Waiver cần ID, scope, reason, compensating control, approver, expiry; CI fail khi expiry qua.
- Không waiver OMS/risk/ledger/audit/credential/migration/external-venue invariant.
- Production/canary deploy chỉ từ artifact đã pass CI; không deploy source tree local hoặc generated patch chưa review.

---

## 14. Roadmap và Go/No-Go gates

### 14.1 Thứ tự triển khai bắt buộc

Đây là đường đi thực tế cho một người triển khai. Không bỏ qua bước để làm UI, AI hoặc kết nối sàn sớm:

~~~text
documentation closure + approved ADRs/contracts
  -> bootstrap + repository guard + CI
  -> database/migration/outbox
  -> fake venue + OMS
  -> risk + reservation + ledger
  -> replay/recovery/chaos
  -> data catalog + simulator + strategy mẫu
  -> public data -> read-only account -> testnet -> shadow
  -> paper evidence -> canary
~~~

### 14.2 Gate rules và evidence

Mỗi gate là một record độc lập tại docs/governance/evidence/gates/phase-N/ và phải có:

| Field | Bắt buộc |
|---|---|
| Scope | venue/account/instrument/strategy/environment áp dụng |
| Conditions | điều kiện cụ thể từ tài liệu |
| Command/test | lệnh CI, test/runbook hoặc procedure đã chạy |
| Expected/actual result | kết quả mong đợi và kết quả thực tế |
| Evidence | report, hash, log, manifest, incident hoặc artifact path |
| Runner/date | ai chạy và khi nào |
| Approver | role/actor xác nhận gate |
| Expiry/revocation | khi nào evidence hết hiệu lực hoặc điều kiện hủy gate |
| Waiver | chỉ có ADR + Account Owner; không dùng cho invariant safety |

Không có evidence thì gate là FAIL. Không dùng câu “ổn định”, “đã kiểm tra” hoặc “có vẻ tốt” thay cho điều kiện/record.

### Phase 0.0 — Documentation closure và decision baseline

**Mục tiêu:** tạo bộ điều khiển thiết kế trước khi có application code, migration, endpoint, venue credential hoặc database schema. Phase này biến master thành artifact pack có thể review; nó không phải “viết thêm tài liệu cho đẹp”.

| Task | Output bắt buộc | Owner / approver |
|---|---|---|
| 0.0.0 Bootstrap task authority | Tạo record YAML/card cho 0.0.1–0.0.7 theo §16.2 và Appendix C; không tạo application/runtime/DB code | Technical Operator / Account Owner |
| 0.0.1 Governance & product | `DOCS_INDEX`, document-control, RACI, RAID register, glossary, product charter, FR/NFR và requirement traceability | Technical Operator / Account Owner |
| 0.0.2 Architecture & toolchain | C4 context/container, runtime sequences, language/repository policy; ADR 0001, 0002, 0014 `APPROVED` | Technical Operator / Account Owner |
| 0.0.3 Domain & data design | canonical domain/OMS/risk/accounting policy; data architecture, ERD, dictionary, database standards, transaction-concurrency, DB ops, migration playbook; ADR 0003, 0004, 0005, 0007, 0011, 0012 `APPROVED` | Technical Operator (tham vấn Risk Approver cho risk policy) / Account Owner — khớp card 0.0.3 |
| 0.0.4 Contract & security baseline | OpenAPI skeleton, command/event/config schemas, error catalog, fixtures; threat model, access-control matrix, auth-session policy, secrets policy, SLO/alert policy | Technical Operator / reviewer Security/Backup Owner (card 0.0.4), gate approve bởi Account Owner |
| 0.0.5 Delivery controls | repository/coding/test/CI/AI protocol, ADR/task-card/gate templates, task-card YAML schema + CI binding design, first approved Task 0.1 card | Technical Operator / reviewer named in task card |
| 0.0.6 AI provider/BYOK baseline | ADR-0016, ARC-AI-001, SEC-AI-POL-001, 8 AI provider/policy/connection schema + fixtures, RB-009, cập nhật registry/traceability liên quan | Technical Operator / reviewer Security/Backup Owner + Account Owner (card 0.0.6) |
| 0.0.7 Codex Enterprise documentation | Đồng bộ master/AGENTS/README/DOCS_INDEX/ENG-AI-001/ENG-CI-001/contract registry; machine-readable task authority; local validation + revalidation evidence; không tạo runtime code | Technical Operator / Account Owner — DONE 2026-08-10T20:07:02Z |

**Nghiệm thu Phase 0.0:**

- Mọi path trong §1.5 tồn tại, có owner/version/status và được `DOCS_INDEX` liệt kê.
- Requirement traceability có ít nhất toàn bộ baseline ở §2.2 và map đến ADR/contract/test/gate dự kiến.
- ADR 0001–0005, 0007, 0011, 0012 và 0014 ở trạng thái `APPROVED`; ADR khác được tạo khi policy yêu cầu nhưng có thể `DRAFT` nếu chưa đến deadline.
- ERD/data dictionary mô tả mọi bảng sẽ xuất hiện ở Task 0.3; không tồn tại migration/DDL không có dictionary entry.
- OpenAPI/schema skeleton pass validation và fixture không chứa secret.
- Có task YAML/card cho mọi task 0.0.x, gồm task 0.0.7 cho Codex Enterprise documentation, ít nhất một gate record mẫu đã review, và Task 0.1 card tồn tại + pass task-card schema validation + đủ điều kiện chuyển `READY` ngay khi gate được ký (card 0.1 giữ `BLOCKED` với precondition "gate Phase 0.0 PASSED" cho tới thời điểm đó — reviewer chuyển `BLOCKED → READY` là hành động đầu tiên sau khi gate ký, không phải điều kiện trước gate). Không bắt đầu Phase 0 nếu thiếu các record này.

### Phase 0 — Foundation

**Mục tiêu:** tạo guardrail và skeleton, chưa kết nối sàn hay LLM.

**Task card theo thứ tự:**

| Task | Input | Output/acceptance |
|---|---|---|
| 0.1 Bootstrap | Phase 0.0 approved artifact pack + task card | repo skeleton theo manifest ENG-REPO-001 §2b, cập nhật README/`AGENTS.md` hiện có, uv lock, .env.example không secret |
| 0.2 Guardrails | skeleton | Ruff, strict type, pytest, Hypothesis, import rule, `contracts validate` command và CI xanh |
| 0.3 Persistence contract | ADR 0003/0004/0012 + ERD/data dictionary approved | PostgreSQL compose, Alembic base, outbox/inbox migration, contract registry skeleton |
| 0.4 Architecture contract | ADR 0001/0002/0014 | empty contexts, event schema sample, dependency test |
| 0.5 Operations skeleton | Task 0.0.7 DONE; §6/§11 + OpenAPI/config schema được Account Owner xác nhận đủ ổn định | 0.5.1 config validation + audit/error envelope (DONE); 0.5.2 local-only Control API skeleton (DONE 2026-08-11T02:14:42Z) |
| 0.6 Capability draft | Account Owner xác nhận local simulator/no venue; OD-001 vẫn OPEN cho external venue | **DONE** — capability matrix draft versioned; không gọi venue, không tạo runtime/application code |

ADR required before Phase 0 starts đã được đóng ở Phase 0.0: 0001–0005, 0007, 0011, 0012, 0014. ADR 0006 chỉ required trước khi NautilusTrader được đưa vào runtime (không muộn hơn khi mở Phase 5, §15.1); ADR 0013 trước Phase 2; ADR 0015 và 0009 trước Phase 3; ADR 0010 trước Phase 4; ADR 0008 và 0016 trước Phase 6.

**Nghiệm thu:**

- Fresh clone bootstrap bằng lệnh được ghi rõ.
- Database healthy; migration upgrade chạy thành công.
- Architecture test chứng minh domain không import framework/vendor.
- Event schema sample validate.
- Secret scan không có leak.
- Không có code gọi exchange/OpenAI hoặc live credential.
- Gate record Phase 0 có CI run ID, artifact và Technical Operator sign-off.

### Phase 1 — Core safety với fake venue

**Mục tiêu:** chứng minh OMS/risk/ledger/recovery không phụ thuộc network.

**Điều kiện vào:** Phase 0 gate pass; ADR 0005, 0007, 0011 và 0012 vẫn `APPROVED`; accounting policy, transaction map và fake-venue contract được link trong task cards. Nếu một rule ledger/risk/concurrency chưa được chốt thì Phase 1 là BLOCKED, không được thay bằng test mock.

**Công việc:**

- Immutable IDs, Decimal/time/clock/random contracts.
- OMS state-transition table, durable submit protocol, fake venue scriptable, event/outbox/inbox, replay.
- Risk policy baseline, reservation, kill switch.
- Double-entry ledger/projection.
- Startup reconciliation/lease logic dùng fake adapter.
- Strategy checkpoint/recovery contract.

**Nghiệm thu:**

- Mọi transition hợp lệ/không hợp lệ có test.
- 100 fault-injection crash/restart runs quanh submit/ack/fill: 0 duplicate order, 0 unexplained state.
- Duplicate ack/fill không tạo tác dụng lần hai.
- Ledger property tests luôn cân bằng.
- 100% negative risk cases trong test fixture bị reject.
- Mất lease chặn submission.
- Domain core coverage ít nhất 80%; risk/OMS/reconciliation transition suite đầy đủ.
- Gate record có test report, fault-injection report, migration result và Risk Approver sign-off.

### Phase 2 — Data, replay và paper simulator

**Mục tiêu:** vertical slice deterministic với dữ liệu lịch sử/replay.

**Điều kiện vào:** Phase 1 gate pass; ADR 0013 `APPROVED`; OD-007 phần legal/retention đã RESOLVED; catalog lifecycle, retention matrix và backup consistency set đã được review.

**Công việc:**

- Canonical trade/quote/candle, quality gate, Parquet writer, dataset manifest.
- Strategy SDK và một strategy mẫu.
- Simulator có fee/slippage/latency/partial-fill versioned.
- Backtest/replay runner, golden fixture, feed-health/gap recovery và alert cơ bản.
- Immutable deployment manifest cho PAPER_SIMULATOR.

**Nghiệm thu:**

- Cùng event stream, config và seed cho cùng decision/event/ledger result.
- Strategy không truy cập network/DB.
- Fixture có test no-look-ahead.
- Dataset checksum và quality report có mặt.
- Backtest report lưu đủ lineage.
- Restart từ strategy checkpoint replay đúng watermark/event offset.
- Gate record có golden artifact, dataset manifest hash và Technical Operator sign-off.

### Phase 3 — Venue đầu tiên: public data, testnet và shadow

**Mục tiêu:** kết nối một venue theo capability contract mà không dùng live **trade** credential hay live execution. `LIVE_READ_ONLY` chỉ được dùng theo §6.1 khi manifest đã phê duyệt.

**Điều kiện vào:** OD-001, OD-002, OD-003, OD-005 và OD-006 phải RESOLVED; ADR 0009 và 0015 được Account Owner phê duyệt. Không có live trade credential hay live execution ở Phase 3.

**Trình tự bắt buộc:**

1. Bật minimal authenticated Control API/audit/RBAC trước external command.
2. Public market data, quality/gap recovery và capability discovery.
3. Private account read-only trên testnet hoặc account được duyệt.
4. Reconciliation read-only.
5. Testnet submit/cancel theo capability profile; direct replace phải bị reject rõ vì không thuộc MVP.
6. PAPER_SIMULATOR với live/replay data, không gửi venue order.
7. SHADOW với live data, không gửi venue order.

**Nghiệm thu Go/No-Go external venue:**

- Chỉ 1 venue, 1 account class, 1 strategy và phạm vi instrument đã chốt.
- Venue adapter contract suite pass; unsupported capability bị reject rõ.
- Control API có actor authorization, audit immutable và re-auth cho dangerous action.
- Testnet lifecycle bao gồm accept, reject, cancel, partial/full fill, unknown outcome và restart/reconnect.
- Startup/periodic reconciliation hoạt động; mismatch alert trong tối đa 60 giây và runtime về safe state.
- Đã diễn tập disconnect, stale feed, rate-limit, DB unavailable, process crash, credential failure và kill switch.
- Backup restore drill pass.

**Nghiệm thu Go/No-Go canary readiness:**

- PAPER_SIMULATOR/SHADOW chạy liên tục ít nhất 14 ngày lịch **hoặc** 10 phiên giao dịch, lấy mốc nào dài hơn.
- Tối thiểu 100 lifecycle được ghi nhận qua simulator/testnet, gồm restart/reconnect; không duplicate order và không unresolved reconciliation mismatch.
- Backtest/replay, paper data và fee/slippage/latency assumption có báo cáo lineage.
- Gate record có capability profile checksum, runbook drill evidence, paper/shadow availability report và Risk Approver sign-off.

### Phase 4 — Canary vốn thật

**Mục tiêu:** xác minh an toàn vận hành với vốn cực nhỏ, không chứng minh alpha.

**Điều kiện bắt buộc trước canary:**

- Phase 3 canary-readiness gate pass; OD-004 RESOLVED; ADR 0010 `APPROVED`.
- Owner phê duyệt bằng văn bản venue/account/instrument/strategy/cap.
- Một sub-account canary nếu venue hỗ trợ.
- Deployment manifest, strategy/config/risk policy freeze và hash.
- Key trade-only, withdrawal disabled; IP allowlist nếu hỗ trợ.
- Runbook unknown order, reconciliation, kill switch, restore đã diễn tập.
- Không LLM tự quyết định, không multi-strategy, không auto-scale.
- Hard cap ở bot và venue nếu venue hỗ trợ.
- Risk mỗi lệnh, max notional, max orders/day, daily loss và max drawdown có giá trị cấu hình được owner ký duyệt.

**Baseline thận trọng đề xuất, phải được owner xác nhận trước khi dùng:**

- rủi ro dự kiến mỗi lệnh không quá 0,25% equity;
- tổng loss/day không quá 0,5% equity;
- không leverage hoặc mức tối thiểu được phê duyệt;
- không mở rộng vốn/phạm vi tự động.

**Dừng ngay và quay về paper nếu:**

- duplicate/unapproved order;
- risk bypass;
- unknown order hoặc reconciliation mismatch chưa giải quyết;
- audit thiếu;
- stale data dẫn đến submission;
- kill switch không hoạt động đúng;
- backup/restore hoặc lease safety bị vi phạm.

**Exit gate canary:**

- Chạy ít nhất 10 phiên giao dịch và đủ lifecycle theo tần suất strategy, không có safety-stop event.
- Mọi order/fill/fee/balance được đối soát và có audit chain đầy đủ.
- Có post-mortem/review thủ công về alert, recovery, slippage/fee assumption và runbook.
- Account Owner và Risk Approver ký gate record trước bất kỳ đề xuất tăng vốn/phạm vi.

Tăng vốn đáng kể hoặc chuyển FULL LIVE **không nằm trong tài liệu này**. Mỗi việc đó cần ADR mới, scope/risk policy mới và Go/No-Go gate riêng; canary pass không tự động là approval.

### Phase 5 — Control plane và dashboard

Chỉ thực hiện sau paper/canary ổn định. Auth/RBAC tối thiểu đã bắt buộc ở Phase 3; Phase này hoàn thiện trải nghiệm và vận hành:

- Flutter dashboard;
- incident/audit/reconciliation/deployment view;
- dangerous-action re-auth và authorization tests.

**Exit gate:** dashboard chỉ đọc projection/gửi command qua API, không giữ secret; mất dashboard không ảnh hưởng trading node; authorization/re-auth tests pass; actor/audit trail cho toàn bộ dangerous action có evidence.

### Phase 6 — AI, memory và controlled learning

Chỉ thực hiện khi core paper/canary đã ổn định, ADR 0008 và ADR 0016 `APPROVED`, OD-008 `RESOLVED`, auth/machine identity và secret-provider topology liên quan đã được phê duyệt:

- Fake/Disabled AI provider trước, CI không dùng key/provider thật.
- Provider-neutral adapter + catalog/capability profile; OpenAI chỉ là một adapter có thể chọn, không phải dependency bắt buộc.
- User BYOK connection: user chọn provider/model và policy profile đã duyệt; create/rotation command không chứa key, isolated secret ingress enroll write-only candidate key, validate với synthetic/sanitized probe rồi activate atomically theo owner/egress/budget policy.
- Endpoint profile, data-egress policy, usage/budget policy và policy profile phải versioned/reviewed; outbound chỉ qua egress gateway allowlist, không redirect/DNS/private-address bypass.
- Memory có provenance, review status, retention và point-in-time retrieval.
- Candidate -> backtest -> walk-forward -> stress -> shadow -> paper -> canary -> approval.
- Không auto-promote live, không tự sửa live code/risk/config.

**Exit gate:** tắt AI không ảnh hưởng trading; invalid/timeout output không block hot path; retrieval không dùng memory tương lai trong replay; hard budget/quota/rate limit được thực thi; raw key không xuất hiện ở response/log/trace/audit/DB/fixture/proxy/WAF/APM/cache; provider/model/endpoint/policy-profile không allowlist bị reject; cross-owner connection access bị deny; initial `PENDING_SECRET`, candidate rotation/cutover/rollback, enrollment no-hash/no-auto-retry, dual-role approval, revoke lease/in-flight, DNS/redirect/egress bypass, catalog drift/deprecation và outage drills pass; AI provider có zero trade credential và contract test chứng minh không có execution tool hoặc silent cross-provider fallback.

### Phần hoãn sau Phase 6

Multi-venue, derivatives, multi-account, distributed worker, HA, advanced ML, graph database, tax/reporting phải có ADR và gate riêng.

---

## 15. ADR, quyết định của owner và Definition of Done

### 15.1 ADR bắt buộc

| ADR | Quyết định | Required by |
|---|---|---|
| 0001 | Modular monolith trước microservice | Phase 0.0 gate |
| 0002 | Hexagonal architecture, dependency rules và composition root | Phase 0.0 gate |
| 0003 | PostgreSQL/Parquet persistence strategy, schema ownership và physical types | Phase 0.0 gate |
| 0004 | Outbox/inbox at-least-once delivery, event compatibility và DLQ | Phase 0.0 gate |
| 0005 | Canonical OMS/order lifecycle, selective event sourcing và reconciliation semantics | Phase 0.0 gate |
| 0006 | NautilusTrader boundary | Trước khi NautilusTrader vào runtime, không muộn hơn Phase 5 |
| 0007 | Risk, reservation, kill-switch và reconciliation policy | Phase 0.0 gate |
| 0008 | LLM off hot path, no trade credential | Trước Phase 6 |
| 0009 | Venue/account/instrument đầu tiên | Trước Phase 3 |
| 0010 | Canary topology, backup và deployment | Trước Phase 4 |
| 0011 | Accounting policy, chart of accounts, rounding, cost basis và ledger invariants | Phase 0.0 gate |
| 0012 | PostgreSQL transaction/isolation/locking, idempotency và execution-leader fencing | Phase 0.0 gate |
| 0013 | Data lifecycle, retention, Parquet atomicity và backup consistency | Trước Phase 2 |
| 0014 | Toolchain, repository topology, language policy và contract authority | Phase 0.0 gate |
| 0015 | Control-plane authentication, session model, machine identity và authorization enforcement | Trước Phase 3 |
| 0016 | Provider-neutral AI/BYOK connection, provider/model catalog, secret ingress, egress/budget/fallback boundary | Trước Phase 6 |

Mỗi ADR có Context, Decision, Alternatives, Consequences, Status, Date, owner, related requirements/contracts, migration/rollout impact và rollback/forward-fix note. Status hợp lệ là `DRAFT`, `APPROVED`, `REJECTED`, `SUPERSEDED`; chỉ `APPROVED` được dùng để mở gate. `SUPERSEDED` phải link tới ADR thay thế; không sửa lịch sử quyết định đã có evidence.

### 15.2 Owner phải chốt

Open Decision Register ở §0.3 là nguồn trạng thái hiện tại. Danh sách dưới đây xác định deadline tối đa:

Trước Phase 2:

- legal/compliance applicability liên quan data và retention;
- data retention, data licensing và hạ tầng backup;
- retention matrix/restore responsibilities được Security/Backup Owner xác nhận.

Trước Phase 3:

- venue đầu tiên và testnet availability;
- country/operating jurisdiction, điều khoản venue, thuế/pháp lý;
- spot-only hay sản phẩm khác; mặc định là spot-only;
- account/sub-account;
- instrument universe và trading session;
- notification channel;
- authentication provider/session, machine identity và network/secret topology.

Trước Phase 4:

- canary capital;
- max order notional, order frequency, daily loss/drawdown hard limit;
- shutdown policy cho open order;
- owner/approver identity;
- live host/topology và escalation path.

Trước Phase 6:

- AI provider/model catalog, adapter capability/version và endpoint/network egress profile;
- user/owner scope, BYOK enrollment/rotation/revoke và secret-provider topology;
- data classification, retention, data residency/terms, budget/quota/rate/fallback policy;
- AI machine identity, no-execution negative-security evidence và provider outage/credential-compromise runbook.

### 15.3 Waiver policy

- Waiver chỉ dùng cho yêu cầu SHOULD hoặc non-safety quality goal.
- Không waiver invariant ở §6.3, duplicate-order/reconciliation/ledger safety, no-withdrawal credential, auth/audit trước external venue hoặc gate canary.
- Waiver phải có ADR, scope/time limit, risk, compensating control, owner/approver và expiry.
- Waiver hết hạn tự động trở thành blocker cho deployment/gate liên quan.

### 15.4 Definition of Done cho mọi task

Task chỉ DONE khi:

- code nằm đúng context/layer;
- public interface có type hint và schema/version nếu cần;
- invariant và failure path có test;
- idempotency/concurrency được xem xét;
- telemetry/redaction/security impact được xem xét;
- migration có test nếu đổi database;
- formatter/lint/type/test liên quan pass;
- docs/ADR cập nhật nếu đổi architecture;
- không thêm dependency không giải thích;
- task YAML đã pass schema/allowlist check, status/evidence/expiry được cập nhật trước khi chuyển DONE;
- evidence/gate record cập nhật nếu task ảnh hưởng phase gate;
- report nêu file thay đổi, lệnh test, kết quả, assumption, risk còn lại.

---

## 16. Quy tắc bắt buộc cho AI Coding Agent

### 16.1 Authority và trạng thái task

`AGENTS.md` ở root (đã tồn tại từ Phase 0.0, được cập nhật tại Task 0.1) là bản rút gọn có thể thực thi của section này. AI phải đọc master, `AGENTS.md`, task card và ADR/contract liên quan trước khi sửa implementation file. Trong Pre-Phase 0 và Phase 0.0, AI chỉ được hoàn thiện/review artifact pack theo task được duyệt; chưa được tạo application, migration hoặc runtime implementation.

Task chỉ ở một trạng thái:

~~~text
READY -> IN_PROGRESS -> REVIEW -> DONE
  ^          |
  |          -> BLOCKED
~~~

Thiếu requirement, ADR, contract, allowed path, acceptance command hoặc owner/reviewer nghĩa là BLOCKED. AI phải báo blocker, không code “best guess”.

### 16.2 Task card bắt buộc

Machine-readable task card là authority cho scope thực thi: `tasks/active/<TASK_ID>.yaml` hoặc `tasks/completed/<TASK_ID>.yaml`, validate bằng `contracts/config/task-card.v1.schema.json`. `docs/governance/templates/task-card.md` là template/readable render, không được khác YAML authority.

Task YAML phải có tối thiểu:

~~~text
task_id / phase / status / owner / reviewer / expiry_at
branch_pattern và PR Task-ID binding
FR-NFR-SEC-ADR-contract references
goal / non_goals / preconditions / blockers
allowed_globs / forbidden_globs
database-api-event-config-dependency-security impact
acceptance criteria / exact required commands
evidence path / gate impact / rollback-forward-fix plan
known risk / assumption / waiver ID nếu có
~~~

CI đọc Task-ID từ PR metadata/branch theo `branch_pattern`, validate YAML/expiry/reviewer rồi so Git diff với `allowed_globs`/`forbidden_globs`. Markdown card, commit message hay AI report không thay thế check này.

Bootstrap exception duy nhất: trước khi `tasks/` và schema tồn tại, Task 0.0.0 được master này authorize sau khi Account Owner đồng ý. Nó chỉ được tạo artifact governance/document/contract/task trong `docs/`, `contracts/` và `tasks/`; không được sửa `src/`, `migrations/`, runtime `configs/`, `infra/`, lockfile hoặc deployment. Ngay khi 0.0.0 tạo YAML đầu tiên, mọi Task 0.0.x sau đó phải có card hợp lệ. Ngoài exception này, không có task card thì AI chỉ được đọc/analyze, không được sửa implementation.

### 16.3 Quy tắc trước khi code

1. Kiểm tra repository và git diff; không ghi đè thay đổi của người dùng.
2. Xác nhận phase/gate hiện tại và authority hierarchy §1.5.
3. Đọc contract/schema/ADR đã được task card trỏ tới; nếu chúng chưa tồn tại, BLOCKED.
4. Kiểm tra exact locked version/official documentation trước khi dùng API thư viện/provider.
5. Nêu assumption chỉ khi task cho phép; assumption ảnh hưởng architecture/risk/security/database phải thành ADR/OD và dừng chờ duyệt.

### 16.4 Quy tắc implementation

- Chỉ sửa allowed paths. Git diff ngoài allowlist là FAIL hoặc task mới.
- Không tạo/sửa migration, public contract, public endpoint, event type, config key, dependency, lockfile, risk/OMS/ledger/security/deployment nếu task không cho phép rõ và reviewer tương ứng chưa có.
- Không import framework/provider vào domain; không dùng float, global time/random, direct env/file/network trong strategy.
- Không hardcode/in secret, không dùng live credential trong local/CI/test, không tạo direct LLM -> exchange path.
- Không retry external submit khi outcome unknown; không bypass risk/reconciliation/kill switch.
- Không dùng Any, type: ignore, noqa, broad/bare except, test skip/xfail, mock domain logic hoặc TODO che safety risk nếu không có waiver ID còn hạn.
- Không thêm microservice, Kafka, Redis, Kubernetes, database, language hoặc framework mới nếu chưa có ADR.
- Không gọi fake/demo adapter là production-ready; capability phải bị reject rõ nếu chưa support.

### 16.5 Quy tắc test và báo cáo

- Viết/điều chỉnh test cùng code; ưu tiên invariant, recovery, idempotency, failure path hơn happy path.
- Chạy required command trong task card; không claim test pass nếu không có command/exit code/artifact.
- Cuối task phải báo: Task ID, kết quả, file thay đổi, allowed-path check, command/test đã chạy và kết quả, migration/contract impact, decision/assumption, waiver, open risk, evidence path và bước kế tiếp.
- Không tự làm bước kế tiếp hoặc phase sau khi chưa được giao.

---

## Phụ lục A — Checklist nhanh trước paper

- [ ] Contract có version và validation.
- [ ] Order state-machine, duplicate/out-of-order và unknown outcome test pass.
- [ ] Risk fail closed, reservation và kill switch pass.
- [ ] Ledger property/rebuild test pass.
- [ ] Startup/periodic reconciliation pass.
- [ ] Dataset manifest, checksum và no-look-ahead fixture có mặt.
- [ ] Strategy deterministic, simulator có fee/slippage/latency.
- [ ] Alert, audit chain, backup restore drill pass.
- [ ] Không có live key.

## Phụ lục B — Checklist nhanh trước canary

- [ ] Toàn bộ paper gate pass và có evidence.
- [ ] Venue adapter contract suite pass.
- [ ] Testnet/paper/shadow ổn định.
- [ ] Chaos/restart/lease/unknown-order drill pass.
- [ ] Key trade-only, withdrawal disabled, IP allowlist nếu có.
- [ ] Owner phê duyệt canary manifest và hard caps.
- [ ] Live host, monitoring, NTP, backup/PITR, alert routing sẵn sàng.
- [ ] Kill switch và rollback manifest đã diễn tập.
- [ ] AI không có đường đặt lệnh trực tiếp.

## Phụ lục C — Mẫu tối thiểu cho artifact pre-code

Các template/readable render trong `docs/governance/templates/` và structured source tương ứng phải dùng các trường dưới đây. Được thêm field cần thiết, không được bỏ field bắt buộc.

### C.1 Header mọi tài liệu kiểm soát

~~~text
Document ID / Title
Version / Status: DRAFT | IN_REVIEW | APPROVED | SUPERSEDED
Owner / Approver / Effective date / Last review date
Related FR-NFR-SEC / ADR / contract / task / gate evidence
Change summary
~~~

### C.2 ADR

~~~text
ADR-XXXX: <title>
Status / Date / Owner / Approver
Context and decision drivers
Decision (normative, including what is explicitly not allowed)
Alternatives considered and why rejected
Consequences / security / risk / data / operations impact
Related requirements, contracts and affected paths
Migration, rollout, rollback or forward-fix plan
Supersedes / superseded by
~~~

### C.3 Task card

Canonical file: `tasks/active/<TASK_ID>.yaml`, validate bằng `contracts/config/task-card.v1.schema.json`.

~~~yaml
task_id: "0.1"
phase: "0"
status: "READY" # READY | IN_PROGRESS | REVIEW | DONE | BLOCKED
owner: "Technical Operator"
reviewer: "Account Owner"
expiry_at: "2026-08-31T00:00:00Z"
branch_pattern: "task/0.1-*"
references:
  requirements: ["NFR-OPS-001"]
  adrs: ["ADR-0014"]
  contracts: []
goal: "..."
non_goals: []
preconditions: []
blockers: []
allowed_globs: ["README.md", "pyproject.toml"]
forbidden_globs: ["migrations/**", "src/**"]
impact: { database: false, api: false, event: false, config: false, dependency: false, security: false }
acceptance_criteria: []
required_commands: ["uv sync --locked"]
evidence_path: "docs/governance/evidence/tasks/0.1/"
gate_impact: "none"
rollback_or_forward_fix: "..."
known_risks: []
waiver_id: null
~~~

### C.4 Gate record

~~~text
Gate ID / Phase / Scope / Environment / Deployment manifest hash
Entry conditions and evidence references
Exact command/procedure / runner / UTC start-end time
Expected result / actual result / artifact hashes
Incident or exception / waiver ID (if any; safety invariant cannot be waived)
Approver role + identity / decision: PASS | FAIL | REVOKED
Expiry/revalidation condition and next permitted action
~~~

### C.5 Data dictionary entry

~~~text
Schema.table / Context owner / Purpose / Classification / Retention
Writer role / reader roles / query patterns and required indexes
Primary key / business key / foreign key scope
For every column: name, PostgreSQL type, nullable, default,
  timestamp/financial semantics, validation/enum/check, source of truth
Append-only or mutable / aggregate version / audit behavior
Related FR-NFR-SEC-ADR / migration ID / backfill + forward-fix plan
Constraint, integration and property test references
~~~

### C.6 Contract registry entry

~~~text
Contract ID / version / kind: HTTP | command | event | config
Canonical path / owner / producer / consumer / schema standard
Authentication/sensitive-data classification / partition or idempotency key
Compatibility rule / deprecation and retirement plan
Fixture path / validator / contract-test and consumer-impact evidence
Related requirement, ADR, task and migration
~~~

### C.7 Runbook

~~~text
Runbook ID / Trigger / Severity / Scope / Incident commander role
Preconditions and safe-state objective
Exact command/endpoint/query (never include secret)
Decision tree: observe -> contain -> reconcile -> recover -> verify
Rollback/escalation threshold / notification target
Evidence required / post-incident action / review cadence
~~~

---

> Tài liệu này là đặc tả kỹ thuật, không phải lời khuyên đầu tư. Mọi chiến lược phải qua backtest, paper, canary và giới hạn rủi ro đã được chủ tài khoản phê duyệt trước khi sử dụng vốn thật.
