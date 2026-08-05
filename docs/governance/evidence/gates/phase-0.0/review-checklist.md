# Review checklist — Phase 0.0

| Thuộc tính | Giá trị |
|---|---|
| Checklist ID | GATE-0.0-CHECK-001 |
| Phiên bản | 0.2.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Required approver | Account Owner (pending) |
| Ngày tạo / Rà soát gần nhất | 2026-07-31 / 2026-08-02 |
| Related gate | [GATE-0.0-001](gate-record.md) |
| Related master | §1.5, Phase 0.0, §15 |
| Change summary | 0.2.0 (2026-08-02): bổ sung header Version/Rà soát/Change summary theo GOV-DOC-001 §3; ghi rõ tham chiếu SEC-ACCESS-001 tại mục 0.0.8 (tránh nhầm title-ID SEC-002 với requirement ID). |

## 0.0.1 Governance and product

- [ ] `DOCS_INDEX` links to every artifact and matches its status.
- [ ] Document-control, RACI, RAID and traceability are reviewed.
- [ ] MVP, non-goals, FR/NFR/SEC IDs and glossary are accepted.
- [ ] No requirement claims unapproved venue, account, legal status or risk value.

## 0.0.2 Architecture and toolchain

- [ ] C4 context/container and runtime sequences preserve all master boundaries.
- [ ] Language, toolchain, dependency and repository policy are accepted.
- [ ] ADR-0001, ADR-0002 and ADR-0014 have Account Owner decision/evidence.
- [ ] No source/runtime skeleton has been created before Phase 0 gate.

## 0.0.3 Domain and data

- [ ] Canonical domain, OMS, risk and accounting documents agree with master invariants.
- [ ] ERD, dictionary, database standards and transaction design identify Task 0.3 tables/constraints.
- [ ] ADR-0003, 0004, 0005, 0007, 0011 and 0012 have Account Owner decision/evidence.
- [ ] All accounting/risk values still requiring owner input are explicitly blocked, not invented.

## 0.0.4 Contracts and security

- [ ] Contract registry includes OpenAPI, JSON Schema, error catalog and fixture paths.
- [ ] JSON schemas parse and fixtures conform; OpenAPI parses with its documented validator.
- [ ] Threat, access, secret, auth and SLO/alert documents are reviewed.
- [ ] No real credential, provider configuration, venue integration or external command is present.

## 0.0.5 Delivery controls

- [ ] Repository, Python, test, CI/CD and AI coding policies are reviewed.
- [ ] Task-card schema and active Phase 0.0 task YAML validate.
- [ ] CI design binds PR Task-ID to machine-readable allowlist/expiry/reviewer.
- [ ] ADR/template/gate record fields match master Appendix C.

## 0.0.6 AI provider-neutral/BYOK baseline (Phase 6 deferred)

- [ ] Master, FR/NFR/SEC traceability, ADR-0016 and ARC-AI-001 agree: OpenAI is optional; user only selects approved API-key provider/model/policy-profile catalog entries.
- [ ] BYOK raw key has exactly one isolated write-only/no-store enrollment path; it is absent from durable command/event/audit/log/proxy/WAF/APM/fixture/config/database metadata, never body-hashed/fingerprinted and cannot be read back.
- [ ] Owner scope, re-auth, dual-role validate/activate, emergency suspend/revoke, provider/model/endpoint/policy-profile allowlist, data-egress/DNS/redirect policy, budget/quota, rotation/revoke lease, outage/unknown-outcome and no-silent-fallback behavior are reviewable.
- [ ] AI remains proposal-only, off the trading hot path, without venue credential or execution tool; Task 0.0.6 remains REVIEW and Phase 6 remains blocked until ADR/OD/security evidence is approved.

## 0.0.7 Register, standard và template bổ sung sau pack ban đầu

- [ ] Waiver register và compliance register được review; không waiver nào đụng safety invariant.
- [ ] Logging standard và versioning/release policy nhất quán với CI/CD design và repository conventions.
- [ ] Incident-record template khớp master Phụ lục C và escalation flow của runbook.
- [ ] Runbook index phủ RB-001..RB-012; 3 runbook mới (venue-rate-limit, outbox-dlq-backlog, clock-drift) được review.
- [ ] Root controls (README/AGENTS/SECURITY/CONTRIBUTING/CODEOWNERS) khớp DOCS_INDEX và thực tế repo.
- [ ] Task card 0.1 validate schema và giữ BLOCKED cho tới khi gate pass.

## 0.0.8 Frontend pack (chỉ là input Phase 5/6)

- [ ] FE pack nhất quán với openapi.yaml, master §11.5 và SEC-ACCESS-001 (access-control-matrix, title SEC-002).
- [ ] Chưa có frontend code.
- [ ] FR-FE-001..007 đã đăng ký trong requirements-traceability với gate Phase 5/6.
- [ ] GAP register (FE-SCREEN-001 §4) được theo dõi qua OD-010/I-005.

## Final decision

Only after every checkbox is backed by a dated evidence path may Account Owner change `GATE-0.0-001` to `PASS`. Any material amendment to an approved Phase 0.0 artifact reopens the affected section and may revoke the gate.
