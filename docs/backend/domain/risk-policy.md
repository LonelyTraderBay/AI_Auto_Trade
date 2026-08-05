# DOM-003 — Risk policy and reservation contract

| Thuộc tính | Giá trị |
|---|---|
| Document ID | DOM-RISK-001 (registry DOCS_INDEX; title giữ alias ngắn) |
| Phiên bản | 0.2.0 |
| Trạng thái | DRAFT — chờ Risk Approver và Account Owner phê duyệt |
| Owner | Risk Approver |
| Approver | Account Owner (pending) |
| Ngày soạn | 2026-07-31 |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-08-02 |
| Liên quan | FR-RSK-001, FR-EXEC-001, FR-REC-001, NFR-SAFE-001, NFR-AUD-001; ADR-0005, ADR-0007, ADR-0012 |
| Nguồn policy | [Master specification](../../../AI_AUTO_TRADE_MASTER_SPEC.md), §5.4–§5.6, §6.3, §7.7, §8.4–§8.10 |
| Change summary | 2026-08-02: chuẩn hóa header theo GOV-DOC-001 §3 (audit toàn diện); nội dung không đổi. |

## 1. Mục đích, authority và giới hạn

Risk là synchronous, deterministic gate ngay trước execution. Tài liệu này xác định cấu trúc và invariant; nó không tự đặt venue, instrument, notional, loss, drawdown, freshness threshold, approval role hay emergency policy. Các giá trị đó phải là immutable, signed risk-policy version do Risk Approver/Account Owner chốt ở phase phù hợp.

Không actor/UI/CLI/AI/adapter nào được bypass risk bằng cách gọi execution port trực tiếp.

## 2. Phạm vi policy và thứ tự hiệu lực

Policy được version, immutable sau activation, có `effective_at`, expiry/supersession rõ và scope từ rộng đến hẹp:

```text
GLOBAL -> VENUE -> ACCOUNT -> STRATEGY -> INSTRUMENT
```

Scope cha áp dụng cho scope con; rule nghiêm ngặt hơn thắng. Nếu có ambiguity, missing policy hoặc policy state không hợp lệ, verdict là `REJECT`/fail closed. Một policy version không được sửa in place.

## 3. Input snapshot cho một decision

| Input | Điều kiện bắt buộc |
|---|---|
| Canonical `OrderIntent` | immutable, có client order ID, expiry, capability-validated fields |
| Policy version | active, đúng scope, được hash/sign và chưa expiry |
| Portfolio snapshot | balance, position, exposure, reservation và version concurrency |
| Market/reference snapshot | price/reference/instrument rule version, freshness/quality state |
| Runtime health | kill switch, execution lease, feed/private account health, deployment approval |
| Time | injected UTC clock, dùng cho daily reset/expiry/freshness |

Theo master §5.6, `RiskDecision` lưu tối thiểu: `verdict`, `approved_quantity`, policy ID/version, portfolio/reference/market snapshot version, `reservation_id` (nullable), machine-readable reason, input hash, decision time và expiry. Ngoài ra tài liệu này lưu thêm snapshot hashes (bổ sung so với master §5.6 — additive, cần được phản ánh vào master trong lần sửa tới). Commit phải phát hiện snapshot/limit state stale; không được approve trên snapshot cũ rồi submit khi exposure đã đổi.

## 4. Required pre-trade checks

| Nhóm | Check tối thiểu | Fail behavior |
|---|---|---|
| Authorization/scope | strategy, deployment, venue, account, instrument được enable/phê duyệt | reject |
| Safety runtime | kill switch inactive, execution leader lease valid | reject; only approved reduce-only emergency exception |
| Data health | market, reference, portfolio/private-account state fresh và quality acceptable | reject |
| Instrument | tick/lot, min/max quantity, min notional, order flag/capability hợp lệ | reject |
| Price | valid price source; sanity/deviation/worst-case pricing per policy | reject |
| Funds/exposure | available/reserved balance, max order, position, gross/net, concentration | reject |
| Rate/open orders | max open order và order rate limit | reject |
| Loss controls | daily loss, drawdown, reset timezone, valuation source | reject |
| Conflict/idempotency | expiry, duplicate/conflicting intent/client order identity | reject |

Leverage, margin, derivatives and automatic flatten are out of MVP. Không thêm check hoặc exception ngầm trong code ngoài policy version đã phê duyệt.

## 5. Verdict contract

| Verdict | Điều kiện / side effect |
|---|---|
| `APPROVE` | persist immutable decision và required reservation; execution mới có thể queue submit |
| `REJECT` | persist machine-readable reason; không tạo submission queue |
| `REQUIRE_MANUAL_APPROVAL` | persist risk-owned pending approval; không reservation/queue trừ khi policy nói rõ reservation pre-approval và đã được ADR phê duyệt [ghi chú: extension "reservation pre-approval" không tồn tại trong master §5.4 và INACTIVE cho đến khi một ADR bật nó một cách tường minh; hành vi mặc định là của master: không reservation, không submission queue] |

Approved quantity, worst-case price/fee/slippage treatment, policy currency/asset scale và rounding phải được policy version ghi rõ. `RiskDecision` expiry làm submit blocked nếu stale.

## 6. Reservation contract

Reservation là lock logic trên balance/exposure trước submission, không phải venue hold. Nó có `reservation_id`, order intent ID, kind, scope, reserved amount/asset, policy/version/snapshot reference, created/expiry/release time và reason. `reserved_amount >= 0`; `(order_intent_id, reservation_kind)` duy nhất.

| Sự kiện | Xử lý reservation |
|---|---|
| risk approve | create/update atomically with decision/order queue flow |
| partial/full fill | chuyển phần đã thực hiện thành exposure/ledger fact theo policy |
| reject/cancel/expire có evidence | release phần còn lại |
| reconciliation proves no order | release theo audited resolution |
| stale reservation | alert + reconcile; không silent clear |
| unknown/lost | giữ/block scope theo policy cho đến evidence/resolution |

Template công thức reservation (DRAFT — tham số hóa; mọi giá trị buffer là symbolic và là owner-decision input theo §10, không phải giá trị được duyệt):

```text
BUY:  reserved_quote = quantity × worst_case_price × (1 + fee_buffer_rate)
      worst_case_price = limit_price                                        (limit order)
      worst_case_price = reference_price × (1 + slippage_buffer_rate)       (market order)
SELL: reserved_base = quantity
```

`fee_buffer_rate` và `slippage_buffer_rate` là policy field bắt buộc (§10), không có default ngầm. Partial fill: release đúng phần tương ứng theo tỷ lệ filled quantity; phần fee buffer chưa dùng được release khi order đạt terminal state.

## 7. Manual approval

Pending approval chứa required approver role, reason, policy/input snapshot hash, expiry và subject identity. Approval record phải có actor, role, re-auth evidence, timestamp và reason. Approval chỉ kích hoạt re-evaluation full risk; không phải một flag bypass. Nếu state thay đổi hoặc expiry xảy ra, order bị reject/expired và cần intent mới.

## 8. Kill switch và degraded behavior

Kill switch hierarchy là `GLOBAL -> VENUE -> ACCOUNT -> STRATEGY -> INSTRUMENT`; scope cha thắng scope con. Default MVP action là `FREEZE`: chặn exposure mới. `CANCEL_OPEN_ORDERS` chỉ khi policy/capability cho phép. `FLATTEN` không tự động trong MVP và cần ADR/risk policy riêng.

Missing data, stale state, feed gap, private-account gap, unknown order, reconciliation BLOCKED, invalid lease, unapproved deployment hoặc failed policy validation đều fail closed. Reduce-only emergency behavior chỉ hợp lệ nếu policy riêng đã định nghĩa trigger, scope, maximum effect, audit và approval.

## 9. Concurrency, audit và operations

Pre-submit runs `SERIALIZABLE` with lock order `risk limit/reservation -> execution order -> platform outbox`. Serialization/deadlock retry chỉ trước external call, bounded, và bắt buộc re-run full risk. Không dùng in-memory mutex hay retry external submit để bảo vệ capital.

Mỗi decision/reservation/approval/kill-switch action phải trace được tới actor or machine identity, policy version, intent, snapshots, correlation/causation/trace ID, result/reason, timestamps và evidence hash. Metrics tối thiểu: approved/rejected/manual counts by reason/scope, reservation age, stale snapshot rejects, kill-switch state, reconciliation blocks and decision latency.

## 10. Owner decisions còn bắt buộc

Các mục sau cố ý chưa có giá trị: policy currency/asset scale, valuation/price source, fee/slippage buffer, exposure/notional/rate/loss/drawdown caps, reset timezone, freshness threshold, approval roles/expiry, reduce-only exception và canary caps. Chúng cần policy artifact đã ký, Open Decision Register và gate phù hợp; không AI nào được điền “giá trị hợp lý”.

## 11. Acceptance trước Phase 1

- [ ] ADR-0007 và ADR-0012 APPROVED.
- [ ] Policy schema/version/fixture và hash/expiry rules được contract registry ghi nhận.
- [ ] Tests cover reject by each class, stale snapshot, reservation races, approval re-evaluation, kill scope and no-bypass path.
- [ ] Risk Approver/Account Owner phê duyệt parameters áp dụng cho environment/scope; nếu chưa có thì runtime trading blocked.

## Nhật ký thay đổi

| Ngày | Phiên bản | Người thực hiện | Phê duyệt | Nội dung |
|---|---|---|---|---|
| 2026-07-31 | 0.2.0 | Technical Operator | Pending | Align danh sách field `RiskDecision` với master §5.6 (đánh dấu snapshot hashes là additive) tại §3; ghi chú escape hatch "reservation pre-approval" INACTIVE vì không có trong master §5.4 tại §5; thêm template công thức reservation tham số hóa (DRAFT) tại §6 |

