# DOM-004 — Accounting policy framework

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 0.2.0 |
| Trạng thái | DRAFT — chờ Account Owner phê duyệt |
| Owner | Technical Operator |
| Approver | Account Owner |
| Ngày soạn | 2026-07-31 |
| Liên quan | FR-LED-001, FR-EXEC-001, FR-REC-001, NFR-AUD-001, NFR-SAFE-001; ADR-0003, ADR-0011, ADR-0012 |
| Nguồn policy | [Master specification](../../../AI_AUTO_TRADE_MASTER_SPEC.md), §3.3, §5.1, §7.8, §8.11 |

## 1. Mục đích và status

Đây là framework quyết định accounting cho MVP, không phải báo cáo thuế hay tư vấn kế toán. Ledger là internal accounting truth append-only; venue là external truth của state tức thời. Hai bên phải reconciliation nhưng không ghi đè lẫn nhau. Mâu thuẫn deadline giữa §7.8 (trước Phase 1) và §8.11 (Phase 3) của master đã được resolve thành "trước Phase 1" tại master v2.2.0.

Tài liệu đang DRAFT. Chưa có asset/currency, cost-basis, valuation source, rounding, fee/rebate, transfer/adjustment hoặc chart-of-accounts cụ thể được Account Owner phê duyệt; vì vậy không có journal posting runtime nào được xem là approved chỉ dựa trên tài liệu này.

## 2. Mô hình canonical

```text
verified source event
  -> immutable journal entry
  -> immutable postings (per accounting policy version)
  -> rebuildable balance / position / PnL projections
```

`JournalEntry` và `Posting` là source of truth accounting. Projection chỉ là read model; có thể rebuild từ journal/posting. Mỗi fill, fee, rebate, funding, interest, transfer hoặc verified adjustment phải có source fact/evidence, không được mutate posting cũ.

## 3. Invariant bắt buộc

1. Money, price, quantity, fee và PnL dùng Decimal / `NUMERIC(38,18)`, không `float`.
2. Journal entry/posting immutable, append-only; runtime role không được `UPDATE`/`DELETE`.
3. Mọi entry cân bằng theo asset/commodity và accounting convention đã được ADR-0011 chốt. Database write path phải enforce; property test không thay enforcement.
4. Một source event/fill chỉ book một lần; duplicate evidence không tạo journal entry/posting lần hai.
5. Every entry carries `source_type`, `source_id`, `source_event_id`, `accounting_policy_version`, `effective_at`, `recorded_at`, correlation/causation context.
6. Adjustment chỉ khi không thể reconstruct original event, có external evidence, reason và approval. Không sửa history để “khớp” venue.
7. Accounting state phải trace được từ market/order/risk/fill đến journal/posting/projection/reconciliation evidence.

## 4. Logical chart of accounts

Chart cụ thể vẫn chờ owner, nhưng mỗi account definition phải có: internal account ID, code, name, classification (`ASSET`, `LIABILITY`, `EQUITY`, `INCOME`, `EXPENSE`, hoặc classification được ADR-0011 thay thế), commodity/asset applicability, normal direction hoặc commodity convention, active/effective range, policy version và parent account khi dùng hierarchy.

Không hard-code account code/name theo venue/asset trong domain. Mapping giữa venue balance terminology và canonical account cần versioned reference/policy record.

## 5. Journal entry và posting contract

| Record | Fields/must-have semantics |
|---|---|
| Journal entry | UUIDv7, source references, policy version, `effective_at`, `recorded_at`, narrative/reason, correlation/causation, evidence hash, append-only sequence |
| Posting | UUIDv7, journal entry ID, line number unique, canonical account ID, asset/commodity, quantity `NUMERIC(38,18)`, direction/convention field approved by ADR, optional valuation reference, immutable |
| Balance projection | derived account/asset balance, watermark/checkpoint, rebuildable; not a truth source |
| Position projection | derived instrument quantity/cost/realized/unrealized views per approved policy; rebuildable |

Unique `(journal_entry_id, line_no)` is mandatory. Foreign keys only stay inside `portfolio_ledger` schema. Financial semantics must never be hidden in JSONB.

## 6. Source event treatment (framework)

| Source fact | Required accounting behavior | Policy decision still required |
|---|---|---|
| Verified fill | book exchanged asset quantities and any known cost/consideration exactly once | convention, account mapping, cost basis |
| Fee/rebate | separate auditable source/line; never silently net away evidence | fee asset and rebate treatment, rounding |
| Funding/interest | out of spot MVP unless capability/ADR enables | account mapping and recognition rules |
| Transfer/deposit/withdrawal | no automatic withdrawal; external transfer only with approved evidence/flow | classification, approval and reconciliation |
| Correction | append approved adjustment linked to original incident | authority, valuation and audit content |
| Unrealized PnL | projection/value result only from approved valuation policy | source, timestamp, FX/asset pricing, rounding |

## 7. Rounding, scale, valuation and cost basis

The fixed storage precision is `NUMERIC(38,18)`. Instrument/asset scale greater than 18 is unsupported until ADR/migration. Accounting policy must explicitly determine before activation:

- asset/currency scale and permitted residual/tolerance;
- rounding mode and where it occurs (calculation, posting, display);
- cost-basis method for realized PnL;
- position/inventory model: net position vs lot-based (FIFO/LIFO/HIFO) và tương tác với cost-basis method — quyết định cùng ADR-0011;
- valuation source, timestamp and stale-data behavior for unrealized PnL;
- treatment of locked/reserved balance versus booked/exposure state;
- fee, rebate, transfer and adjustment mapping;
- daily/reset timezone if PnL/risk policy requires it.

No fallback default is authorized. A missing choice blocks affected ledger/risk behavior.

## 8. Reconciliation and correction

Reconciliation compares external balance, position, open orders, fills and fees with internal projection/source facts. A discrepancy opens a case with snapshots, tolerance, time window, adapter version and evidence. It does not alter journal or posting. If original data cannot be reconstructed, an `APPROVED_ADJUSTMENT` path creates a new balancing entry under a named policy version and approval record.

## 9. Database enforcement and recovery

ADR-0011 must specify the approved database enforcement mechanism for entry balance (for example a deferred constraint trigger or approved stored write procedure). Only the approved ledger write path may insert journal/posting. Backup/restore validation must check balance, source dedupe, projection rebuild and reconciliation before strategy is enabled.

## 10. Required approval checklist

- [ ] Accounting convention and chart structure selected.
- [ ] Asset scales, rounding, fee/rebate, transfer and adjustment treatment approved.
- [ ] Cost basis and valuation source/timestamp approved.
- [ ] Locked/reserved balance representation aligned with risk reservation.
- [ ] Database balance enforcement and role grants approved.
- [ ] ADR-0011 and transaction mapping ADR-0012 APPROVED; properties/fixtures/evidence linked.

Until every applicable item is approved, Phase 1 ledger implementation is BLOCKED.

## 11. Verification (DRAFT — mapping invariant sang test dự kiến)

| Invariant (§3) | Loại test dự kiến |
|---|---|
| #3 — mọi entry cân bằng theo asset/convention | property test: journal balance per entry |
| #4 — một source event/fill chỉ book một lần | property test: duplicate fill không tạo double-book |
| §2 — projection rebuildable từ journal/posting | rebuild test: projection == replay of journal |
| #6 — adjustment cần evidence/approval | integration test: adjustment yêu cầu approval evidence |

## Nhật ký thay đổi

| Ngày | Phiên bản | Người thực hiện | Phê duyệt | Nội dung |
|---|---|---|---|---|
| 2026-07-31 | 0.2.0 | Technical Operator | Pending | Ghi nhận resolution deadline §7.8/§8.11 thành "trước Phase 1" theo master v2.2.0 tại §1; thêm open decision position/inventory model (net vs lot-based FIFO/LIFO/HIFO) tại §7; thêm §11 Verification mapping invariant sang test dự kiến (DRAFT) |

