# Ma trận traceability yêu cầu

| Thuộc tính | Giá trị |
|---|---|
| Document ID | GOV-TRACE-001 |
| Phiên bản | 0.5.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-08-02 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §1.5, §2.2, §5–§13, §14 và §15 |
| Related requirements | Toàn bộ FR/NFR/SEC trong registry bên dưới |
| Related ADR | ADR-0001 đến ADR-0016 theo phạm vi/deadline |
| Change summary | 0.5.0 (2026-08-02): sửa quy ước TASK/GATE ID khớp thực tế; đăng ký SEC-GOV-001/SEC-KEY-001; trỏ authority SEC-* về PRD-NFR-001 §8.1. |

> Đây là registry traceability, không phải implementation plan. Trong Phase 0.0, cột module/test/contract nêu target dự kiến; không có mục nào ở đây cho phép tạo code, DDL hoặc endpoint khi chưa có task card và artifact APPROVED.

## 1. Quy ước trace

Mỗi feature phải đi theo chuỗi:

~~~text
Requirement -> ADR -> contract/schema -> owned context/module
            -> test/evidence -> task -> gate record
~~~

ID phải ổn định:

- FR-<DOMAIN>-<NNN>: functional requirement.
- NFR-<DOMAIN>-<NNN>: non-functional requirement.
- SEC-<DOMAIN>-<NNN>: security/control requirement (định nghĩa canonical tại PRD-NFR-001 §8.1; bảng §4 dưới đây là registry tham chiếu).
- ADR-NNNN: decision record (file `docs/backend/adr/NNNN-<slug>.md`).
- Task ID dạng `<phase>.<n>` (ví dụ `0.0.6`, `0.1`) theo Master Phụ lục C.3; authority là `tasks/active|completed/<task_id>-<slug>.yaml`.
- `GATE-<PHASE>-<NNN>` (ví dụ `GATE-0.0-001`): gate record theo template TMP-GATE-001.

Trạng thái artifact được tham chiếu phải được kiểm ở DOCS_INDEX/gate record. Không diễn giải một link DRAFT như approval.

## 2. Functional requirement registry

| ID | Tóm tắt chuẩn | Priority | Planned phase | Primary context | Nguồn chi tiết |
|---|---|---|---|---|---|
| FR-MKT-001 | Chuẩn hóa market data, lưu lineage/history và kiểm tra chất lượng dữ liệu. | MVP | 2 | market_data, reference | docs/backend/product/functional-requirements.md |
| FR-STR-001 | Chạy strategy cùng contract ở backtest, replay, paper và testnet/canary theo scope. | MVP | 2 | strategy, research | docs/backend/product/functional-requirements.md |
| FR-EXEC-001 | Tạo OrderIntent, risk gate, submit/cancel, xử lý fill/fee và outcome không rõ. | MVP | 1 | execution, risk | docs/backend/product/functional-requirements.md |
| FR-LED-001 | Lưu double-entry ledger, position, balance và PnL có thể đối soát. | MVP | 1 | portfolio_ledger | docs/backend/product/functional-requirements.md |
| FR-REC-001 | Khôi phục crash, xử lý unknown order và không gửi lệnh trùng. | MVP | 1 | execution, operations, platform | docs/backend/product/functional-requirements.md |
| FR-RSK-001 | Áp dụng risk, reservation và kill switch theo hierarchy scope. | MVP | 1 | risk, operations | docs/backend/product/functional-requirements.md |
| FR-OPS-001 | Cung cấp API/CLI cho vận hành, audit, reconciliation và deployment. | MVP | 0–3 | operations, platform | docs/backend/product/functional-requirements.md |
| FR-AI-001 | User quản lý BYOK connection, chọn provider/model đã duyệt; AI chỉ proposal/memory an toàn. | Deferred | 6 | operations, ai_memory | docs/backend/product/functional-requirements.md |

### 2a. Frontend functional requirements (Phase 5/6 — DRAFT)

Các FR-FE dưới đây là input Phase 5/6 từ Frontend pack; không mục nào cho phép tạo frontend code trước gate Phase 5.

| ID | Tóm tắt chuẩn | Priority | Planned phase | Primary context | Nguồn chi tiết |
|---|---|---|---|---|---|
| FR-FE-001 | Hiển thị runtime/mode/health thật, cache có nhãn stale. | Deferred | 5 | frontend | docs/frontend/product/frontend-charter.md |
| FR-FE-002 | Order/position/PnL/fill views (16 OMS states, DecimalString). | Deferred | 5 | frontend | docs/frontend/product/frontend-charter.md |
| FR-FE-003 | Incident/reconciliation/audit views. | Deferred | 5 | frontend | docs/frontend/product/frontend-charter.md |
| FR-FE-004 | Command submission theo quyền + async 202/polling + idempotency. | Deferred | 5 | frontend | docs/frontend/product/frontend-charter.md |
| FR-FE-005 | Dangerous-action re-auth flow + reason + audit. | Deferred | 5 | frontend | docs/frontend/product/frontend-charter.md |
| FR-FE-006 | Mandatory ops views trước testnet (OPS-001 §4.2). | Deferred | 5 | frontend | docs/frontend/product/frontend-charter.md |
| FR-FE-007 | BYOK connection management UI (write-only key, 10 status). | Deferred | 6 | frontend | docs/frontend/product/frontend-charter.md |

## 3. Non-functional requirement registry

| ID | Tóm tắt chuẩn | Planned phase | Nguồn chi tiết |
|---|---|---|---|
| NFR-DET-001 | Cùng code/config/data/seed cho cùng result trong replay/backtest. | 1–2 | docs/shared/product/non-functional-requirements.md |
| NFR-AUD-001 | Truy vết decision market event → risk → order → fill → ledger. | 1 | docs/shared/product/non-functional-requirements.md |
| NFR-SAFE-001 | Không duplicate order/risk bypass/ledger imbalance; fail closed khi state không tin cậy. | 1 | docs/shared/product/non-functional-requirements.md |
| NFR-SEC-001 | Least privilege credential; AI/UI không có đường đặt lệnh trực tiếp. | 0–3 | docs/shared/product/non-functional-requirements.md |
| NFR-OPS-001 | Health, alert, restore/reconciliation và runbook có evidence. | 0–3 | docs/shared/product/non-functional-requirements.md |
| NFR-AI-001 | AI đa provider có egress/budget/failure isolation; không provider bắt buộc và không ảnh hưởng trading hot path. | 6 | docs/shared/product/non-functional-requirements.md |

## 4. Security/control requirement registry

| ID | Tóm tắt chuẩn | Planned phase | Source |
|---|---|---|---|
| SEC-CRED-001 | Credential tách theo environment/account, trade key không withdrawal và không xuất hiện trong code/log/UI/AI worker. | 0–3 | Master §6.1, §12.1 |
| SEC-AUTH-001 | Trước external venue, control API xác thực actor, phân quyền action, rate limit và audit command nguy hiểm; machine identity riêng. | 3 | Master §11.3 |
| SEC-AUD-001 | Audit/event/ledger evidence append-only, traceable và redacted; approval có actor/role/time/version. | 0–1 | Master §1.5, §7.8, §11.3 |
| SEC-SUP-001 | Dependency/image/artifact được pin, scan, kiểm checksum/SBOM theo phase; không dùng dependency tự phát. | 0–4 | Master §12.2, §13 |
| SEC-DATA-001 | Dữ liệu nhạy cảm, backup và fixture được phân loại/redact/encrypt theo policy; retention có decision trước Phase 2. | 0–2 | Master §7.11–§7.12, §12.2 |
| SEC-GOV-001 | Thay đổi artifact/task/gate tuân theo document-control lifecycle; approval có actor/role/UTC/evidence; task card YAML là authority scope; không tự chuyển APPROVED. | 0.0–0 | Master §1.6, §13.2, §14.2; PRD-NFR-001 §8.1 |
| SEC-KEY-001 | Secret/key theo secrets-and-key-management policy: không secret trong repo/log/fixture/evidence; enrollment/rotation/revocation có procedure/runbook; secret provider được approve trước khi enrollment. | 0–3 | Master §12.1; PRD-NFR-001 §8.1 |
| SEC-AI-001 | AI worker proposal-only, sanitized input, no execution tool/trade credential/config promotion. | 6 | Master §10.6–§10.8, §12.1 |
| SEC-AI-002 | BYOK key chỉ qua secret ingress write-only; không read-back, không log/persist/echo và tách theo owner/provider/environment. | 6 | Master §10.6, §12.1; ADR-0016 |
| SEC-AI-003 | Provider/model/endpoint egress allowlist, data classification, budget/quota/fallback và owner-scope isolation được enforce/audit. | 6 | Master §10.6, §12.4–§12.6; ADR-0016 |

## 5. Mapping baseline đến decision, contract và evidence

Các đường dẫn contract có thể chưa tồn tại trong Phase 0.0; trạng thái của chúng phải được cập nhật khi artifact được tạo. Planned context không phải permission để tạo source module trước Phase 0.

| Requirement | ADR tối thiểu | Planned contract/artifact | Planned context/test | Gate evidence |
|---|---|---|---|---|
| FR-MKT-001 | ADR-0003, ADR-0004, ADR-0013 | market-data event schema, dataset manifest, data dictionary | market_data/reference; contract, quality, replay test | Phase 2 data/replay gate |
| FR-STR-001 | ADR-0001, ADR-0002, ADR-0006 khi áp dụng | strategy action/config schema, checkpoint contract | strategy/research; unit, replay, golden test | Phase 2 strategy gate |
| FR-EXEC-001 | ADR-0005, ADR-0007, ADR-0012 | OrderIntent/event schemas, OMS policy, venue capability contract | execution/risk; state-machine, contract, chaos test | Phase 1 core-safety and Phase 3 venue gate |
| FR-LED-001 | ADR-0003, ADR-0011, ADR-0012 | journal/posting schema, accounting policy, dictionary | portfolio_ledger; property, rebuild, integration test | Phase 1 core-safety gate |
| FR-REC-001 | ADR-0004, ADR-0005, ADR-0012 | reconciliation command/event schema, runbook | execution/operations/platform; recovery, chaos, integration test | Phase 1 and Phase 3 gate |
| FR-RSK-001 | ADR-0007, ADR-0012 | risk policy/config schema, RiskDecision event, kill-switch command | risk/operations; property, decision, state-machine test | Phase 1 core-safety gate |
| FR-OPS-001 | ADR-0002, ADR-0014, ADR-0015 when Phase 3 | OpenAPI, command schema, error catalog, task/gate template | operations/platform; API contract, authorization, CLI test | Phase 0 then Phase 3 gate |
| FR-AI-001 | ADR-0008, ADR-0015, ADR-0016 | AI provider catalog/connection, endpoint/egress/usage/policy-profile contracts, isolated secret-enrollment OpenAPI, lifecycle command/event, error catalog | operations/ai_memory/adapters; contract, authorization, redaction, capability/rotation test | Phase 6 AI/BYOK gate |
| NFR-DET-001 | ADR-0001, ADR-0002, ADR-0014 | config/deployment/dataset/checkpoint manifests | all applicable; replay/golden test | Phase 2 gate |
| NFR-AUD-001 | ADR-0004, ADR-0005, ADR-0011 | event envelope, audit/journal schema, trace field standard | execution/risk/ledger; rebuild/audit-chain test | Phase 1 gate |
| NFR-SAFE-001 | ADR-0005, ADR-0007, ADR-0011, ADR-0012 | OMS/risk/accounting/concurrency policies | risk/execution/ledger; property, chaos, reconciliation test | Phase 1 and Phase 4 gate |
| NFR-SEC-001 | ADR-0014, ADR-0015, ADR-0008 when Phase 6 | access matrix, secrets policy, auth session policy | operations/adapters/ai_memory; security/authorization test | Phase 0.0, Phase 3 and Phase 6 gate |
| NFR-OPS-001 | ADR-0012, ADR-0013, ADR-0015 when Phase 3 | runbook index, SLO/alert policy, backup policy | operations/platform; drill, restore, health test | Phase 0.0 through Phase 3 gate |
| NFR-AI-001 | ADR-0008, ADR-0016 | provider catalog/profile, endpoint/egress/usage policy, AI observability | ai_memory/adapters/operations; budget, outage, no-fallback/egress-bypass test | Phase 6 AI/BYOK gate |
| SEC-CRED-001 | ADR-0014, ADR-0015 | secret/key policy, deployment manifest schema | adapters/operations; secret scan, deployment review | Phase 0, Phase 3/4 gate |
| SEC-AUTH-001 | ADR-0015 | OpenAPI security scheme, authorization matrix | control_api/operations; authorization/re-auth test | Phase 3 gate |
| SEC-AUD-001 | ADR-0004, ADR-0011, ADR-0012 | audit envelope, gate/task evidence templates | platform/ledger/operations; append-only and trace test | Phase 0.0 and Phase 1 gate |
| SEC-SUP-001 | ADR-0014 | lockfile/image/SBOM evidence policy | CI/build; scan and reproducibility check | Phase 0 and Phase 4 gate |
| SEC-DATA-001 | ADR-0013 | classification/retention matrix, backup policy | market_data/research/operations; restore/redaction test | Phase 2 gate |
| SEC-GOV-001 | ADR-0014 | document-control (GOV-DOC-001), task-card schema, gate-record template | governance/CI; task-card validation, gate record review | Phase 0.0 gate |
| SEC-KEY-001 | ADR-0015, ADR-0016 khi Phase 6 | secrets-and-key-management policy (SEC-004), RB-007/RB-008 | operations/security-ops; secret scan, rotation/restore drill | Phase 0.0, Phase 3 gate |
| SEC-AI-001 | ADR-0008, ADR-0016 | LLM provider/proposal/memory schema | ai_memory; contract, negative-security test | Phase 6 gate |
| SEC-AI-002 | ADR-0016 | isolated secret-ingress contract, connection metadata schema, key lifecycle/rotation policy | operations/ai_memory; no-hash/no-read-back, secret-leak and owner-scope negative test | Phase 6 AI/BYOK gate |
| SEC-AI-003 | ADR-0016 | catalog/endpoint/egress/usage/policy profile, provider error catalog | adapters/operations; egress/DNS/redirect, quota, drift, outage/no-fallback test | Phase 6 AI/BYOK gate |
| FR-FE-001..007 | ADR-0015 (pending) | contracts/api/openapi.yaml + FE-API-001 | frontend client; contract/authorization/re-auth test | Phase 5/6 gate |

## 6. Completion rules

Một requirement chỉ có thể được đánh dấu implemented khi tất cả điều kiện sau có evidence:

- requirement status và acceptance criteria được xác nhận;
- ADR applicable là APPROVED;
- contract/schema có version và compatibility rule;
- module/context owner và task card được link;
- test bao phủ success, failure và invariant phù hợp;
- gate record ghi command, result, artifact hash/path và approver;
- open risk/waiver còn lại được nêu rõ; safety invariant không có waiver.

Khi breaking change xảy ra, tạo version/supersession và cập nhật toàn bộ inbound/outbound link; không thay đổi ID/meaning của requirement đã được implementation sử dụng.

## 7. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.5.0 | 2026-08-02 | Audit toàn diện: sửa quy ước §1 cho khớp artifact thực tế (task_id `<phase>.<n>` theo Phụ lục C.3 thay TASK-x; `GATE-<PHASE>-<NNN>` thay GATE-Px); đăng ký SEC-GOV-001, SEC-KEY-001 (trước đây dangling trong task card 0.0.1/0.0.4/0.0.5) kèm mapping §5; ghi rõ PRD-NFR-001 §8.1 là requirement authority của SEC-*, §4 chỉ là registry. | Technical Operator | Pending |
| 0.4.0 | 2026-08-02 | Thêm §2a Frontend functional requirements FR-FE-001..007 (Phase 5/6 — DRAFT, nguồn Frontend charter) và mapping row FR-FE-001..007 vào §5 (ADR-0015 pending, openapi.yaml + FE-API-001, Phase 5/6 gate). | Technical Operator | Pending |
| 0.3.0 | 2026-07-31 | Cập nhật "Nguồn chi tiết" theo tái cấu trúc docs/ sang lớp Backend/Frontend/Shared/Governance (GOV-CLASS-001): FR trỏ docs/backend/product/, NFR trỏ docs/shared/product/. | Technical Operator | Pending |
| 0.2.0 | 2026-07-31 | Thêm trace BYOK đa provider: FR/NFR/SEC AI, ADR-0016 và Phase 6 evidence chain. | Technical Operator | Pending |
| 0.1.0 | 2026-07-31 | Khởi tạo registry FR/NFR/SEC và planned trace chain cho Phase 0.0. | Technical Operator | Pending |
