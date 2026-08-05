# Phân loại tài liệu theo lớp Backend / Frontend / Shared / Governance

| Thuộc tính | Giá trị |
|---|---|
| Document ID | GOV-CLASS-001 |
| Phiên bản | 0.4.0 |
| Trạng thái | DRAFT |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực; chỉ có hiệu lực khi trạng thái APPROVED |
| Rà soát gần nhất | 2026-08-02 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §1.5; docs/governance/document-control.md §6; docs/governance/DOCS_INDEX.md |
| Related requirements | Không tạo requirement mới; đây là artifact tham khảo, không phải đặc tả kỹ thuật |
| Related ADR | Không có ADR liên quan hiện hành; di chuyển vật lý đã được Account Owner yêu cầu thực thi trực tiếp (bỏ qua bước ADR-0017/RACI review đề xuất ở Mục 5) — khoảng trống hợp thức hóa được theo dõi tại RAID I-009 |
| Change summary | 0.4.0 (2026-08-02): addendum §6 cập nhật corpus 103 → 105 tệp (bổ sung 2 validation record gate Phase 0.0); ghi nhận minh bạch khoảng trống approval của lần tái cấu trúc (RAID I-009) — không tự tạo approval hồi tố. |

> Tài liệu này là một artifact **tham khảo (reference)**. Mục 1–4 là bản ghi phân tích/phân loại tại thời điểm soạn thảo (2026-07-31) và bảng ánh xạ ở Mục 3 mô tả trạng thái **cũ → mới**; các đường dẫn "cũ" trong Mục 1–4 là lịch sử, không còn tồn tại trên đĩa. **Việc di chuyển vật lý theo đúng bảng ánh xạ ở Mục 3 đã được thực thi** theo yêu cầu trực tiếp của Account Owner (xem Mục 7, v0.2.0) — bỏ qua lộ trình RACI review/ADR-0017 khuyến nghị ở Mục 5. Cấu trúc hiện tại của repo phản ánh đúng cột "Đường dẫn mới" trong bảng ở Mục 3.
>
> **Ghi nhận khoảng trống governance (audit 2026-08-02):** theo GOV-DOC-001 §4, một yêu cầu trực tiếp trong trao đổi không phải approval record hợp lệ (thiếu actor/role/UTC/scope/evidence path). Việc thực thi trước khi có record như vậy là một ngoại lệ đã xảy ra, được theo dõi tại **RAID I-009**; nó phải được hợp thức hóa bằng chính quyết định ký gate Phase 0.0 của Account Owner (gate record liệt kê tái cấu trúc GOV-CLASS-001 trong phạm vi phê duyệt). Không artifact nào — kể cả tài liệu này — được tự ghi approval hồi tố thay cho Account Owner.

**Phạm vi:** Toàn bộ 81 tệp tài liệu hiện có trong repo (`docs/`, root repo, `contracts/errors/error-catalog.md`) + phân tích theo mục (17 mục) của `AI_AUTO_TRADE_MASTER_SPEC.md`.

---

## 1. Tóm tắt

**Tổng số tệp tài liệu được phân loại:** 81 tệp độc lập (không tính `AI_AUTO_TRADE_MASTER_SPEC.md`, được phân tích riêng theo 17 mục lớn vì đây là một tài liệu tổng hợp duy nhất).

| Layer | Số tệp | Tỷ lệ |
|---|---|---|
| Backend | 57 | 70,4% |
| Governance-Process | 22 | 27,2% |
| Shared-CrossCutting | 2 | 2,5% |
| **Frontend** | **0** | **0,0%** |
| **Tổng** | **81** | **100%** |

Đối chiếu với `AI_AUTO_TRADE_MASTER_SPEC.md` (17 mục cấp 1): Backend 11/17 (64,7%), Governance-Process 5/17 (29,4%), Shared-CrossCutting 1/17 (5,9%, mục 11 — Control plane/API/UI), Frontend 0/17 (0,0%).

**Phát hiện quan trọng nhất — nói thẳng, không tô hồng:** Không có bất kỳ tệp tài liệu nào trong toàn bộ 81 tệp được phân loại thuần **Frontend**. Toàn bộ nội dung liên quan đến giao diện (Flutter dashboard) chỉ tồn tại dưới dạng các đoạn văn ngắn, rải rác, nằm lồng bên trong các tài liệu được phân loại Backend hoặc Shared-CrossCutting — ví dụ §3.4 và §11.5 của master spec (~15 dòng trong một tài liệu hàng nghìn dòng), một dòng trong bảng công nghệ §3.5, một hộp nhãn "Flutter/CLI/API" không được diễn giải thêm trong sơ đồ §4.1, và các câu ranh giới đơn lẻ trong ADR-0002, ADR-0015, `c4-container.md`, `language-and-technology-policy.md`. Tổng khối lượng nội dung frontend trong toàn bộ master spec dưới 2%. Đây **không phải là một khoảng trống tài liệu cần báo động** — dự án đang chủ động hoãn Flutter dashboard đến Phase 5+ và hiện là API/CLI-first theo đúng chủ đích sản phẩm (`product-charter.md`, `functional-requirements.md`). Tuy nhiên, điều cần nói thẳng là: **hiện tại "tài liệu frontend" như một khối công việc độc lập chưa hề tồn tại** — nó chỉ là các ràng buộc phụ áp lên một client tương lai, không phải một đặc tả UI/UX. Bất kỳ ai đọc tên các thư mục tài liệu hiện có (00-governance … 06-security-ops) mà kỳ vọng tìm thấy một mảng tài liệu frontend tương xứng sẽ không tìm thấy gì.

---

## 2. Bảng phân loại chi tiết

### 2.1. docs/00-governance/

| File/Section | Layer | Lý do ngắn gọn |
|---|---|---|
| document-control.md | Governance-Process | Định nghĩa hệ thống phân cấp nguồn sự thật, vòng đời tài liệu (DRAFT/IN_REVIEW/APPROVED), quy tắc versioning và checklist gate Phase 0.0 — thuần quy trình quản trị, không có nội dung kỹ thuật backend/frontend. |
| raci.md | Governance-Process | Ma trận RACI gán vai trò (Account Owner, Technical Operator, Risk Approver, AI Coding Agent...) cho hoạt động quản trị; chỉ tham chiếu khái niệm backend để gán trách nhiệm, không thiết kế chúng. |
| raid-register.md | Governance-Process | Nhật ký vận hành các rủi ro/giả định/issue/dependency (đơn hàng trùng, gap phê duyệt ADR...) phục vụ theo dõi quản trị, không phải tài liệu thiết kế. |
| requirements-traceability.md | Governance-Process | Ma trận truy vết liên kết ID yêu cầu FR/NFR/SEC với ADR, hợp đồng, module, test và evidence gate — sổ sách bookkeeping theo dõi độ phủ yêu cầu. |

### 2.2. docs/01-product/

| File/Section | Layer | Lý do ngắn gọn |
|---|---|---|
| product-charter.md | Backend | Tầm nhìn, mục tiêu MVP, roadmap tập trung vào market data lineage, execution safety, ledger/audit; Flutter dashboard chỉ được nhắc 2 lần, cả hai đều để loại khỏi phạm vi/hoãn tới Phase 5+. |
| functional-requirements.md | Backend | Toàn bộ 8 yêu cầu chức năng (market data, strategy, order execution, ledger, recovery, risk/kill-switch, API/CLI, AI BYOK) đều là logic server-side/API lập trình; chỉ có một cụm từ phụ "UI/API MUST reject..." nằm trong yêu cầu backend AI connection. |
| non-functional-requirements.md | Shared-CrossCutting | Tiêu chí chất lượng toàn hệ thống ràng buộc mọi client — NFR-SEC-001 nêu "UI chỉ gọi Control API", NFR-AI-001 liệt kê cả route AI connection của dashboard — chính sách thực sự trải trên cả backend lẫn frontend tương lai. |
| glossary.md | Shared-CrossCutting | Thuật ngữ chuẩn dùng chung cho mọi yêu cầu/ADR/task/test bất kể phía nào, mang tính cross-cutting bản chất. |

### 2.3. docs/02-architecture/

| File/Section | Layer | Lý do ngắn gọn |
|---|---|---|
| c4-context.md | Backend | Ranh giới hệ thống, bounded context (strategy, risk, execution, ledger, market data, AI worker) và trust boundary; Viewer/Dashboard chỉ là actor read-only bị ràng buộc, không có nội dung UI thực chất. |
| c4-container.md | Backend | Topology tiến trình backend (Control API, trading node, workers, PostgreSQL, Parquet); Flutter dashboard chỉ là 1/8 dòng trong bảng, được khoanh vùng là client API thuần túy không có logic riêng. |
| runtime-sequences.md | Backend | Toàn bộ sequence diagram và invariant về xử lý market-event, submit lệnh, reconciliation, AI enrollment/inference đều backend, không có nội dung UI. |
| language-and-technology-policy.md | Backend | Ma trận công nghệ, quy tắc dependency, topology repo gần như toàn bộ là quyết định stack backend (Python, PostgreSQL, FastAPI, SQLAlchemy, Parquet); Dart/Flutter chỉ là một dòng phụ scope tới dashboard Phase 5 hoãn lại. |
| ai-provider-byok-architecture.md | Backend | Thiết kế bảo mật/kiến trúc backend cho catalog provider, secret_ingress, ai_worker, vòng đời binding secret-provider; dashboard chỉ được nhắc như thành phần hiển thị metadata bị cấm lưu/đọc lại secret. |

### 2.4. docs/03-domain/

| File/Section | Layer | Lý do ngắn gọn |
|---|---|---|
| canonical-domain-model.md | Backend | Định nghĩa bounded context, aggregate identity, value type và pipeline strategy-to-ledger được tiêu thụ lập trình bởi backend/hợp đồng — không có nội dung UI. |
| oms-state-machine.md | Backend | Máy trạng thái vòng đời lệnh chuẩn, transition guard, idempotency/dedup, thủ tục reconciliation cho execution engine — thuần logic backend. |
| risk-policy.md | Backend | Cổng rủi ro pre-trade đồng bộ: phạm vi policy, verdict, reservation, kill switch, quy tắc audit/concurrency — logic server-side. |
| accounting-policy.md | Backend | Mô hình kế toán/ledger nội bộ (journal entry, posting, projection, reconciliation, enforcement DB) — hoàn toàn backend financial domain. |

### 2.5. docs/04-data/

| File/Section | Layer | Lý do ngắn gọn |
|---|---|---|
| data-architecture.md | Backend | Ranh giới system-of-record PostgreSQL/Parquet, ownership schema, chính sách role đọc/ghi; nêu rõ "Dashboard has no production DB role". |
| erd.md | Backend | ERD khái niệm mô tả quan hệ/cardinality/key giữa các bounded context backend (risk, execution, ledger, AI connections) — không liên quan UI. |
| data-dictionary.md | Backend | Đặc tả cột vật lý cho bảng PostgreSQL (outbox/inbox/dead_letters); nêu rõ dashboard/API client không truy cập DB trực tiếp. |
| database-standards.md | Backend | Chuẩn đặt tên/kiểu dữ liệu/index/role bắt buộc cho PostgreSQL 16.x; "Dashboard/UI has no direct production database role". |
| transaction-and-concurrency.md | Backend | Ranh giới transaction, lock ordering, optimistic concurrency, retry/idempotency, leader/lease cho order submission và ledger — logic backend. |
| db-operations.md | Backend | Cách ly môi trường DB, giám sát vận hành, backup/restore/PITR, xử lý sự cố migration — hạ tầng backend thuần túy. |
| migration-backfill-playbook.md | Backend | Phương pháp expand-migrate-contract, hợp đồng backfill, evidence bắt buộc cho thay đổi schema Alembic — quy trình DDL backend. |

### 2.6. docs/05-engineering/

| File/Section | Layer | Lý do ngắn gọn |
|---|---|---|
| repository-conventions.md | Backend | Topology repo (src/ai_auto_trade/{contexts,adapters,bootstrap}), ownership, quy tắc branch/PR/commit và xử lý secret cho source/hợp đồng/migration backend — không có nội dung client. |
| coding-standards-python.md | Backend | Toolchain Python 3.12, layering domain/application/ports/adapters, quy tắc Decimal/UUIDv7/immutability, error-handling — chuẩn code backend thuần túy. |
| test-strategy.md | Backend | Test pyramid, invariant suite (OMS, risk, reconciliation, ledger), fixture tất định, kiểm thử hợp đồng/API — không có nội dung test UI. |
| ci-cd-design.md | Backend | Thiết kế pipeline CI/CD, allowlist task-card, kiểm tra hợp đồng/bảo mật/supply-chain cho source/migration/hạ tầng backend — không đề cập build frontend. |
| ai-coding-protocol.md | Backend | Giao thức vận hành và các điều cấm cho AI coding agent khi triển khai domain/adapters/migration/hợp đồng backend (Decimal, risk engine, kill switch...). |

### 2.7. docs/06-security-ops/ (bao gồm runbooks/)

| File/Section | Layer | Lý do ngắn gọn |
|---|---|---|
| threat-model.md | Backend | Threat register 16 mục (T-001..T-016) bao trùm control plane, trading node, DB, CI supply chain, BYOK egress; threat T-008 về phiên dashboard chỉ là 1 mục phụ trong catalog chủ yếu server-side. |
| access-control-matrix.md | Backend | Quy tắc RBAC server-side, ma trận hành động theo vai trò người/máy (control-api, trading-node, ai-worker...); xác thực được đánh giá hoàn toàn phía server, client "không tự cấp quyền". |
| auth-session-policy.md | Backend | Hành vi xác thực trung lập-provider phía backend cho các class định danh, xác thực lại, audit; cookie/CSRF chỉ là nhánh nhỏ trong đặc tả dịch vụ xác thực server-side. |
| secrets-and-key-management.md | Backend | Vòng đời secret, ma trận credential theo tiến trình runtime (trading-node, ai-worker, CI, data-worker), xử lý BYOK secret-ingress — hoàn toàn hạ tầng/backend. |
| slo-sli-alert-policy.md | Backend | SLI/SLO cho freshness stream, reconciliation, ledger, DB health, AI egress/budget — chỉ số vận hành server-side/runtime, không có nội dung trình bày frontend. |
| runbook-index.md | Backend | Chỉ mục runbook vận hành backend (unknown-order, stream-gap, reconciliation, kill-switch, DB, credential rotation, AI incident) kèm owner — nội dung ứng phó sự cố backend, không phải bookkeeping quy trình. |
| ai-byok-security-policy.md | Backend | Chính sách hợp nhất backend/ai-worker cho BYOK key ingress, kiểm soát egress theo provider/model/endpoint, budget/rate limit — toàn bộ về xử lý credential AI phía server. |
| runbooks/unknown-order.md | Backend | Quy trình khôi phục lệnh ở trạng thái UNKNOWN dùng API OMS/reconciliation, lệnh idempotent, evidence ledger — thuần vận hành execution/risk backend. |
| runbooks/stream-gap.md | Backend | Khôi phục gián đoạn stream market-data/private bằng resync snapshot+delta, dedup sequence — hạ tầng market-data/execution backend. |
| runbooks/reconciliation-mismatch.md | Backend | Thu thập evidence read-only và thủ tục sửa lệch order/fill/balance/position — logic ledger/OMS backend. |
| runbooks/kill-switch.md | Backend | Kích hoạt/gỡ kill switch qua API command với re-authentication, xác minh scope; nêu rõ "No UI-only confirmation." |
| runbooks/trading-node-restart.md | Backend | Thủ tục restart/failover trading runtime: leader lease/fencing, xác minh manifest, replay outbox/inbox — hạ tầng execution node backend. |
| runbooks/database-unavailable.md | Backend | Khôi phục fail-closed khi DB mất kết nối/hỏng dung lượng/integrity — hạ tầng persistence/audit/ledger backend. |
| runbooks/backup-restore.md | Backend | Thủ tục restore cách ly và verify tập nhất quán qua PostgreSQL/WAL, Parquet, manifest triển khai — phục hồi dữ liệu/hạ tầng backend. |
| runbooks/credential-rotation.md | Backend | Xoay vòng/thu hồi credential giao dịch và hệ thống qua manifest triển khai, reconciliation sau rollover — quy trình bảo mật/vận hành backend. |
| runbooks/ai-provider-connection-incident.md | Backend | Ứng phó sự cố kết nối AI BYOK: tạm ngưng secret-binding, ngăn egress, xoay vòng qua control path backend, cô lập ai worker khỏi trading. |

### 2.8. docs/adr/

| File/Section | Layer | Lý do ngắn gọn |
|---|---|---|
| README.md | Governance-Process | Chỉ mục/đăng ký ADR (trạng thái, gate pha, quy trình phê duyệt) — bookkeeping thuần túy, không có nội dung kiến trúc. |
| 0001-modular-monolith.md | Backend | Quyết định topology triển khai server-side (repo đơn, bounded context, dispatch in-process, PostgreSQL system of record). |
| 0002-hexagonal-architecture.md | Backend | Quy tắc phụ thuộc domain/application/ports/adapters backend; "UI cannot call venue/database" chỉ là một dòng ranh giới phụ. |
| 0003-persistence-strategy.md | Backend | Kiến trúc lưu trữ PostgreSQL/Parquet, kiểu vật lý (UUIDv7, NUMERIC(38,18), TIMESTAMPTZ), migration, backup — thuần backend. |
| 0004-outbox-inbox-delivery.md | Backend | Cơ chế delivery outbox/inbox, consumer idempotent, DLQ, versioning sự kiện nội bộ server-side. |
| 0005-canonical-oms.md | Backend | Máy trạng thái OMS chuẩn, sinh client order ID, lịch sử sự kiện, reconciliation thuộc execution context. |
| 0006-nautilus-boundary.md | Backend | Ranh giới đánh giá thư viện NautilusTrader làm adapter backend đằng sau port — quyết định dependency server-side. |
| 0007-risk-kill-switch-reconciliation.md | Backend | Cổng rủi ro pre-trade đồng bộ, reservation, phân cấp kill switch, chính sách reconciliation — logic trading an toàn backend. |
| 0008-llm-off-hot-path.md | Backend | Cô lập ai_worker khỏi execution (không credential venue, không port thực thi) — ranh giới an toàn/kiến trúc backend. |
| 0009-first-venue-account-instrument.md | Backend | Tiêu chí phê duyệt venue adapter backend (capability profile, credential class) trước tích hợp Phase 3. |
| 0010-canary-topology-backup-deployment.md | Backend | Kiểm soát triển khai canary real-capital: image pinning, machine identity, backup/PITR — hạ tầng backend. |
| 0011-accounting-policy.md | Backend | Invariant ledger double-entry, chart of accounts, quy tắc posting cho portfolio_ledger — mô hình tài chính backend. |
| 0012-transaction-concurrency.md | Backend | Isolation level PostgreSQL, lock ordering, CAS/versioning, leader fencing chống double exposure — kiến trúc concurrency backend. |
| 0013-data-lifecycle-retention.md | Backend | Phân loại retention, atomicity ghi Parquet (temp/checksum/commit marker), backup consistency set — data-ops backend. |
| 0014-toolchain-repo-contract-authority.md | Backend | Bắt buộc toolchain Python 3.12/uv/Pyright/Ruff, topology repo src/ai_auto_trade, thứ tự authority hợp đồng; Flutter ngoài phạm vi ADR này. |
| 0015-authentication-session-machine-identity.md | Backend | Xác thực Control API, machine identity theo tiến trình, ma trận RBAC/permission, audit correlation server-side; "dashboard has no direct DB/venue access" chỉ là câu ranh giới phụ. |
| 0016-provider-neutral-byok-ai-connections.md | Backend | Catalog AI provider backend, máy trạng thái vòng đời kết nối, ranh giới secret_ingress, kiểm soát egress gateway, RBAC BYOK; UI chỉ được nhắc là không được nhận endpoint/key tự do. |

### 2.9. docs/templates/ và docs/evidence/

| File/Section | Layer | Lý do ngắn gọn |
|---|---|---|
| templates/adr.md | Governance-Process | Khung mẫu ADR rỗng nội dung (context/decision/alternatives/consequences) — định nghĩa quy trình soạn thảo, không phải quyết định kỹ thuật cụ thể. |
| templates/task-card.md | Governance-Process | Khung YAML task-card chuẩn và bản render đọc được, dùng để uỷ quyền/theo dõi mọi task triển khai — công cụ delivery-process. |
| templates/gate-record.md | Governance-Process | Mẫu ghi nhận điều kiện đầu vào/quyết định/sign-off phase gate — bookkeeping quy trình, không có nội dung kỹ thuật theo lĩnh vực. |
| evidence/gates/README.md | Governance-Process | Ghi chú index một đoạn trỏ tới vị trí lưu evidence gate — bookkeeping thuần túy. |
| evidence/gates/phase-0.0/review-checklist.md | Governance-Process | Checklist checkbox cho review governance/architecture/domain/contracts/delivery-control/AI trước khi gate Phase 0.0 pass — bookkeeping audit. |
| evidence/gates/phase-0.0/gate-record.md | Governance-Process | Ghi nhận điều kiện đầu vào, kết quả thủ tục, quyết định pass/fail gate Phase 0.0 — hồ sơ quy trình/audit. |
| evidence/tasks/README.md | Governance-Process | Quy tắc một đoạn mô tả nơi lưu và nội dung evidence task bất biến — hướng dẫn quy trình. |
| evidence/tasks/0.0.0/README.md | Governance-Process | Ghi chú trạng thái placeholder cho evidence task bootstrap authority — bookkeeping. |
| evidence/tasks/0.0.1/README.md | Governance-Process | Ghi chú trạng thái chờ Account Owner review artifact governance/product — bookkeeping. |
| evidence/tasks/0.0.2/README.md | Governance-Process | Ghi chú trạng thái chờ review kiến trúc/ADR — bookkeeping, không có nội dung thiết kế. |
| evidence/tasks/0.0.3/README.md | Governance-Process | Ghi chú trạng thái chờ review domain/data/accounting — bookkeeping. |
| evidence/tasks/0.0.4/README.md | Governance-Process | Ghi chú trạng thái chờ review hợp đồng/schema và bảo mật — bookkeeping. |
| evidence/tasks/0.0.5/README.md | Governance-Process | Ghi chú trạng thái chờ review engineering/delivery-control — bookkeeping. |
| evidence/tasks/0.0.6/README.md | Governance-Process | Quy tắc evidence cho task AI/BYOK (cấm lưu key/secret/payload thô) và trỏ tới tài liệu liên quan — hướng dẫn xử lý evidence. |
| evidence/tasks/0.0.6/validation-2026-07-30.md | Governance-Process | Bản ghi audit trail của một lần validate kỹ thuật cục bộ (schema/OpenAPI, quét pattern secret, hash artifact), có disclaimer rõ "không phải phê duyệt" — bằng chứng tuân thủ quy trình. |

### 2.10. docs/ (gốc), root repo, và contracts/

| File/Section | Layer | Lý do ngắn gọn |
|---|---|---|
| docs/DOCS_INDEX.md | Governance-Process | Index tổng liệt kê mọi artifact Phase 0.0, trạng thái và thứ tự review bắt buộc — chỉ mục quản trị thuần túy. |
| docs/contract-registry.md | Backend | Quy tắc kỹ thuật thực chất cho hợp đồng backend (canonical OpenAPI/JSON Schema, mapping HTTP command-to-durable-record, resolve $id offline, versioning) — thiết kế API/hợp đồng, không đơn thuần bookkeeping. |
| COMMIT_NOTES.md | Governance-Process | Ghi chú commit/checklist pre-commit, trạng thái gate (IN_REVIEW/NOT PASSED), phạm vi loại trừ — bookkeeping quy trình commit thuần túy. |
| contracts/errors/error-catalog.md | Backend | Envelope lỗi chuẩn và mapping HTTP status cho hợp đồng OpenAPI (bao gồm lỗi risk/reconciliation/kill-switch và AI BYOK) — hợp đồng API lập trình do backend trả về. |

### 2.11. AI_AUTO_TRADE_MASTER_SPEC.md — theo mục

| Section | Layer | Lý do ngắn gọn |
|---|---|---|
| 0. Start here — control panel | Governance-Process | Bảng trạng thái vận hành sống (phase hiện tại, blocker, Open Decision Register) và checklist đầu ngày — bookkeeping quy trình. |
| 1. Cách dùng và quản trị tài liệu | Governance-Process | Quy ước MUST/SHOULD/MAY, hệ thống authority, gói artifact tiền-code, RACI, quy tắc version — quản trị chính tài liệu, không phải một layer kỹ thuật. |
| 2. Mục tiêu, phạm vi MVP và phần hoãn | Backend | Vertical slice MVP và bảng FR/NFR (market data, strategy, execution, ledger, reconciliation, risk, ops API/CLI) mô tả năng lực hệ thống backend; danh sách hoãn loại trừ rõ "Full Flutter dashboard" thay vì thiết kế nó. |
| 3. Các quyết định kiến trúc đã chốt | Backend | Gần như toàn bộ chốt công nghệ backend (Python, PostgreSQL, Parquet/DuckDB, FastAPI, event bus, Decimal/NUMERIC, hashing, ranh giới Nautilus); có một quyết định UI nhỏ (§3.4) và một dòng Dart/Flutter trong bảng §3.5. |
| 4. Kiến trúc, ranh giới và luật phụ thuộc | Backend | Bounded context, luật phụ thuộc, cấu trúc repo, phạm vi credential theo tiến trình là kiến trúc backend/service; hộp "Flutter/CLI/API" trong sơ đồ không được diễn giải thêm và repo skeleton không có thư mục frontend. |
| 5. Hợp đồng domain chuẩn | Backend | Định nghĩa hợp đồng domain server-side — identifier, market-event, OrderIntent, OMS state machine, RiskDecision, event envelope — hoàn toàn backend modeling. |
| 6. Mode, môi trường, cấu hình và release | Backend | Ma trận run-mode/credential-class, topology môi trường, độ ưu tiên cấu hình, giao thức manifest/release — mối quan tâm runtime/hạ tầng backend. |
| 7. Eventing, persistence và quyền sở hữu dữ liệu | Backend | Ngữ nghĩa command/event/query, delivery outbox/inbox, quyền sở hữu DDL PostgreSQL, transaction/concurrency, migration/backup — thiết kế data-layer/hạ tầng backend. |
| 8. Trading core: strategy, risk, OMS, ledger và reconciliation | Backend | Strategy SDK, risk engine, giao thức submit bền vững, kill switch, ledger double-entry — lõi logic trading server-side, không có nội dung UI. |
| 9. Market data, catalog lịch sử và backtest | Backend | Phân lớp dữ liệu (bronze/silver/gold), dataset manifest, cổng chất lượng dữ liệu, metric backtest — mối quan tâm data-engineering/research-pipeline backend. |
| 10. Adapter và tích hợp bên ngoài | Backend | Port adapter venue/AI, vòng đời kết nối BYOK, hợp đồng memory/candidate-learning là thiết kế tích hợp server-side; một câu ràng buộc hành vi UI tương lai nhưng không đặc tả UI. |
| 11. Control plane, API, UI và phân quyền | Shared-CrossCutting | Phần lớn (§11.1–§11.4) là backend — toàn bộ hợp đồng Control-API/OpenAPI và ma trận vai trò auth/authorization — nhưng §11.5 là tiểu mục riêng đặc tả hành vi client Flutter dashboard, khiến đây là mục duy nhất thực sự phủ cả hai lớp. |
| 12. Bảo mật, quan sát và vận hành | Backend | Chính sách credential, threat model, observability/metric, xử lý sự cố, runbook là nội dung security/ops backend; dashboard chỉ được nhắc 2 lần thoáng qua (một threat CSRF, và "chỉ gọi Control API"). |
| 13. Chất lượng, kiểm thử và kỷ luật delivery | Backend | Toolchain (Ruff, Pyright, Pytest, Hypothesis), chuẩn git/review, test pyramid và pipeline CI đều nhắm vào codebase Python backend; chưa có tooling/test frontend vì chưa có code frontend. |
| 14. Roadmap và Go/No-Go gates | Governance-Process | Khung gate theo pha (điều kiện vào/ra, trường evidence); gần như mọi deliverable là backend, chỉ Phase 5 đưa Flutter dashboard vào như một milestone, nhưng bản thân nội dung mục này là bookkeeping roadmap/gate. |
| 15. ADR, quyết định của owner và Definition of Done | Governance-Process | Đăng ký ADR bắt buộc, hạn quyết định của owner, chính sách waiver, Definition of Done — bookkeeping quyết định/quản trị; 16 chủ đề ADR gần như toàn bộ backend/kiến trúc, không có ADR nào dành cho frontend. |
| 16. Quy tắc bắt buộc cho AI Coding Agent | Governance-Process | Quy tắc vận hành cho AI coding agent (authority task-card, kiểm tra tiền-code, quy tắc báo cáo) — kỷ luật quy trình delivery, không phải đặc tả kỹ thuật backend hay frontend. |

---

## 3. Đề xuất cấu trúc Enterprise-Grade

Cấu trúc đề xuất tách rõ 4 lớp thành 4 nhóm cấp cao nhất dưới `docs/`, giữ nguyên tên tệp gốc (chỉ đổi vị trí thư mục) để tối thiểu hoá rủi ro diff/blame khi thực hiện `git mv`:

```text
docs/
├── governance/
│   ├── document-control.md
│   ├── raci.md
│   ├── raid-register.md
│   ├── requirements-traceability.md
│   ├── DOCS_INDEX.md
│   ├── COMMIT_NOTES.md
│   ├── adr/
│   │   └── README.md                       (chỉ mục ADR — nội dung ADR nằm ở backend/adr/)
│   ├── templates/
│   │   ├── adr.md
│   │   ├── task-card.md
│   │   └── gate-record.md
│   └── evidence/
│       ├── gates/...
│       └── tasks/...
├── shared/
│   ├── glossary.md
│   └── product/
│       └── non-functional-requirements.md
├── backend/
│   ├── product/
│   │   ├── product-charter.md
│   │   └── functional-requirements.md
│   ├── architecture/       (5 tệp — c4-context, c4-container, runtime-sequences, language-and-technology-policy, ai-provider-byok-architecture)
│   ├── domain/             (4 tệp — canonical-domain-model, oms-state-machine, risk-policy, accounting-policy)
│   ├── data/                (7 tệp — data-architecture … migration-backfill-playbook)
│   ├── engineering/         (5 tệp — repository-conventions … ai-coding-protocol)
│   ├── security-ops/        (7 tệp chính sách + 9 tệp runbooks/)
│   ├── adr/                 (0001–0016, 16 tệp)
│   └── contracts/
│       └── contract-registry.md
└── frontend/
    └── (trống — sẽ khởi tạo khi Phase 5 bắt đầu thiết kế Flutter dashboard thật sự)

contracts/                    <- GIỮ NGUYÊN vị trí gốc, KHÔNG di chuyển (xem Mục 4)
└── errors/error-catalog.md
```

Ghi chú thiết kế:

- `docs/frontend/` được tạo **rỗng** làm placeholder có chủ đích — phản ánh đúng thực trạng (0 tệp frontend hiện có) thay vì giả vờ có nội dung để lấp đầy cấu trúc.
- ADR được tách: chỉ mục đăng ký (`README.md`, Governance-Process) ở `governance/adr/`, còn 16 ADR nội dung (đều Backend) ở `backend/adr/`. Đây là điểm cần cân nhắc thêm — xem khuyến nghị ở Mục 5 nếu muốn giữ ADR làm một chuỗi đánh số liền mạch thay vì tách theo layer.
- `contracts/` (thư mục JSON Schema/OpenAPI/fixtures cấp gốc repo, ngang hàng `docs/`) được đề xuất **không di chuyển** vì đây là artifact được tiêu thụ bởi tooling/CI (resolve `$id` offline, `$ref` trong `openapi.yaml`), không phải tài liệu thuần đọc-hiểu — di chuyển nó thuộc phạm vi một sáng kiến khác (tái cấu trúc contracts, không phải tái cấu trúc docs).

### Bảng ánh xạ đầy đủ đường dẫn cũ → mới (toàn bộ 81 tệp)

| # | Đường dẫn cũ | Đường dẫn mới | Layer |
|---|---|---|---|
| 1 | docs/00-governance/document-control.md | docs/governance/document-control.md | Governance-Process |
| 2 | docs/00-governance/raci.md | docs/governance/raci.md | Governance-Process |
| 3 | docs/00-governance/raid-register.md | docs/governance/raid-register.md | Governance-Process |
| 4 | docs/00-governance/requirements-traceability.md | docs/governance/requirements-traceability.md | Governance-Process |
| 5 | docs/01-product/product-charter.md | docs/backend/product/product-charter.md | Backend |
| 6 | docs/01-product/functional-requirements.md | docs/backend/product/functional-requirements.md | Backend |
| 7 | docs/01-product/non-functional-requirements.md | docs/shared/product/non-functional-requirements.md | Shared-CrossCutting |
| 8 | docs/01-product/glossary.md | docs/shared/glossary.md | Shared-CrossCutting |
| 9 | docs/02-architecture/c4-context.md | docs/backend/architecture/c4-context.md | Backend |
| 10 | docs/02-architecture/c4-container.md | docs/backend/architecture/c4-container.md | Backend |
| 11 | docs/02-architecture/runtime-sequences.md | docs/backend/architecture/runtime-sequences.md | Backend |
| 12 | docs/02-architecture/language-and-technology-policy.md | docs/backend/architecture/language-and-technology-policy.md | Backend |
| 13 | docs/02-architecture/ai-provider-byok-architecture.md | docs/backend/architecture/ai-provider-byok-architecture.md | Backend |
| 14 | docs/03-domain/canonical-domain-model.md | docs/backend/domain/canonical-domain-model.md | Backend |
| 15 | docs/03-domain/oms-state-machine.md | docs/backend/domain/oms-state-machine.md | Backend |
| 16 | docs/03-domain/risk-policy.md | docs/backend/domain/risk-policy.md | Backend |
| 17 | docs/03-domain/accounting-policy.md | docs/backend/domain/accounting-policy.md | Backend |
| 18 | docs/04-data/data-architecture.md | docs/backend/data/data-architecture.md | Backend |
| 19 | docs/04-data/erd.md | docs/backend/data/erd.md | Backend |
| 20 | docs/04-data/data-dictionary.md | docs/backend/data/data-dictionary.md | Backend |
| 21 | docs/04-data/database-standards.md | docs/backend/data/database-standards.md | Backend |
| 22 | docs/04-data/transaction-and-concurrency.md | docs/backend/data/transaction-and-concurrency.md | Backend |
| 23 | docs/04-data/db-operations.md | docs/backend/data/db-operations.md | Backend |
| 24 | docs/04-data/migration-backfill-playbook.md | docs/backend/data/migration-backfill-playbook.md | Backend |
| 25 | docs/05-engineering/repository-conventions.md | docs/backend/engineering/repository-conventions.md | Backend |
| 26 | docs/05-engineering/coding-standards-python.md | docs/backend/engineering/coding-standards-python.md | Backend |
| 27 | docs/05-engineering/test-strategy.md | docs/backend/engineering/test-strategy.md | Backend |
| 28 | docs/05-engineering/ci-cd-design.md | docs/backend/engineering/ci-cd-design.md | Backend |
| 29 | docs/05-engineering/ai-coding-protocol.md | docs/backend/engineering/ai-coding-protocol.md | Backend |
| 30 | docs/06-security-ops/threat-model.md | docs/backend/security-ops/threat-model.md | Backend |
| 31 | docs/06-security-ops/access-control-matrix.md | docs/backend/security-ops/access-control-matrix.md | Backend |
| 32 | docs/06-security-ops/auth-session-policy.md | docs/backend/security-ops/auth-session-policy.md | Backend |
| 33 | docs/06-security-ops/secrets-and-key-management.md | docs/backend/security-ops/secrets-and-key-management.md | Backend |
| 34 | docs/06-security-ops/slo-sli-alert-policy.md | docs/backend/security-ops/slo-sli-alert-policy.md | Backend |
| 35 | docs/06-security-ops/runbook-index.md | docs/backend/security-ops/runbook-index.md | Backend |
| 36 | docs/06-security-ops/ai-byok-security-policy.md | docs/backend/security-ops/ai-byok-security-policy.md | Backend |
| 37 | docs/06-security-ops/runbooks/unknown-order.md | docs/backend/security-ops/runbooks/unknown-order.md | Backend |
| 38 | docs/06-security-ops/runbooks/stream-gap.md | docs/backend/security-ops/runbooks/stream-gap.md | Backend |
| 39 | docs/06-security-ops/runbooks/reconciliation-mismatch.md | docs/backend/security-ops/runbooks/reconciliation-mismatch.md | Backend |
| 40 | docs/06-security-ops/runbooks/kill-switch.md | docs/backend/security-ops/runbooks/kill-switch.md | Backend |
| 41 | docs/06-security-ops/runbooks/trading-node-restart.md | docs/backend/security-ops/runbooks/trading-node-restart.md | Backend |
| 42 | docs/06-security-ops/runbooks/database-unavailable.md | docs/backend/security-ops/runbooks/database-unavailable.md | Backend |
| 43 | docs/06-security-ops/runbooks/backup-restore.md | docs/backend/security-ops/runbooks/backup-restore.md | Backend |
| 44 | docs/06-security-ops/runbooks/credential-rotation.md | docs/backend/security-ops/runbooks/credential-rotation.md | Backend |
| 45 | docs/06-security-ops/runbooks/ai-provider-connection-incident.md | docs/backend/security-ops/runbooks/ai-provider-connection-incident.md | Backend |
| 46 | docs/adr/README.md | docs/governance/adr/README.md | Governance-Process |
| 47 | docs/adr/0001-modular-monolith.md | docs/backend/adr/0001-modular-monolith.md | Backend |
| 48 | docs/adr/0002-hexagonal-architecture.md | docs/backend/adr/0002-hexagonal-architecture.md | Backend |
| 49 | docs/adr/0003-persistence-strategy.md | docs/backend/adr/0003-persistence-strategy.md | Backend |
| 50 | docs/adr/0004-outbox-inbox-delivery.md | docs/backend/adr/0004-outbox-inbox-delivery.md | Backend |
| 51 | docs/adr/0005-canonical-oms.md | docs/backend/adr/0005-canonical-oms.md | Backend |
| 52 | docs/adr/0006-nautilus-boundary.md | docs/backend/adr/0006-nautilus-boundary.md | Backend |
| 53 | docs/adr/0007-risk-kill-switch-reconciliation.md | docs/backend/adr/0007-risk-kill-switch-reconciliation.md | Backend |
| 54 | docs/adr/0008-llm-off-hot-path.md | docs/backend/adr/0008-llm-off-hot-path.md | Backend |
| 55 | docs/adr/0009-first-venue-account-instrument.md | docs/backend/adr/0009-first-venue-account-instrument.md | Backend |
| 56 | docs/adr/0010-canary-topology-backup-deployment.md | docs/backend/adr/0010-canary-topology-backup-deployment.md | Backend |
| 57 | docs/adr/0011-accounting-policy.md | docs/backend/adr/0011-accounting-policy.md | Backend |
| 58 | docs/adr/0012-transaction-concurrency.md | docs/backend/adr/0012-transaction-concurrency.md | Backend |
| 59 | docs/adr/0013-data-lifecycle-retention.md | docs/backend/adr/0013-data-lifecycle-retention.md | Backend |
| 60 | docs/adr/0014-toolchain-repo-contract-authority.md | docs/backend/adr/0014-toolchain-repo-contract-authority.md | Backend |
| 61 | docs/adr/0015-authentication-session-machine-identity.md | docs/backend/adr/0015-authentication-session-machine-identity.md | Backend |
| 62 | docs/adr/0016-provider-neutral-byok-ai-connections.md | docs/backend/adr/0016-provider-neutral-byok-ai-connections.md | Backend |
| 63 | docs/templates/adr.md | docs/governance/templates/adr.md | Governance-Process |
| 64 | docs/templates/task-card.md | docs/governance/templates/task-card.md | Governance-Process |
| 65 | docs/templates/gate-record.md | docs/governance/templates/gate-record.md | Governance-Process |
| 66 | docs/evidence/gates/README.md | docs/governance/evidence/gates/README.md | Governance-Process |
| 67 | docs/evidence/gates/phase-0.0/review-checklist.md | docs/governance/evidence/gates/phase-0.0/review-checklist.md | Governance-Process |
| 68 | docs/evidence/gates/phase-0.0/gate-record.md | docs/governance/evidence/gates/phase-0.0/gate-record.md | Governance-Process |
| 69 | docs/evidence/tasks/README.md | docs/governance/evidence/tasks/README.md | Governance-Process |
| 70 | docs/evidence/tasks/0.0.0/README.md | docs/governance/evidence/tasks/0.0.0/README.md | Governance-Process |
| 71 | docs/evidence/tasks/0.0.1/README.md | docs/governance/evidence/tasks/0.0.1/README.md | Governance-Process |
| 72 | docs/evidence/tasks/0.0.2/README.md | docs/governance/evidence/tasks/0.0.2/README.md | Governance-Process |
| 73 | docs/evidence/tasks/0.0.3/README.md | docs/governance/evidence/tasks/0.0.3/README.md | Governance-Process |
| 74 | docs/evidence/tasks/0.0.4/README.md | docs/governance/evidence/tasks/0.0.4/README.md | Governance-Process |
| 75 | docs/evidence/tasks/0.0.5/README.md | docs/governance/evidence/tasks/0.0.5/README.md | Governance-Process |
| 76 | docs/evidence/tasks/0.0.6/README.md | docs/governance/evidence/tasks/0.0.6/README.md | Governance-Process |
| 77 | docs/evidence/tasks/0.0.6/validation-2026-07-30.md | docs/governance/evidence/tasks/0.0.6/validation-2026-07-30.md | Governance-Process |
| 78 | docs/DOCS_INDEX.md | docs/governance/DOCS_INDEX.md | Governance-Process |
| 79 | docs/contract-registry.md | docs/backend/contracts/contract-registry.md | Backend |
| 80 | COMMIT_NOTES.md | docs/governance/COMMIT_NOTES.md (tuỳ chọn: có thể giữ ở gốc repo — xem Mục 4) | Governance-Process |
| 81 | contracts/errors/error-catalog.md | contracts/errors/error-catalog.md (KHÔNG ĐỔI — xem Mục 4) | Backend |

*(Ghi chú ngoài bảng: `AI_AUTO_TRADE_MASTER_SPEC.md` không nằm trong danh sách 81 tệp gốc — đây là tài liệu tổng hợp một-tệp-nhiều-lớp. Khuyến nghị giữ nguyên vị trí gốc repo làm "tài liệu vào cửa" (entry point) duy nhất; việc tách nó ra theo mục vào các thư mục backend/shared/governance tương ứng là một sáng kiến riêng, rủi ro cao hơn nhiều so với việc di chuyển các tệp rời, nên không đưa vào phạm vi di chuyển vật lý lần này.)*

---

## 4. Rủi ro khi thực hiện di chuyển vật lý

Việc đổi tên thư mục/di chuyển tệp (`git mv`) không phải là thao tác "miễn phí" trong bộ tài liệu này, vì nhiều tệp **mã hoá cứng đường dẫn hiện tại** hoặc đóng vai trò sổ sách/bằng chứng gắn với đường dẫn cụ thể:

1. **`docs/DOCS_INDEX.md`** — là "index tổng liệt kê mọi artifact Phase 0.0" theo từng thư mục 00–06, kèm link Markdown tương đối tới từng tệp. Di chuyển vật lý sẽ làm **toàn bộ danh sách này lỗi thời ngay lập tức**, cần viết lại hoàn toàn.
2. **`docs/00-governance/document-control.md` §6** — bảng "Vị trí chuẩn" (canonical location) đã quy định rõ artifact loại nào nằm ở đâu (ví dụ "ADR → docs/adr", "Governance/product/architecture → docs/00-governance, docs/01-product, docs/02-architecture"). Đây là tài liệu **có thẩm quyền cao nhất** về cấu trúc, nên bất kỳ thay đổi cấu trúc nào cũng phải sửa chính bảng này trước, không phải sau.
3. **`docs/00-governance/requirements-traceability.md`** — ma trận truy vết liên kết ID yêu cầu với ADR, hợp đồng, module và **gate evidence**; loại ma trận này thường trỏ theo đường dẫn tệp cụ thể tới ADR/tài liệu domain. Di chuyển vật lý có nguy cơ làm gãy các liên kết truy vết này.
4. **`docs/contract-registry.md`** — quy định "offline `$id` schema resolution" và thứ tự authority hợp đồng; các tham chiếu chéo tới ADR/kiến trúc theo đường dẫn cần được rà soát.
5. **`AI_AUTO_TRADE_MASTER_SPEC.md` §1.5** — liệt kê chính xác cây thư mục `docs/00-governance/{...}.md`, `docs/01-product/{...}.md`, v.v. như "gói artifact tiền-code" (pre-code artifact pack) dùng để gate Phase 0.0. Đây là danh sách gate; sai đường dẫn ở đây có thể chặn nhầm hoặc bỏ sót điều kiện gate.
6. **§15 của master spec** (đăng ký ADR bắt buộc) và **`docs/adr/README.md`** — nếu các mục này chứa link Markdown tương đối tới từng ADR (`../adr/0001-...md`), việc tách `README.md` (đề xuất vào `governance/adr/`) khỏi nội dung ADR (đề xuất vào `backend/adr/`) sẽ phá vỡ các liên kết đó — cần cân nhắc kỹ trước khi tách, hoặc giữ cả thư mục `adr/` nguyên vẹn làm một khối (xem khuyến nghị Mục 5).
7. **Liên kết chéo giữa các ADR** — nhiều ADR trích dẫn nhau và trích dẫn tài liệu domain/data bằng liên kết Markdown tương đối — mọi liên kết dạng này trong cả 81 tệp cần một lượt quét/sửa tự động (link-check) sau khi di chuyển.
8. **`docs/evidence/gates/phase-0.0/gate-record.md`** và **`review-checklist.md`** — các hồ sơ này ghi nhận "điều kiện đầu vào" và kết quả review **tại thời điểm cụ thể** (gate hiện đang ở trạng thái NOT PASSED/IN_REVIEW theo `COMMIT_NOTES.md`). Theo đúng tinh thần "evidence bất biến" nêu trong `docs/evidence/tasks/README.md`, các hồ sơ evidence đã ghi nhận **không nên bị sửa để khớp đường dẫn mới** — nếu cần, nên thêm một ghi chú addendum trỏ sang cấu trúc mới thay vì chỉnh sửa hồ sơ lịch sử.
9. **`docs/evidence/tasks/0.0.1/README.md` … `0.0.5/README.md`** — mỗi tệp là con trỏ review theo chủ đề; nếu chứa đường dẫn tệp cụ thể, chúng sẽ cần cập nhật.
10. **`contracts/errors/error-catalog.md`** và `contracts/api/openapi.yaml`/schema JSON khác — các tệp trong `contracts/` sử dụng `$ref`/`$id` để giải quyết schema offline. Đây là lý do khuyến nghị **không di chuyển `contracts/`** trong đợt tái cấu trúc `docs/` này — trộn hai sáng kiến sẽ làm tăng đáng kể diện rủi ro và diện review.
11. **ADR-0014** ("Toolchain, repository topology, language policy và contract authority") — ADR này *đã* là quyết định có hiệu lực quy định về topology repo. Một tái cấu trúc `docs/` có thể bị xem là **xung đột với hoặc cần sửa đổi một ADR đã tồn tại** — về nguyên tắc cần một ADR mới (bổ sung/thay thế một phần ADR-0014, hoặc làm rõ ADR-0014 chỉ áp cho `src/`) trước khi thực hiện, chứ không thể coi đây là một thay đổi "chỉ đổi tên thư mục tài liệu".

**Kết luận quan trọng về quy trình:** Theo đúng quy tắc mà chính bộ tài liệu này đặt ra (`document-control.md` — kiểm soát vòng đời/versioning artifact; `raci.md` — ai được quyền phê duyệt thay đổi loại gì), **một cuộc tái cấu trúc cấu trúc thư mục tài liệu là một thay đổi mang tính thực chất/breaking (substantive/breaking change)** đối với toàn bộ nguồn sự thật của dự án — không phải một việc dọn dẹp vô hại. Nó đòi hỏi tối thiểu: (a) tăng version của `document-control.md` và các tài liệu index/traceability liên quan, (b) review theo đúng vai trò RACI phù hợp (nhiều khả năng Account Owner + Technical Operator, vì đây là thay đổi ảnh hưởng authority/toàn bộ pack), và (c) rất có thể một ADR riêng (bổ sung hoặc làm rõ phạm vi ADR-0014) trước khi thực thi — **không nên thực hiện như một commit dọn dẹp âm thầm.**

---

## 5. Khuyến nghị

Lộ trình triển khai an toàn, theo thứ tự ưu tiên rủi ro thấp → cao:

1. **Bước 1 — Đưa báo cáo phân loại này vào làm tài liệu tham chiếu bổ sung, không phá huỷ (non-destructive).** Đây chính là tệp bạn đang đọc (`docs/00-governance/documentation-layer-classification.md`), không di chuyển hay đổi tên bất kỳ tệp nào hiện có. Rủi ro gần như bằng không — không ảnh hưởng đường link, evidence, hay gate hiện tại — nhưng ngay lập tức tạo ra một bản đồ tra cứu Backend/Frontend/Shared/Governance dùng được cho review, onboarding và lập kế hoạch Phase 5.
2. **Bước 2 — Đưa ra RACI review cho chính đề xuất tái cấu trúc.** Trình bảng ánh xạ ở Mục 3 cho Account Owner/Technical Operator theo đúng cơ chế `raci.md`, xin ý kiến rõ ràng về việc có nên tách ADR registry (`README.md`) khỏi nội dung ADR (0001–0016) hay giữ nguyên `docs/adr/` làm một khối — đây là điểm thiết kế có thể gây tranh cãi nhất trong đề xuất.
3. **Bước 3 — Viết một ADR riêng cho việc tái cấu trúc** (ví dụ ADR-0017), nêu rõ quan hệ với ADR-0014 (bổ sung/làm rõ phạm vi, không mâu thuẫn), trước khi đụng tới bất kỳ tệp nào.
4. **Bước 4 — Thực thi dưới dạng một task-card duy nhất, có kiểm soát**, dùng `git mv` (giữ lịch sử/blame) theo đúng bảng ánh xạ đầy đủ ở Mục 3, kèm một lượt quét/sửa link Markdown tương đối tự động trên toàn bộ corpus, cập nhật `DOCS_INDEX.md`, `requirements-traceability.md`, và bảng vị trí chuẩn trong `document-control.md`; với các hồ sơ evidence/gate đã đóng băng (Phase 0.0), **thêm addendum thay vì sửa nội dung lịch sử**. Giữ nguyên `contracts/` — không gộp vào đợt di chuyển này.
5. **Bước 5 — Tận dụng cửa sổ rủi ro thấp hiện tại.** Gate Phase 0.0 hiện đang ở trạng thái **NOT PASSED / IN_REVIEW** (theo `gate-record.md` và `COMMIT_NOTES.md`) — nghĩa là toàn bộ bộ tài liệu chưa được baseline/approve chính thức. Đây là thời điểm **rẻ nhất** để tái cấu trúc vật lý (ít evidence bất biến bị ảnh hưởng, chưa có bên ngoài phụ thuộc đường dẫn cũ); nếu trì hoãn tới sau khi gate pass, chi phí sửa đổi các hồ sơ audit đã chốt sẽ cao hơn đáng kể.
6. Sau khi hoàn tất, chạy lại toàn bộ checklist Phase 0.0 (`review-checklist.md`) và re-validate task-card allowlist trước khi coi đợt tái cấu trúc là hoàn thành.

---

## 6. Addendum — Phân loại tệp bổ sung sau bản ghi 81 tệp (2026-08-02)

Sau bản ghi 81 tệp (Mục 1–3, đóng băng lịch sử tại 2026-07-31), corpus tài liệu đã tăng từ **81 lên 105 tệp** trong cùng phạm vi (`docs/`, root repo, `contracts/errors/error-catalog.md`): 22 tệp bổ sung tại đợt audit chéo 2026-08-02 và 2 validation record gate Phase 0.0 bổ sung cùng ngày (row 23–24). **Mục 1–3 là bản ghi lịch sử và không được sửa**. Phát hiện đáng chú ý: lớp **Frontend lần đầu khác 0** (8 tệp), do bộ tài liệu Frontend pack được khởi tạo làm input Phase 5/6 (chưa cho phép code).

### 6.1. Bảng phân loại 24 tệp bổ sung

| # | Tệp | Layer |
|---|---|---|
| 1 | docs/frontend/README.md | Frontend |
| 2 | docs/frontend/product/frontend-charter.md | Frontend |
| 3 | docs/frontend/product/screen-inventory.md | Frontend |
| 4 | docs/frontend/architecture/api-integration-contract.md | Frontend |
| 5 | docs/frontend/architecture/flutter-app-architecture.md | Frontend |
| 6 | docs/frontend/design/design-system.md | Frontend |
| 7 | docs/frontend/security/frontend-security-policy.md | Frontend |
| 8 | docs/frontend/engineering/frontend-testing-strategy.md | Frontend |
| 9 | docs/backend/engineering/logging-standard.md | Backend |
| 10 | docs/backend/engineering/versioning-release-policy.md | Backend |
| 11 | docs/backend/security-ops/runbooks/venue-rate-limit.md | Backend |
| 12 | docs/backend/security-ops/runbooks/outbox-dlq-backlog.md | Backend |
| 13 | docs/backend/security-ops/runbooks/clock-drift.md | Backend |
| 14 | docs/governance/waiver-register.md | Governance-Process |
| 15 | docs/governance/compliance-register.md | Governance-Process |
| 16 | docs/governance/templates/incident-record.md | Governance-Process |
| 17 | docs/governance/evidence/tasks/0.1/README.md | Governance-Process |
| 18 | docs/governance/documentation-layer-classification.md (tệp này — tự tham chiếu, không nằm trong danh sách 81 tệp gốc) | Governance-Process |
| 19 | README.md (root repo) | Governance-Process |
| 20 | AGENTS.md | Governance-Process |
| 21 | SECURITY.md | Governance-Process |
| 22 | CONTRIBUTING.md | Governance-Process |
| 23 | docs/governance/evidence/gates/phase-0.0/validation-2026-08-02.md (EV-GATE-0.0-2026-08-02-01) | Governance-Process |
| 24 | docs/governance/evidence/gates/phase-0.0/validation-2026-08-02-02.md (EV-GATE-0.0-2026-08-02-02 — record hiện hành sau đợt sửa audit toàn diện) | Governance-Process |

Ghi chú: các control phi-Markdown ở root repo (`CODEOWNERS`, `.editorconfig`, `.gitignore`) là repo control, không tính vào corpus tài liệu Markdown được phân loại.

### 6.2. Tổng hợp mới (105 tệp)

Bảng tóm tắt ở Mục 1 là bản ghi lịch sử tại thời điểm 81 tệp và không được sửa; tổng hợp hiện hành là:

| Layer | Số tệp (bản ghi 81) | Bổ sung | Số tệp (hiện hành 105) |
|---|---|---|---|
| Backend | 57 | +5 | 62 |
| Governance-Process | 22 | +11 | 33 |
| Shared-CrossCutting | 2 | 0 | 2 |
| Frontend | 0 | +8 | 8 |
| **Tổng** | **81** | **+24** | **105** |

### 6.3. Đính chính bản ghi v0.2.0

- `COMMIT_NOTES.md` được **giữ ở gốc repo**: tuỳ chọn nêu tại row 80 của bảng ánh xạ Mục 3 ("có thể giữ ở gốc repo — xem Mục 4") đã được chọn; tệp **không** được di chuyển vào `docs/governance/`.
- Con số "80 tệp `git mv`" trong changelog v0.2.0 thực tế là **79**: 81 tệp trừ `contracts/errors/error-catalog.md` (row 81 — không đổi chỗ) và `COMMIT_NOTES.md` (row 80 — giữ ở gốc repo).

---

## 7. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.4.0 | 2026-08-02 | Audit toàn diện đợt 2: addendum §6 cập nhật corpus 103 → 105 tệp (row 23–24: hai validation record gate Phase 0.0 ngày 2026-08-02); thêm khối "Ghi nhận khoảng trống governance" — thực thi tái cấu trúc trước khi có approval record hợp lệ theo GOV-DOC-001 §4 được theo dõi tại RAID I-009 và phải được hợp thức hóa trong quyết định ký gate Phase 0.0; thêm row Change summary vào header. | Technical Operator | Pending |
| 0.3.0 | 2026-08-02 | Thêm Mục 6 (Addendum): phân loại 22 tệp bổ sung sau bản ghi 81 tệp — corpus tăng lên 103 tệp (Backend 62, Governance-Process 31, Shared 2, Frontend 8 — lần đầu khác 0); đính chính v0.2.0 (COMMIT_NOTES.md giữ ở gốc repo; số tệp `git mv` thực tế là 79, không phải 80). Mục 1–3 lịch sử không đổi; changelog được đánh số lại thành Mục 7. | Technical Operator | Pending |
| 0.2.0 | 2026-07-31 | **Thực thi** di chuyển vật lý theo đúng bảng ánh xạ ở Mục 3, theo yêu cầu trực tiếp của Account Owner (bỏ qua lộ trình RACI/ADR-0017 khuyến nghị ở Mục 5). 80 tệp `git mv` sang docs/{governance,shared,backend,frontend}/; docs/frontend/README.md placeholder được tạo; toàn bộ link tương đối, DOCS_INDEX.md, document-control.md §6, requirements-traceability.md, master spec §1.5/§4.6 và 7 task-card YAML (`tasks/active/*.yaml`) được cập nhật theo đường dẫn mới trong cùng thay đổi. Hồ sơ evidence Phase 0.0 đã đóng băng chỉ được sửa link, không sửa nội dung/quyết định evidence. | Technical Operator | Pending |
| 0.1.0 | 2026-07-31 | Tạo bản phân loại Backend/Frontend/Shared/Governance đầu tiên cho toàn bộ 81 tệp tài liệu Phase 0.0 và `AI_AUTO_TRADE_MASTER_SPEC.md`; đề xuất cấu trúc Enterprise-Grade mục tiêu (chưa thực thi vật lý). | Technical Operator | Pending |
