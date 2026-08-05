# C4 Container — process, storage và boundary runtime

| Thuộc tính | Giá trị |
|---|---|
| Document ID | ARC-C4-002 |
| Phiên bản | 0.3.0 |
| Change summary | 0.3.0: xem Nhật ký thay đổi; row này được bổ sung 2026-08-02 theo GOV-DOC-001 §3 (audit toàn diện — không đổi nội dung container/ownership). |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §3, §4.6–§4.7, §6, §7, §11–§13 |
| Related requirements | FR-MKT-001, FR-EXEC-001, FR-LED-001, FR-REC-001, FR-OPS-001, FR-AI-001; NFR-SEC-001, NFR-OPS-001, NFR-AI-001 |
| Related ADR | ADR-0001, ADR-0002, ADR-0003, ADR-0004, ADR-0012, ADR-0014, ADR-0015, ADR-0016 |

> Đây là view dự kiến trước implementation. Port, endpoint, DB schema, authentication provider và deployment topology chi tiết phải theo contract/ADR/manifest được phê duyệt, không suy ra từ diagram này.

## 1. Container diagram

~~~mermaid
flowchart TB
    U[Operator / Dashboard client]
    CLI[CLI]
    VENUE[Venue / testnet]
    DATA[Market data source]
    ALERT[Alert channel]
    LLM[Approved AI provider/gateway<br/>Phase 6]
    VAULT[Approved secret provider<br/>opaque BYOK binding]

    subgraph PLATFORM[AI Auto Trade modular monolith deployment]
        API[Control API process<br/>FastAPI]
        NODE[Trading node process<br/>strategy + risk + OMS + ledger]
        DW[Data worker<br/>market/reference ingest]
        RW[Research worker<br/>replay/backtest]
        AIW[AI worker<br/>Phase 6]
        ING[Isolated secret_ingress<br/>Phase 6 write-only path]
        CLIAPP[CLI application]
    end

    subgraph STATE[State and data stores]
        PG[(PostgreSQL 16<br/>OLTP, outbox/inbox, audit)]
        PQ[(Parquet catalog<br/>historical/research)]
    end

    U -->|HTTPS control/read API| API
    U -->|one-time write-only enrollment only| ING
    CLI -->|authorized command path| CLIAPP
    CLIAPP -->|control command| API
    API -->|command record vào operations.commands<br/>+ read projection| PG
    NODE -->|poll/claim command record<br/>từ operations.commands| PG
    API -->|alert/incident routing| ALERT
    ING -->|safe receipt/lifecycle metadata only| PG
    ING -->|direct write-only secret enrollment| VAULT

    DATA -->|raw feed/reference| DW
    DW -->|ingest/quality metadata + checkpoints<br/>raw tick ở Parquet, DB chỉ metadata/control theo master §7.6| PG
    DW -->|catalog dataset / manifest| PQ
    NODE -->|read reference/market/projection<br/>write order/risk/ledger/outbox| PG
    NODE <-->|execution / recovery query<br/>only supported modes| VENUE
    RW <-->|read catalog / write report metadata| PQ
    RW -->|candidate/report metadata only| PG
    AIW -->|sanitized read / proposal-memory write| PG
    AIW <-->|structured request only, catalog endpoint| LLM
    AIW <-->|just-in-time binding only| VAULT
~~~

Control command từ API tới trading node đi qua durable command record trong `operations.commands` (PostgreSQL) theo master §7.6: Control API persist command record; owner application handler của trading node poll/claim và thực thi transition. Không có direct API→node network call — trading_node không expose public HTTP management surface (master §4.7).

## 2. Process/container inventory

| Container / entry point | Responsibility | Identity / credential ceiling | Storage interaction | Must not do |
|---|---|---|---|---|
| apps/control_api | FastAPI control plane, command intake, read projections, health/audit. | Control DB role; no venue trade key. | Controlled operations write (durable command record vào `operations.commands` theo master §7.6), projection read. | Run strategy, submit venue order directly, hay gọi trực tiếp trading node qua network. |
| apps/trading_node | Strategy scheduler, risk, OMS, execution, ledger/reconciliation; owner handler poll/claim command record từ `operations.commands` và thực thi transition. | Trading DB role; venue credential only per approved manifest/mode. | Owned context write/read, outbox, lease, poll/claim `operations.commands`. | Public HTTP management surface (master §4.7). |
| apps/workers/data_worker | Market/reference ingestion, quality, catalog management. | Data DB role; public/testnet read credential if needed. | Market/reference write; catalog metadata. | Execution/risk/ledger write or trade secret. |
| apps/workers/research_worker | Replay, backtest, report/candidate generation. | Catalog/research role; network disabled by default. | Catalog/research output; no live write model. | Read trade credential or run execution. |
| apps/workers/ai_worker | Sanitized proposal/memory workflow at Phase 6. | Scoped machine identity; resolves one active opaque BYOK binding via short owner/connection/revision/job lease; no venue credential. | Sanitized read + policy-filtered connection metadata + ai_memory write. | Raw-key read-back, candidate binding use, execution tool, risk bypass, config promotion or arbitrary provider endpoint. |
| apps/secret_ingress | Isolated Phase 6 one-time secret enrollment routed directly to approved secret provider (có authority chính thức tại master §4.7, v2.2.0). | Re-authenticated owner scope + one-time enrollment session only; no broad DB/venue credential. | Secret provider write; safe lifecycle receipt only. | Normal Control API middleware, raw-body logging/APM, command/event/outbox persistence, body hash/fingerprint or key read-back. |
| apps/cli | Operator command client. | Caller identity through approved path. | Through command port/API; no direct privileged DB. | Bypass Control API policy. |
| Flutter dashboard | Phase 5 client rendering/control; Phase 6 may invoke protected secret-enrollment handoff. | End-user identity only. | Through Control API and isolated approved secret-ingress boundary. | Store/read-back secret, access DB/venue or own business logic. |

## 3. Storage/container ownership

| Store | Purpose | Writers | Readers | Invariants |
|---|---|---|---|---|
| PostgreSQL 16 | OLTP system of record for control, domain state, outbox/inbox, audit and ledger. | Context owner repository; whitelisted UoW only across contexts. | Process DB role with least privilege. | Context ownership, append-only audit/ledger/event controls, UUIDv7/TIMESTAMPTZ/NUMERIC rules. |
| Parquet catalog | Partitioned historical market data/research datasets. | Data worker/catalog pipeline; research output where allowed. | Research worker and approved readers. | Dataset manifest/checksum/atomicity/retention policy; not OLTP business state. |
| Generated/evidence storage | CI artifacts, reports, signed gate/task evidence. | CI/authorized operator. | Reviewers/approvers per access policy. | Hash/source link, redaction and retention policy. |

Physical schema, roles, backup and retention are defined by data/security artifacts and ADRs; this diagram does not authorize a table or data path.

## 4. Runtime wiring by mode

| Mode | Trading node execution port | Venue credential | Required behavior |
|---|---|---|---|
| BACKTEST / REPLAY | Simulator/replay adapter only. | NONE. | No external network/order. |
| PAPER_SIMULATOR | Simulator adapter. | NONE, except approved read-only input where Master permits. | Never send venue order. |
| SHADOW | Disabled/fail-closed execution adapter. | No trade credential. | Observe/decide but do not submit. |
| TESTNET | Venue execution adapter. | TESTNET_TRADE_ONLY only. | Capability/manifest/lease/reconciliation required. |
| CANARY | Venue execution adapter. | LIVE_TRADE_ONLY only under approved manifest. | Scope/cap/gate/independent review required. |
| FULL_LIVE | Not in MVP scope. | Requires future ADR/gate. | Not inferred from canary. |

## 5. Composition and dependency rules

1. Domain imports only Python standard library/shared kernel.
2. Application imports domain and ports.
3. Ports expose no vendor DTO.
4. Concrete adapter/framework code belongs under src/ai_auto_trade/adapters/<kind>/<provider>.
5. Composition root of each process is the only place that wires concrete adapter.
6. A context does not import private implementation/ORM model of another context.
7. Cross-context persistence occurs only by event/owner port or explicit whitelisted unit of work.

## 6. Deployment boundaries

- Testnet/canary target is a Linux container image pinned by digest; Windows is supported for local developer tooling only.
- One process has one primary responsibility and one machine identity.
- Each environment/account uses separate credential and database role; application never runs as DB superuser.
- AI credential binding is scoped by owner/environment/provider connection/revision/job, short-lived and not injected wholesale into the worker environment or deployment manifest. Candidate binding is validation-only; suspend/revoke invalidates new lease issuance.
- Config/deployment identity must be validated/hashed and immutable for a running deployment.
- Network/secret topology and auth provider are pending OD-005/OD-006 and ADR-0015 before Phase 3.

## 7. Observability and failure boundaries

Each process emits structured logs/metrics/traces with permitted correlation identity. A failure in UI, research or AI worker must not block trading hot path. AI telemetry includes only safe provider/model/connection-revision/policy/usage/status metadata, never key/raw prompt-response by default. Failure in execution state, lease, DB, credential, market freshness or reconciliation must follow fail-closed/safe-state policy, not silent degradation.

## 8. Review checklist

- [ ] Every process has one identity, credential ceiling and data access scope.
- [ ] No process outside trading_node can wire an execution adapter.
- [ ] Context/data ownership agrees with data architecture and architecture tests.
- [ ] Runtime mode maps to an explicit safe execution adapter.
- [ ] New container/database/language/framework has ADR before inclusion.

## 9. Nhật ký thay đổi

| Version | Date | Thay đổi | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | Tạo container/process/storage baseline theo modular monolith. | Technical Operator | Pending |
| 0.2.0 | 2026-07-31 | Thêm secret-provider/owner-scoped BYOK binding boundary cho ai_worker Phase 6. | Technical Operator | Pending |
| 0.3.0 | 2026-07-31 | Sửa API→NODE thành durable command record qua `operations.commands` (master §7.6, không direct HTTP call); sửa nhãn DW→PG thành ingest/quality metadata + checkpoints; ghi nhận authority master §4.7 v2.2.0 cho apps/secret_ingress. | Technical Operator | Pending |
