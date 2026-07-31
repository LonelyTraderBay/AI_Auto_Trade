# C4 Context — ranh giới hệ thống AI Auto Trade

| Thuộc tính | Giá trị |
|---|---|
| Document ID | ARC-C4-001 |
| Phiên bản | 0.2.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §2, §4.1–§4.5, §6, §8, §10–§12 |
| Related requirements | FR-MKT-001, FR-EXEC-001, FR-LED-001, FR-REC-001, FR-RSK-001, FR-OPS-001, FR-AI-001; NFR-SAFE-001, NFR-SEC-001, NFR-AI-001 |
| Related ADR | ADR-0001, ADR-0002, ADR-0005, ADR-0007, ADR-0014; ADR-0008/0009/0015/0016 theo phase |

> C4 context này mô tả phạm vi và quan hệ logic. Nó không là network diagram, permission matrix hoặc deployment manifest. Tích hợp external venue, authentication provider và notification channel vẫn bị chặn bởi Open Decision Register/ADR tương ứng.

## 1. System of interest

AI Auto Trade là một modular monolith để chạy vertical slice từ market event đến audit/reconciliation. System of interest giữ canonical domain của strategy, risk, OMS, ledger, reconciliation và control/audit.

Hệ thống không tự động thay thế quyết định Account Owner/Risk Approver; không hứa hẹn PnL; không cho UI hoặc AI gọi venue execution trực tiếp.

## 2. Context diagram

~~~mermaid
flowchart LR
    AO[Account Owner]
    TO[Technical Operator]
    RA[Risk Approver]
    SO[Security / Backup Owner]
    V[Viewer / Dashboard User]

    subgraph SYS[AI Auto Trade platform]
        CP[Control plane]
        TN[Trading runtime]
        MD[Market / reference ingestion]
        REC[Reconciliation and audit]
        RES[Research and replay]
        AI[AI provider/profile + proposal worker<br/>Phase 6 only]
    end

    VENUE[External venue / testnet]
    FEED[Public/private market data feed]
    CAT[Historical data catalog]
    IDP[Authentication provider<br/>TBD before Phase 3]
    NOTIFY[Alert / notification channel<br/>TBD before Phase 3]
    LLM[LLM provider<br/>Phase 6 only]

    AO -->|scope, approval, gate evidence| CP
    TO -->|audited operational commands| CP
    RA -->|risk approval / release action| CP
    SO -->|credential, topology, restore governance| CP
    V -->|sanitized read model only| CP

    FEED -->|market/reference input| MD
    MD -->|canonical event / quality| TN
    MD -->|dataset / lineage| CAT
    RES <-->|recorded data / report| CAT
    RES -->|candidate evidence only| CP
    CP -->|authorized command / config intent| TN
    TN -->|audit, health, reconciliation state| REC
    TN <-->|submit, cancel, query only by mode/capability| VENUE
    REC <-->|external state evidence| VENUE
    CP -->|alerts / incident routing| NOTIFY
    CP <-->|actor authentication / session| IDP
    AI <-->|sanitized proposal / memory| CP
    AI <-->|approved provider/profile, structured request, no trade credential| LLM
~~~

## 3. Actor và external-system relationship

| Entity | Trao đổi với platform | Quyền / constraint |
|---|---|---|
| Account Owner | Scope, owner decision, ADR/gate/canary approval. | Không override regulatory constraint hoặc safety invariant. |
| Technical Operator | Audited control command, CI, deploy/runbook/reconciliation request. | Không bypass risk, authorization hoặc task/gate control. |
| Risk Approver | Risk policy, manual approval, kill-switch release và canary review. | Fresh risk evaluation bắt buộc; không bypass audit. |
| Security/Backup Owner | Secret, access, topology, backup/restore decision và evidence. | Không cấp trade credential cho UI/AI/unauthorized process. |
| Viewer/Dashboard user | Sanitized projection/audit read theo permission. | Không gọi DB/venue trực tiếp. |
| External venue | Market data, account state, execution/recovery evidence theo capability. | Không phải source of truth của internal ledger; external outcome unknown phải reconcile. |
| Market data feed | Public/private input, sequence/gap/quality evidence. | Không tự biến thành risk decision hoặc order trigger ngoài canonical flow. |
| Historical data catalog | Dataset/manifest/Parquet và research/replay read. | Không làm phình OLTP hoặc viết live state. |
| Authentication provider | Actor/session input cho Control API, lựa chọn chưa chốt. | Không tồn tại trong Phase 0 local loopback bootstrap; requires ADR-0015 trước Phase 3. |
| Alert channel | Incident/alert delivery, lựa chọn chưa chốt. | Không mang secret/raw sensitive payload. |
| AI provider / private gateway | Structured proposal/memory only ở Phase 6, qua provider/model/policy profile catalog, isolated BYOK secret ingress và owner-scoped connection. | Không có arbitrary endpoint/proxy/policy, execution tool, venue credential hoặc config promotion authority. |

## 4. Bounded context ownership

| Context | Sở hữu | Incoming | Outgoing | Cấm |
|---|---|---|---|---|
| reference | Venue, instrument, symbol mapping, constraints. | Venue/reference source. | Versioned reference snapshot. | Submit order. |
| market_data | Normalized tick/trade/quote/candle, quality, feed health. | Adapter feed/raw event. | Canonical market event/dataset lineage. | Risk decision. |
| strategy | Definition/version/instance/state/signal/intent proposal. | Canonical event/state/checkpoint. | Domain action, ProposedOrderIntent. | Network/DB/file/env/venue import. |
| risk | Policy, reservation, verdict, limit state. | Immutable intent and snapshots. | RiskDecision/reservation/kill state. | Submit order. |
| execution | OMS, attempt, venue submission, order/fill lifecycle. | Approved intent/risk decision/venue evidence. | Canonical order/fill events, reconciliation input. | Bypass risk. |
| portfolio_ledger | Journal, postings, balance/position/PnL projection. | Fill/fee/verified adjustment. | Accounting projection/audit link. | Overwrite history to match venue. |
| research | Dataset/backtest/validation/report. | Catalog/recorded event. | Candidate/report evidence. | Write live state or trade credential. |
| operations | Deployment, lease, health, incident, kill switch, AI connection metadata/audit. | Authorized control action/runtime signal. | Readiness/incident/safe-state/AI lifecycle event. | Return raw secret or cross-owner connection metadata. |
| platform | Outbox, inbox, DLQ, idempotency/delivery metadata. | Cross-context delivery operation. | Delivery/compatibility signal. | Own business/risk decision. |
| ai_memory | AI inference provenance/proposal/memory at Phase 6. | Sanitized projection + active owner-scoped connection policy. | Proposal/memory record. | Execution write, trade credential or raw key. |

## 5. Trust và authority boundaries

| Boundary | Rule |
|---|---|
| Strategy -> execution | Strategy returns action only. It cannot make venue/DB/network call or create ClientOrderId. |
| Risk -> execution | Risk returns decision/reservation only. Execution owns submit/OMS. |
| Control plane -> trading runtime | Control plane submits authorized command/config intent; it does not execute hot-path market tick logic. |
| UI/CLI -> control plane | UI/CLI must use authorized API/command path; no direct venue/database path. |
| AI -> platform | AI produces proposal only; it may resolve a just-in-time owner-scoped provider binding but must not receive trade credential, execution capability or raw-key read-back. |
| Internal -> venue | Only trading runtime with valid mode, manifest, capability, lease and credential may wire execution adapter. |
| Internal ledger -> venue | They are reconciled but neither silently overwrites the other. |
| Research -> live contexts | Research evidence may inform candidate workflow but cannot write live state/promotion. |

## 6. Context-level safety flows

1. Market/reference adapter produces input; market_data/reference normalize and validate it.
2. Strategy sees only canonical state/event and produces proposal.
3. Execution canonicalizes proposal, assigns internal/client identity, then calls risk.
4. Risk returns APPROVE, REJECT or REQUIRE_MANUAL_APPROVAL; only fresh approval can reach queue.
5. Execution/operations/portfolio_ledger coordinate durable attempt, fill, audit, reconciliation and safe-state.
6. Control plane exposes sanitized observations and authorized commands; no manual order endpoint exists in MVP.

Detailed temporal behavior is defined by ARC-SEQ-001 and Master §5/§8.

## 7. Phase constraints

| Capability | Earliest phase | Constraint |
|---|---|---|
| Local control/read skeleton | 0 | Loopback only; no venue credential/external command. |
| Fake venue core | 1 | No external network dependency. |
| Catalog/replay/paper simulator | 2 | No live execution. |
| Venue testnet/shadow | 3 | Requires venue/auth/OD/ADR gate and capability contract. |
| Canary | 4 | Requires independent safety review, signed scope/cap and live topology gate. |
| Dashboard | 5 | Client of control API only. |
| AI/memory/BYOK | 6 | Proposal-only, provider/policy profile catalog, isolated secret ingress, egress/DNS/budget/rotation gate; no hot-path/execution authority. |

## 8. Review checklist

- [ ] Every relationship has a named owner/context and explicit allowed direction.
- [ ] No arrow grants UI/AI/strategy direct venue execution.
- [ ] External integrations shown as TBD remain blocked until owner decision/ADR.
- [ ] Context ownership matches data architecture/ERD/contract registry when those artifacts are created.
- [ ] Sequence and container views have been updated if a relationship changes.

## 9. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | Tạo C4 context baseline cho modular monolith MVP. | Technical Operator | Pending |
| 0.2.0 | 2026-07-31 | Làm rõ AI provider catalog/BYOK owner scope và secret/execution boundary Phase 6. | Technical Operator | Pending |
