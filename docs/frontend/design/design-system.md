# FE-DS-001 — Frontend design system (Flutter dashboard)

| Thuộc tính | Giá trị |
|---|---|
| Document ID | FE-DS-001 |
| Phiên bản | 0.1.1 |
| Trạng thái | DRAFT |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực — chờ Account Owner phê duyệt |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | [Master](../../../AI_AUTO_TRADE_MASTER_SPEC.md) §11.3, §11.5, §14 Phase 5; [DOM-002](../../backend/domain/oms-state-machine.md); [PRD-GLOSSARY-001](../../shared/glossary.md); [ARC-AI-001](../../backend/architecture/ai-provider-byok-architecture.md); [C-ERR-001](../../../contracts/errors/error-catalog.md); `contracts/api/openapi.yaml` |
| Related requirements | NFR-SAFE-001, NFR-AUD-001, NFR-OPS-001; FR-EXEC-001, FR-REC-001 |
| Related ADR | ADR-0005, ADR-0012, ADR-0015 (session/dangerous action UX phụ thuộc), ADR-0016 (BYOK Phase 6) |

> Tài liệu này định nghĩa design system cho Flutter dashboard — client thuần của Control API theo master §11.5 ("Flutter chỉ là client của Control API... không giữ secret hoặc logic risk/execution"). Mọi lựa chọn thẩm mỹ trong tài liệu này là DRAFT — cần Account Owner phê duyệt; các ràng buộc semantic (state name, enum, error envelope) là normative theo backend contract được trích dẫn và không được đổi ở client.

## 1. Nguyên tắc: dashboard vận hành (operations-first)

1. **Đọc nhanh trạng thái quan trọng đứng trên thẩm mỹ.** Dashboard tồn tại để operator thấy mode thật, health, order/position/PnL, incident và reconciliation (master §11.5). Mọi trade-off giữa "đẹp" và "đọc được trạng thái nguy hiểm trong dưới một giây" phải chọn vế sau.
2. **Trạng thái nguy hiểm phải nổi bật, không thể bỏ sót.** Các điều kiện chặn an toàn — `safe_state` khác `READY`, order ở `UNKNOWN`/`RECONCILING`/`LOST` (DOM-002 §2), kill switch active (C-ERR-001 `KILL_SWITCH_ACTIVE`) — phải hiển thị persistent (banner/badge luôn thấy), không được ẩn sau tab, collapse, toast tự tắt hay pagination.
3. **Không dark-pattern che giấu trạng thái xấu.** UI không được làm mềm, đổi tên, gộp hay trì hoãn hiển thị trạng thái tiêu cực (ví dụ hiển thị `LOST` như "processing"). Đây là hệ quả trực tiếp của nguyên tắc audit/evidence "facts are append-only... Evidence is retained, not rewritten" (SEC-001 §4) và quy tắc dùng từ glossary §7 (không gọi testnet/paper/shadow là live trading).
4. **UI là read model, không phải nguồn quyền.** Client hiển thị projection và gửi command qua API theo quyền; mất dashboard không ảnh hưởng trading node (master §11.5, Phase 5 exit gate §14). Không control an toàn nào được implement chỉ ở UI (SEC-002 §1).

## 2. Semantic color system (DRAFT — cần Account Owner phê duyệt)

Màu là **semantic token**, không phải màu trang trí: một state luôn map vào đúng một nhóm màu. Palette cụ thể (hex value) sẽ chốt trong review thiết kế Phase 5; nhóm semantic dưới đây là phần normative của tài liệu này.

### 2.1 OMS order state → nhóm màu

16 state canonical lấy nguyên văn từ DOM-002 §2 và glossary §2 "OMS state name" (SCREAMING_SNAKE, không dịch — xem §4):

| Nhóm màu (semantic) | State | Căn cứ |
|---|---|---|
| `safe/neutral` (xanh lá/xám trung tính — lifecycle bình thường) | `CREATED`, `RISK_APPROVED`, `SUBMISSION_QUEUED`, `SUBMITTING`, `OPEN`, `PARTIALLY_FILLED`, `FILLED` | Non-terminal lifecycle bình thường và terminal thành công (`FILLED`) theo DOM-002 §2 |
| `warning` (vàng/cam — cần hành động hoặc đang chờ người) | `PENDING_MANUAL_APPROVAL`, `CANCEL_REQUESTED` | `PENDING_MANUAL_APPROVAL` = "Risk yêu cầu approval"; `CANCEL_REQUESTED` = "cancel request đã durable, chờ evidence" (DOM-002 §2) |
| `danger/blocked` (đỏ — safe block, cấm thao tác thường) | `UNKNOWN`, `RECONCILING`, `LOST` | `UNKNOWN`/`RECONCILING` là "non-terminal/safe block", cấm blind retry; `LOST` là terminal với "critical incident + manual handling" (DOM-002 §2–§3) |
| `terminal-negative` (xám đậm/đỏ nhạt — kết thúc không thành) | `RISK_REJECTED`, `REJECTED`, `CANCELLED`, `EXPIRED` | Terminal "không được quay lại non-terminal" (DOM-002 §2) |

Ghi chú bắt buộc:

- `UNKNOWN` và `LOST` phải kèm visual weight cao nhất (nhóm danger) vì chúng gắn với nghĩa vụ reconcile và block exposure (DOM-002 §3, §9: "A `LOST` order blocks conflicting exposure").
- `EXPIRED` là một state duy nhất; UI phân biệt nguyên nhân bằng `terminal_reason` (`INTENT_EXPIRED`, `DECISION_EXPIRED`, `APPROVAL_EXPIRED`, `VENUE_TIF_EXPIRED`) hiển thị phụ, không tạo state UI mới (DOM-002 §5). **Lưu ý contract:** enum `Order.terminal_reason` của openapi v1.1 chưa chứa các reason chi tiết này (GAP 8, FE-SCREEN-001 §4; RAID I-006) — client chỉ nhận và render giá trị thuộc enum contract hiện hành, phần chi tiết chỉ áp dụng sau khi OD-010 đóng GAP.
- `EXTERNAL` không phải OMS state (DOM-002 §1, glossary §2) — không được render như một order state; hiển thị như classification của reconciliation case.

### 2.2 Incident severity → 4 mức

Enum `severity` lấy từ `contracts/api/openapi.yaml` (schema incident): `CRITICAL, HIGH, MEDIUM, LOW`.

| Severity | Mức hiển thị (DRAFT) |
|---|---|
| `CRITICAL` | Đỏ đậm + banner persistent, đứng đầu mọi danh sách |
| `HIGH` | Đỏ/cam, badge nổi |
| `MEDIUM` | Vàng |
| `LOW` | Xám trung tính |

### 2.3 `safe_state` → banner colors

Enum `safe_state` lấy từ `contracts/api/openapi.yaml` schemas `Readiness`/`Runtime`: `READY, BLOCKED, FROZEN, KILL_SWITCH_ACTIVE`.

| `safe_state` | Banner (DRAFT) |
|---|---|
| `READY` | Không banner hoặc chỉ báo xanh kín đáo |
| `BLOCKED` | Banner cam persistent, hiển thị `blocking_reasons` (field bắt buộc của `Readiness`) |
| `FROZEN` | Banner đỏ persistent |
| `KILL_SWITCH_ACTIVE` | Banner đỏ đậm nhất, persistent trên mọi màn hình; khớp semantic C-ERR-001 `KILL_SWITCH_ACTIVE` (HTTP 423, `retryable=false`, "Release only through high-risk approved procedure") |

### 2.4 BYOK connection state → nhóm (Phase 6)

10 lifecycle state lấy nguyên văn từ ARC-AI-001 §4.2: `DRAFT`, `PENDING_SECRET`, `PENDING_VALIDATION`, `VALIDATION_FAILED`, `ACTIVE`, `ROTATION_PENDING_SECRET`, `ROTATION_PENDING_VALIDATION`, `SUSPENDED`, `EXPIRED`, `REVOKED`.

| Nhóm | State | Ghi chú |
|---|---|---|
| `pending` (vàng/xám — chưa dùng được cho inference) | `DRAFT`, `PENDING_SECRET`, `PENDING_VALIDATION`, `VALIDATION_FAILED`, `ROTATION_PENDING_SECRET`, `ROTATION_PENDING_VALIDATION` | `VALIDATION_FAILED` dùng emphasis warning trong nhóm (retry chỉ qua explicit `PENDING_SECRET`, ARC-AI-001 §4.2); rotation states vẫn cho phép active binding cũ phục vụ inference (ARC-AI-001 §4.2) — UI phải chỉ rõ "đang rotate, key cũ vẫn hiệu lực" |
| `active` (xanh) | `ACTIVE` | |
| `terminal` (xám đậm/đỏ) | `SUSPENDED`, `EXPIRED`, `REVOKED` | Terminal trong BYOK v1, "recovery requires a new, separately reviewed connection lifecycle, never an implicit resume" (ARC-AI-001 §4.2) — UI không được đưa nút "resume/reactivate" |

### 2.5 Accessibility (normative)

- **Không dùng màu làm kênh thông tin duy nhất.** Mỗi state/severity phải kèm icon và/hoặc text label (chính là wire enum, §4) để người mù màu và màn hình grayscale vẫn phân biệt được.
- **Tương phản tối thiểu WCAG 2.1 AA** (4.5:1 cho text thường, 3:1 cho text lớn/UI component) cho mọi cặp foreground/background của semantic token — DRAFT: verify bằng automated contrast check trong CI theo FE-TEST-001.

## 3. Data display rules

### 3.1 Decimal

- Giá, quantity, money, fee, PnL đến từ API dưới dạng `DecimalString` — "Base-10 Decimal serialized as string; never JSON number/float" (`contracts/api/openapi.yaml`), khớp glossary §3 "Decimal... float bị cấm".
- **Client hiển thị nguyên văn precision nhận được, không làm tròn.** Client không được parse qua `double`/float ở bất kỳ tầng nào của display path (hệ quả invariant "Không mất precision qua serialize/deserialize", master §13.4).
- Formatting duy nhất được phép: ngăn cách hàng nghìn (thousand separator) không thay đổi chữ số (DRAFT — cần Account Owner phê duyệt).
- Số âm hiển thị dấu `-` rõ ràng (pattern `DecimalString` cho phép `-?`), không chỉ dựa vào màu đỏ (accessibility §2.5).
- Đơn vị/asset luôn kèm số lượng: "1250.50000000 USDT", không bao giờ số trần — asset là "đơn vị tài sản/currency" gắn với balance/ledger (glossary §1).

### 3.2 Timestamp

- API trả `Timestamp` UTC ISO-8601 (pattern `Z$`, `contracts/api/openapi.yaml`). UI hiển thị theo local timezone của operator, kèm tooltip/secondary text giá trị UTC gốc nguyên văn.
- Tuổi (age) dạng relative ("3m ago") bắt buộc cho các phần tử có SLA/backlog semantic: order `UNKNOWN` (gắn unknown-order SLO, SEC-001 T-004) và backlog/queue view. Relative time phải tính từ injected clock, không dùng wall clock trực tiếp (xem FE-TEST-001 §4, khớp NFR-DET-001).
- Không đặt tên hiển thị lệch chuẩn timestamp: giữ đúng semantic `occurred_at` / `received_at` / `processed_at` / `recorded_at` / `effective_at` (glossary §3, §7).

### 3.3 Identifier

- Internal ID là UUIDv7 (glossary §1; schema `UuidV7` trong openapi.yaml). Hiển thị rút gọn **8 ký tự hex đầu** + action copy toàn bộ giá trị đầy đủ. Không truncate trong giá trị được copy.
- `correlation_id` trong `ErrorEnvelope` (C-ERR-001 §1) luôn hiển thị được và copy được — nó là evidence ("correlation ID is evidence", C-ERR-001 `INTERNAL_ERROR`).
- `VenueOrderId` có thể chưa tồn tại khi outcome unknown (glossary §1) — UI hiển thị placeholder rõ ("chưa có venue order ID"), không hiển thị chuỗi rỗng.

## 4. Terminology — UI copy

UI copy PHẢI dùng đúng glossary (`docs/shared/glossary.md`); các quy tắc sau là normative:

1. **OMS state hiển thị nguyên văn wire enum** — SCREAMING_SNAKE giữ nguyên (`PARTIALLY_FILLED`, không phải "Khớp một phần" làm label chính), theo glossary §2: "Tên state wire/canonical dùng đúng chữ hoa". Mô tả tiếng Việt chỉ là text phụ (tooltip/subtitle).
2. **Không gọi credential binding hay masked label là "API key"** — "Không gọi credential binding, masked label hay validation state là API key; raw key không được read-back" (glossary §7; ARC-AI-001 §2).
3. **"Reconcile", không phải "retry"** — "Không dùng 'retry' cho unknown external outcome; dùng reconcile" (glossary §7; DOM-002 §2 `UNKNOWN`: "cấm blind retry").
4. **Testnet/paper/shadow không được hiển thị như "live"** — glossary §7: "Không gọi testnet/paper/shadow là live trading". Mode label (`BACKTEST`…`FULL_LIVE`, glossary §5) hiển thị nguyên văn, mọi màn hình phải hiển thị mode thật (master §11.5).
5. Không gọi AI proposal là strategy/order approval hay execution; không gọi projection là source of truth accounting (glossary §7).

## 5. Layout patterns

### 5.1 Bốn state chuẩn của mọi view

Mọi view dữ liệu phải implement đủ 4 state (được test theo FE-TEST-001 §1):

| State | Yêu cầu |
|---|---|
| `loading` | Skeleton placeholder, không spinner toàn màn hình che layout |
| `empty` | Có hướng dẫn hành động tiếp theo, không màn trắng |
| `error` | Hiển thị `code`, `message`, `correlation_id` và `remediation_hint` từ `ErrorEnvelope` (C-ERR-001 §1); hành vi retry theo `retryable` — xem FE-API-001 §8 |
| `stale` | Nhãn "as-of <timestamp>" khi dữ liệu không còn tươi/mất kết nối; không được hiển thị dữ liệu cũ như dữ liệu hiện tại (hệ quả nguyên tắc §1.3) |

### 5.2 Danger zone pattern

Dangerous action (danh sách theo master §11.3 — xem FE-SEC-001 §4) dùng pattern thống nhất: tách vùng riêng biệt về thị giác (danger zone), confirm 2 bước nêu rõ hậu quả/scope, sau đó **re-auth** trước khi submit — vì "Không có action high-risk nào chỉ dựa vào UI confirmation" (master §11.4) và re-auth là bắt buộc theo master §11.3/SEC-003 §4. Chi tiết flow ở FE-SEC-001 §4.

### 5.3 Typography/spacing (DRAFT — cần Account Owner phê duyệt)

- Dùng Material 3 baseline của Flutter (type scale và spacing mặc định), không custom font trong MVP — giảm bề mặt review dependency (CONTRIBUTING §3) và giữ trọng tâm operations-first §1.
- Monospace cho: `DecimalString`, identifier/UUID, hash (`manifest_hash` dạng `sha256:…`, openapi.yaml `Runtime`), wire enum — để căn cột và đối chiếu ký tự chính xác.

## Nhật ký thay đổi

| Ngày | Phiên bản | Người thực hiện | Phê duyệt | Nội dung |
|---|---|---|---|---|
| 2026-08-02 | 0.1.1 | Technical Operator | Pending | Audit toàn diện: §2.1 ghi chú tường minh enum terminal_reason chi tiết chưa có trong openapi v1.1 (GAP 8/I-006) — client chỉ render giá trị enum contract hiện hành. |
| 2026-07-31 | 0.1.0 | Technical Operator | Pending | Khởi tạo design system: nguyên tắc operations-first, semantic color mapping cho 16 OMS state / severity / safe_state / BYOK connection state, data display rules (Decimal/timestamp/UUID), terminology theo glossary và layout patterns 4-state + danger zone. |
