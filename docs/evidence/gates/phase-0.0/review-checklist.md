# Review checklist — Phase 0.0

| Thuộc tính | Giá trị |
|---|---|
| Checklist ID | GATE-0.0-CHECK-001 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Required approver | Account Owner |
| Related gate | [GATE-0.0-001](gate-record.md) |
| Related master | §1.5, Phase 0.0, §15 |

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

## Final decision

Only after every checkbox is backed by a dated evidence path may Account Owner change `GATE-0.0-001` to `PASS`. Any material amendment to an approved Phase 0.0 artifact reopens the affected section and may revoke the gate.
