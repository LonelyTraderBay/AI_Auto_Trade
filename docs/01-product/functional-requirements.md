# Functional Requirements — MVP

| Thuộc tính | Giá trị |
|---|---|
| Document ID | PRD-FR-001 |
| Phiên bản | 0.1.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §2.2, §5, §8–§11 và §14 |
| Related requirements | FR-MKT-001, FR-STR-001, FR-EXEC-001, FR-LED-001, FR-REC-001, FR-RSK-001, FR-OPS-001 |
| Related ADR | ADR-0001–0005, ADR-0007, ADR-0011, ADR-0012, ADR-0014; phase-dependent ADR khác theo GOV-TRACE-001 |

> Mỗi requirement bên dưới còn DRAFT/IN_REVIEW cho tới khi approver xác nhận. Implementation chỉ dùng requirement đã có task card, ADR/contract applicable APPROVED và gate cho phép.

## 1. Quy ước

- Priority MVP nghĩa là phải có trong vertical slice, không có nghĩa phải làm ở Phase 0.
- MUST là điều kiện nghiệm thu; SHOULD cần ADR/waiver hợp lệ nếu không theo.
- Contract/schema/field name cụ thể phải được chuẩn hóa trong artifact machine-readable; prose này không thay thế chúng.
- Mọi acceptance evidence phải link requirement ID, task, command/procedure, result và gate record.

## 2. Bảng tóm tắt

| ID | Requirement | Priority | Planned phase | Context chính |
|---|---|---|---|---|
| FR-MKT-001 | Market data normalization, lineage, history và quality. | MVP | 2 | market_data, reference |
| FR-STR-001 | Strategy contract nhất quán giữa backtest/replay/paper/testnet/canary. | MVP | 2 | strategy, research |
| FR-EXEC-001 | Intent-to-order lifecycle qua risk, execution, fill/fee và unknown outcome. | MVP | 1 | execution, risk |
| FR-LED-001 | Double-entry ledger, balance/position/PnL projection và reconciliation. | MVP | 1 | portfolio_ledger |
| FR-REC-001 | Crash recovery, unknown order handling và reconciliation. | MVP | 1 | execution, operations, platform |
| FR-RSK-001 | Pre-trade risk, reservation, manual approval và kill-switch hierarchy. | MVP | 1 | risk, operations |
| FR-OPS-001 | API/CLI control plane cho vận hành, audit, reconciliation và deployment. | MVP | 0–3 | operations, platform |

## 3. FR-MKT-001 — Market data chuẩn hóa, lineage và quality

**Mô tả:** Hệ thống MUST nhận dữ liệu thị trường theo adapter, chuẩn hóa về canonical market event, lưu lineage/history phù hợp và đánh giá chất lượng trước khi dùng cho strategy/risk.

**Scope và acceptance criteria:**

- Event normalized có event_id, schema_version, venue, instrument_id, occurred_at, received_at, processed_at, recorded_at, source sequence/trade ID khi venue cung cấp, price/quantity/side phù hợp, quality flags và correlation metadata.
- Instrument/reference version có canonical symbol, base/quote asset, tick/lot/min/max/min-notional/precision, trading status, effective/valid time và source checksum/adapter version.
- Feed gap, duplicate, late/out-of-order hoặc stale condition được phân loại và tạo signal/alert theo policy; dữ liệu không tin cậy không được làm input risk/strategy trái policy.
- Dataset/history có manifest/version/checksum và point-in-time lineage để replay/backtest.
- Test fixture redacted và immutable; quality/no-look-ahead/replay evidence được lưu theo task/gate.

**Dependencies:** ADR-0003, ADR-0004, ADR-0013 trước Phase 2; market-data event/schema, data dictionary/dataset manifest; NFR-DET-001, NFR-AUD-001, NFR-SAFE-001, SEC-DATA-001.

## 4. FR-STR-001 — Strategy contract đa mode

**Mô tả:** Strategy MUST chỉ nhận canonical event/state/context và trả domain action; cùng strategy code/contract phải hoạt động ở backtest, replay, paper simulator và venue mode hợp lệ.

**Scope và acceptance criteria:**

- Public strategy lifecycle gồm on_start, on_market_event, on_order_event và snapshot theo canonical contract do schema/port xác định.
- Action chỉ thuộc danh sách được master cho phép: ProposeOrderIntent, CancelIntent, UpdateTarget, EmitSignal, ScheduleTimer và NoAction.
- Strategy không đọc file/env/database/network, không import adapter/venue SDK, không dùng wall clock/global random và không bypass risk/execution.
- Strategy version có code SHA, artifact/dependency-lock hash, config schema, feature contract và metadata creator.
- Checkpoint có version/checksum, last processed event/offset, watermark, config/feature hash và restore compatibility; runtime validate trước enable.
- Golden/replay test chứng minh deterministic result với data/config/seed pin; simulator version hóa fee/slippage/latency/partial fill/rejection model.

**Dependencies:** ADR-0001, ADR-0002, ADR-0006 nếu NautilusTrader được xét; strategy/config/checkpoint contract; NFR-DET-001, NFR-SAFE-001, SEC-SUP-001.

## 5. FR-EXEC-001 — Order lifecycle an toàn

**Mô tả:** Hệ thống MUST biến ProposedOrderIntent thành OrderIntent có canonical identity, đưa qua risk gate, quản lý OMS, submit/cancel theo capability và xử lý fill/fee/outcome unknown không gây duplicate order.

**Scope và acceptance criteria:**

- Strategy chỉ tạo ProposedOrderIntent. Execution application validate/canonicalize, tạo OrderIntentId và đúng một ClientOrderId trước risk; ClientOrderId không reuse trong cùng venue/account.
- Chỉ execution context được gửi order; risk chỉ tạo RiskDecision; unsupported venue capability bị reject rõ, không fallback âm thầm.
- OMS thực thi state/guard/side effect chuẩn từ CREATED qua risk/submission đến terminal/reconciliation; terminal state không quay về non-terminal state.
- Submit protocol persist risk decision, reservation, order state, submission queue và outbox cùng transaction; attempt/client_order_id/request hash được persist trước external request.
- Timeout/disconnect sau submit chuyển UNKNOWN, không blind retry; reconciliation dùng client_order_id/history/open order/fill evidence.
- Fill và fee được persist immutable; fill-before-ack và late venue evidence được xử lý bằng canonical state/terminal-correction procedure.
- Direct venue replace không thuộc MVP; replace là cancel intent rồi OrderIntent mới với ClientOrderId mới.

**Dependencies:** ADR-0005, ADR-0007, ADR-0012; OrderIntent/OMS/event/capability contract; NFR-AUD-001, NFR-SAFE-001, SEC-AUD-001.

## 6. FR-LED-001 — Ledger và projection tài chính

**Mô tả:** Hệ thống MUST lưu internal accounting truth bằng double-entry ledger, derive balance/position/PnL projection có thể rebuild và đối soát với external state mà không ghi đè lịch sử.

**Scope và acceptance criteria:**

- Mọi fill, fee và event accounting nằm trong scope tạo journal entry/posting cân bằng theo policy đã version hóa.
- Journal entry/posting immutable; duplicate fill/event không được book lần hai; projection có thể rebuild.
- Adjustment chỉ được dùng khi không thể reconstruct original event, phải có evidence/approval; không overwrite history để khớp venue.
- Decimal domain và NUMERIC(38,18) database; API/wire serialize number tài chính dạng string; rounding/cost basis/fee/valuation phải do accounting policy chỉ định.
- Integration/property tests chứng minh balance invariant, duplicate protection và rebuild result.

**Dependencies:** ADR-0003, ADR-0011, ADR-0012; accounting policy, journal/posting schema và dictionary; NFR-AUD-001, NFR-SAFE-001, SEC-AUD-001.

## 7. FR-REC-001 — Recovery và reconciliation

**Mô tả:** Hệ thống MUST khôi phục an toàn sau crash/mất kết nối, phát hiện state unknown hoặc mismatch và block exposure mới trong scope bị ảnh hưởng cho tới khi có evidence giải quyết.

**Scope và acceptance criteria:**

- Startup đi qua lease/config/local-state/venue/reconciliation/market-health readiness sequence trước enable strategy.
- Chỉ một execution leader trên mỗi venue/account; lease có TTL, heartbeat, fencing token tăng đơn điệu; mất lease dừng claim/send lệnh mới.
- Reconciliation chạy startup, định kỳ, sau stream gap/disconnect, unknown order và khi operator request.
- So sánh balance, position, open order, recent fill, fee và order state; mismatch tạo case với internal/external snapshot, time window, tolerance, adapter version và actor.
- State case có CLEAN, DETECTED, INVESTIGATING, BLOCKED, RESOLVED và APPROVED_ADJUSTMENT semantics; BLOCKED ngăn exposure mới trong scope.
- Unknown/Lost order chỉ được resolve bởi venue evidence hoặc approved external procedure; không resubmit old order.
- Chaos/recovery evidence bao gồm restart, disconnect, stale feed, DB failure, credential failure và kill switch theo phase.

**Dependencies:** ADR-0004, ADR-0005, ADR-0012; reconciliation command/event/runbook; NFR-SAFE-001, NFR-OPS-001, SEC-AUD-001.

## 8. FR-RSK-001 — Risk, reservation và kill switch

**Mô tả:** Hệ thống MUST thực thi deterministic pre-trade risk trước execution, reserve exposure/balance, hỗ trợ manual approval không bypass risk và kill switch theo hierarchy scope.

**Scope và acceptance criteria:**

- Risk input có immutable intent, policy version, portfolio/reference/market snapshot, reservation state, runtime health và injected time.
- Checks tối thiểu gồm enablement, kill switch, approval/deployment, freshness, instrument constraint, price sanity, balance/reservation, notional/exposure/concentration/rate/open-order, daily loss/drawdown, duplicate/conflict và leadership lease.
- Thiếu hoặc stale data/state gây reject/fail closed, trừ policy reduce-only emergency có ADR/rule riêng.
- APPROVE/REJECT/REQUIRE_MANUAL_APPROVAL đều lưu machine-readable reason, policy/snapshot/input hash, decision time/expiry; manual approve chạy lại full fresh risk evaluation.
- Reservation tạo trước submit, được chuyển/release theo lifecycle và stale reservation alert/reconcile; không silently clear.
- Kill switch hierarchy GLOBAL -> VENUE -> ACCOUNT -> STRATEGY -> INSTRUMENT; parent scope vô hiệu child; default FREEZE cấm tăng exposure.
- Release kill switch cần explicit approval, re-auth, reconciliation sạch, health check và audit evidence.

**Dependencies:** ADR-0007, ADR-0012; risk policy/config, RiskDecision/kill-switch contracts; NFR-SAFE-001, NFR-AUD-001, NFR-SEC-001, SEC-AUTH-001.

## 9. FR-OPS-001 — Control plane vận hành

**Mô tả:** Hệ thống MUST cung cấp control plane qua API/CLI để quản lý read model, audit, reconciliation, strategy/deployment/kill-switch action theo phase và phân quyền phù hợp.

**Scope và acceptance criteria:**

- Canonical HTTP contract là contracts/api/openapi.yaml; route/request/response/status không được implement trước schema/fixture review.
- API prefix, asynchronous command lifecycle, idempotency, optimistic concurrency, cursor pagination và error envelope tuân theo master.
- Các read endpoint và command được mở theo phase; manual order endpoint không nằm trong MVP.
- Control plane không xử lý market tick hot path, không trả raw secret và không bypass trading-node/risk/execution policy.
- Dangerous command có actor, authorization, reason, correlation ID, idempotency, audit before/after hash và re-auth khi policy yêu cầu.
- CLI đi qua command/authorization path được duyệt; không truy cập DB/venue trực tiếp để bypass policy.

**Dependencies:** ADR-0002, ADR-0014, ADR-0015 trước Phase 3; OpenAPI/command/config/error contracts; NFR-AUD-001, NFR-SEC-001, NFR-OPS-001, SEC-AUTH-001, SEC-CRED-001.

## 10. Mapping chức năng tới quality/security

| Functional requirement | NFR bắt buộc | SEC bắt buộc |
|---|---|---|
| FR-MKT-001 | NFR-DET-001, NFR-AUD-001, NFR-SAFE-001 | SEC-DATA-001, SEC-AUD-001 |
| FR-STR-001 | NFR-DET-001, NFR-SAFE-001 | SEC-SUP-001 |
| FR-EXEC-001 | NFR-AUD-001, NFR-SAFE-001, NFR-OPS-001 | SEC-AUD-001, SEC-CRED-001 |
| FR-LED-001 | NFR-DET-001, NFR-AUD-001, NFR-SAFE-001 | SEC-AUD-001, SEC-DATA-001 |
| FR-REC-001 | NFR-AUD-001, NFR-SAFE-001, NFR-OPS-001 | SEC-AUD-001, SEC-CRED-001 |
| FR-RSK-001 | NFR-DET-001, NFR-AUD-001, NFR-SAFE-001 | SEC-AUTH-001, SEC-AUD-001 |
| FR-OPS-001 | NFR-AUD-001, NFR-SEC-001, NFR-OPS-001 | SEC-AUTH-001, SEC-CRED-001, SEC-AUD-001 |

## 11. Điều kiện review

Mỗi FR cần có contract versioned, data dictionary hoặc domain policy khi applicable, task card, test evidence và gate mapping trong GOV-TRACE-001 trước khi được coi là implemented. Thay đổi semantic hoặc breaking acceptance cần ADR/versioning, không sửa âm thầm requirement đã được dùng.

## 12. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | Chuẩn hóa acceptance criteria cho baseline functional requirements. | Technical Operator | Pending |
