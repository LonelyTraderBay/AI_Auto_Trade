# Product Charter — AI Auto Trade

| Thuộc tính | Giá trị |
|---|---|
| Document ID | PRD-CHARTER-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §1.2, §2, §8–§12 và §14 |
| Related requirements | FR-MKT-001, FR-STR-001, FR-EXEC-001, FR-LED-001, FR-REC-001, FR-RSK-001, FR-OPS-001; NFR-DET-001, NFR-AUD-001, NFR-SAFE-001, NFR-SEC-001, NFR-OPS-001 |
| Related ADR | ADR-0001, ADR-0002, ADR-0003, ADR-0004, ADR-0005, ADR-0007, ADR-0011, ADR-0012, ADR-0014 |

> Đây là charter sản phẩm/kỹ thuật cho MVP. Nó không là lời khuyên đầu tư, không hứa hẹn lợi nhuận và không phê duyệt giao dịch vốn thật.

## 1. Tầm nhìn

Xây một nền tảng giao dịch tự động có phạm vi nhỏ nhưng có thể kiểm thử, audit, phục hồi và mở rộng có kiểm soát. Hệ thống ưu tiên safety, determinism và khả năng đối soát hơn PnL, tốc độ tối đa hoặc số lượng tích hợp.

Vertical slice mục tiêu:

~~~text
market event
  -> strategy mẫu
  -> deterministic risk
  -> simulated/testnet execution
  -> order/fill event
  -> double-entry ledger
  -> reconciliation
  -> audit, replay và alert
~~~

## 2. Vấn đề cần giải quyết

Một bot giao dịch không chỉ cần sinh signal. Nó phải chứng minh được:

- cùng input tạo cùng decision trong replay/backtest;
- mỗi lệnh truy ngược được market data, strategy, risk, order, fill và ledger;
- crash, timeout hoặc reconnect không tạo duplicate order;
- khi state nội bộ khác venue, hệ thống phát hiện, block scope ảnh hưởng và đối soát;
- credential, AI, UI và operator action không tạo đường bypass execution/risk/audit.

## 3. Mục tiêu sản phẩm

| Mục tiêu | Outcome có thể kiểm tra | Requirement chính |
|---|---|---|
| Market data đáng tin cậy | Normalized event có lineage, timestamp/quality flag và dataset manifest. | FR-MKT-001, NFR-DET-001 |
| Strategy portable | Một strategy contract chạy được ở replay/backtest/paper/testnet theo mode hợp lệ. | FR-STR-001 |
| Execution an toàn | OrderIntent đi qua risk, idempotency, OMS và xử lý unknown outcome. | FR-EXEC-001, NFR-SAFE-001 |
| Accounting/audit | Fill/fee tạo ledger cân bằng và decision chain có thể truy vết. | FR-LED-001, NFR-AUD-001 |
| Recovery/reconciliation | Restart, unknown order và mismatch có safe-state/evidence. | FR-REC-001, NFR-OPS-001 |
| Operational control | API/CLI có authorization/audit, không có manual order endpoint trong MVP. | FR-OPS-001, NFR-SEC-001 |

## 4. Phạm vi MVP

MVP chỉ bao gồm:

- một venue crypto spot;
- một account;
- một hoặc vài instrument được Account Owner phê duyệt;
- một strategy mẫu, mục tiêu kiểm chứng platform chứ không tối ưu alpha;
- backtest, replay, PAPER_SIMULATOR, TESTNET và SHADOW trước canary;
- modular monolith do một người phát triển/vận hành, với ranh giới context rõ;
- API/CLI control plane trước dashboard.

Không có live trade hoặc canary vì Charter còn DRAFT/IN_REVIEW hay do code chạy được. Các gate và owner decision tại master vẫn bắt buộc.

## 5. Ngoài phạm vi hiện tại

- HFT, colocation, tối ưu sub-millisecond.
- Futures, margin, leverage, short selling, multi-leg arbitrage.
- Multi-venue, multi-account, MT5, Interactive Brokers.
- Kafka, NATS, Redis, Kubernetes, microservice hoặc database/language mới.
- Flutter dashboard trước Phase 5.
- LLM-generated execution, self-learning, tự promote model/strategy/config lên live.
- Withdrawal, transfer tự động, tax engine.

Mở rộng phạm vi chỉ theo Master §2.4: ADR, capability/adapter contract test, risk policy/runbook và gate paper/testnet riêng.

## 6. Stakeholder và nhu cầu

| Stakeholder / role | Nhu cầu | Quyết định không thuộc role này |
|---|---|---|
| Account Owner | Scope, capital, venue/account/instrument, legal/terms và canary approval có evidence. | Override safety invariant hoặc regulatory constraint. |
| Technical Operator | Artifact rõ, task nhỏ, contract-first, CI/recovery evidence. | Tự quyết risk cap/live scope. |
| Risk Approver | Policy bất biến có version, risk decision/review/kill-switch có audit. | Bypass risk để cứu lệnh. |
| Security/Backup Owner | Credential isolation, machine identity, backup/restore, network/secrets policy. | Cho AI/UI quyền venue trade. |
| Viewer / operator | Read model trung thực, incident/reconciliation visibility và command có quyền rõ. | Direct DB/venue control bypass. |
| AI Coding Agent | Requirement, ADR, contract, allowed path và acceptance command rõ ràng. | Suy diễn logic chưa có authority hoặc deploy/live action. |

## 7. Cách đo thành công

Các chỉ số chấp nhận đầu tiên là kỹ thuật/vận hành:

1. Replay/backtest tái lập cùng event/decision/ledger result khi code, config, data và seed không đổi.
2. Audit chain liên kết market event đến risk decision, order, fill và journal/posting.
3. Unknown submit outcome không gây blind retry hay duplicate order.
4. Reconciliation phát hiện mismatch và đưa runtime/scope về safe state theo policy.
5. Paper/testnet/shadow có evidence theo gate trước bất kỳ canary scope nào.
6. Credential least privilege, redaction và authorization được chứng minh bằng policy/test/evidence.

PnL, alpha, win rate hoặc số lượng trade không phải exit criteria Phase 0–3 và không được dùng thay thế safety evidence.

## 8. Nguyên tắc sản phẩm không thể thương lượng

- Fail closed khi market/reference/portfolio/runtime state không đáng tin cậy.
- Không có direct UI/LLM-to-exchange path.
- Risk approval thủ công không bypass fresh risk evaluation.
- No blind retry khi external outcome unknown.
- Ledger/audit/event bắt buộc append-only theo chính sách domain.
- Public contract versioned; breaking change cần version/migration/compatibility evidence.
- Không có live credential trong local/CI/fixture; trade key không có withdrawal permission.

## 9. Lộ trình giá trị

| Phase | Value được chứng minh | Không được suy ra |
|---|---|---|
| 0.0 | Documents, ADR, contract skeleton và delivery controls được review. | Không có application/DB/runtime approval. |
| 0 | Repository guardrails, local skeleton, CI và contract validation. | Không có venue/LLM integration. |
| 1 | Fake venue chứng minh OMS/risk/ledger/recovery safety. | Không có live venue safety proof. |
| 2 | Catalog, replay, backtest và paper simulator có determinism evidence. | Không có alpha/live approval. |
| 3 | Một venue public/read-only/testnet/shadow theo capability contract. | Không có live trade credential/canary approval. |
| 4 | Canary vốn cực nhỏ, scope/cap được owner ký. | Không tự động cho phép full live hoặc scale capital. |
| 5–6 | Control-plane UX rồi controlled AI/memory off hot path. | Không có auto-promote/autonomous live trading. |

## 10. Assumption và open decision

Các assumption/blocker được quản lý tại GOV-RAID-001 và Open Decision Register của master. Các quyết định sau không được suy đoán:

- venue/testnet, jurisdiction, account/sub-account, instrument universe;
- data retention/legal applicability;
- auth provider/session model;
- canary capital/risk hard caps/shutdown policy;
- alert channel, backup location và live topology.

## 11. Tiêu chí review charter

Charter chỉ có thể chuyển APPROVED khi:

- scope và exclusions nhất quán với master;
- baseline FR/NFR/SEC có traceability;
- stakeholder/accountability được RACI xác nhận;
- open decision/dependency được RAID ghi nhận;
- approver ghi rõ scope, version và ngày hiệu lực.

## 12. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | Tạo product charter MVP từ master v2.0. | Technical Operator | Pending |
