# Template — Task Card readable render

| Thuộc tính | Giá trị |
|---|---|
| Document ID | TMP-TASK-001 |
| Artifact type | Reusable task-card template |
| Phiên bản | 0.1.0 |
| Trạng thái | IN_REVIEW |
| Owner | Technical Operator |
| Approver | Account Owner (pending) |
| Ngày hiệu lực | Chưa hiệu lực |
| Rà soát gần nhất | 2026-07-31 |
| Tham chiếu chuẩn | AI_AUTO_TRADE_MASTER_SPEC.md §0.2, §13.2, §15.4, §16.1–§16.5 và Phụ lục C.3 |
| Related requirements | NFR-OPS-001, NFR-SEC-001, SEC-AUD-001, SEC-SUP-001 |
| Related ADR | ADR-0014 |

> Canonical task authority là YAML tại tasks/active/<TASK_ID>.yaml hoặc tasks/completed/<TASK_ID>.yaml, validate bằng contracts/config/task-card.v1.schema.json. Markdown này chỉ là readable render/template và không thay YAML authority.

## 1. Cách sử dụng

1. Tạo YAML từ schema và copy các field vào render này.
2. Không bắt đầu task nếu requirement, ADR, contract, allowed path, reviewer, acceptance command hoặc expiry thiếu.
3. Status hợp lệ: READY, IN_PROGRESS, REVIEW, DONE, BLOCKED.
4. Khi BLOCKED, ghi blocker/evidence và không code best guess.
5. Khi DONE, ghi command thật đã chạy, exit/result, evidence path và review; không tự claim pass.

## 2. Canonical YAML skeleton

~~~yaml
task_id: "<TASK_ID>"
phase: "<0.0|0|1|2|3|4|5|6>"
status: "READY"
owner: "<role or actor>"
reviewer: "<role or actor independent for applicable scope>"
expiry_at: "YYYY-MM-DDTHH:MM:SSZ"
branch_pattern: "task/<TASK_ID>-*"
references:
  requirements: ["<FR-NFR-SEC-ID>"]
  adrs: ["ADR-<NNNN>"]
  contracts: ["<canonical contract path or empty list>"]
goal: "<single bounded objective>"
non_goals:
  - "<explicitly excluded work>"
preconditions:
  - "<approved artifact, command or decision>"
blockers: []
allowed_globs:
  - "<allowed path glob>"
forbidden_globs:
  - "src/**"
  - "migrations/**"
impact:
  database: false
  api: false
  event: false
  config: false
  dependency: false
  security: false
acceptance_criteria:
  - "<observable condition>"
required_commands:
  - "<exact command available in this phase>"
evidence_path: "docs/governance/evidence/tasks/<TASK_ID>/"
gate_impact: "none"
rollback_or_forward_fix: "<safe rollback/forward-fix procedure>"
known_risks:
  - "<risk or empty list>"
assumptions:
  - "<allowed assumption or empty list>"
waiver_id: null
~~~

## 3. Readable render

### Identity and ownership

| Field | Value |
|---|---|
| Task ID | <TASK_ID> |
| Phase / status | <phase> / <status> |
| Owner / reviewer | <owner> / <reviewer> |
| Expiry (UTC) | <timestamp> |
| Branch / PR binding | <branch pattern and PR metadata> |
| Gate impact | <none or gate ID/name> |

### Scope

**Goal:** <single bounded objective>

**Non-goals:**

- <item>

**Preconditions:**

- <approved input/decision>

**Blockers:**

- <item or none>

### Authority and impacts

| Field | Value |
|---|---|
| Requirement IDs | <FR/NFR/SEC list> |
| ADR IDs | <list> |
| Contract/schema paths | <list> |
| Database/API/event/config/dependency/security impact | <true/false with explanation> |
| Allowed paths | <glob list> |
| Forbidden paths | <glob list> |

### Acceptance and verification

| Acceptance criterion | Verification command/procedure | Expected evidence |
|---|---|---|
| <criterion> | <exact command or review procedure> | <path/hash/result> |

### Safety, risk and forward-fix

| Field | Value |
|---|---|
| Known risks | <list> |
| Assumptions | <list> |
| Waiver ID / expiry | <ID or none> |
| Rollback or forward-fix | <procedure> |
| Evidence path | <path> |

### Execution report

| Field | Value |
|---|---|
| Actual files changed | <list from diff> |
| Allowed-path check | PASS / FAIL with evidence |
| Commands run | <command, UTC time, exit result> |
| Tests/validation result | <result/artifact> |
| Contract/migration impact | <none or detail> |
| Open risk/blocker | <none or detail> |
| Reviewer decision | APPROVED / returned / BLOCKED |

## 4. Validation rules

- CI validates YAML schema, task status/expiry/reviewer and PR Task-ID binding before comparing diff against allowed_globs/forbidden_globs.
- Markdown prose, commit message and self-report never override YAML allowlist.
- New dependency, migration, public contract, risk/OMS/ledger/security/deployment impact needs explicit impact flag, allowed path, applicable reviewer and approval.
- No Any, type ignore, noqa, broad/bare except, skip/xfail or safety TODO without an unexpired waiver ID in the task.

## 5. Change log

| Version | Date | Change | Owner | Approval |
|---|---|---|---|---|
| 0.1.0 | 2026-07-31 | Initial readable task-card template. | Technical Operator | Pending |
