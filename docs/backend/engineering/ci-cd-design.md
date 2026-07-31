# ENG-CI-001 — CI/CD design và quality gates

| Trường | Giá trị |
|---|---|
| Version / Status | 1.1.0 / IN_REVIEW |
| Owner / Approver | Technical Operator / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | NFR-OPS-001, NFR-SEC-001; ADR-0012, ADR-0014; Phase 0.0.5 |
| Change summary | 1.1.0 (2026-07-31, Technical Operator, Pending): đổi title ID ENG-004 -> ENG-CI-001; thêm trigger matrix DRAFT, xác nhận secret scanning tool detect-secrets, thêm dòng evidence retention theo ADR-0013. 1.0.0: thiết kế pipeline và enforcement trước khi workflow implementation được tạo ở Task 0.1/0.2. |

## 1. Phạm vi

Phase 0.0 chỉ ghi thiết kế và validate artifact. Chưa có `.github/workflows`, build image, deploy, secret integration hoặc production credential. Pipeline thực tế được Task 0.1/0.2 tạo từ task card đã `READY`.

## 2. Trigger và principle

- Pull request vào `main`, push branch được phép và release/tag sau này đều chạy check phù hợp.
- `main` protected; merge cần required checks, review record và Task-ID binding.
- CI dùng ephemeral environment, không secret thật, không venue network/trade credential và không database persistent.
- Pipeline chạy cùng command profile với local; không tạo command CI riêng để lách local gate.
- Build/release artifact bất biến: commit SHA, lock checksum, SBOM, build digest và manifest link là evidence bắt buộc.

### Trigger matrix (DRAFT — cần phê duyệt)

| Trigger | Checks |
|---|---|
| PR | lint, type check, test, schema validation, task-card allowlist, secret scan |
| `main` (merge) | như PR + migration upgrade (từ Task 0.3) + contract compatibility + evidence upload |
| tag `v*` | như `main` + SBOM (syft, định dạng CycloneDX) + image build/scan khi image tồn tại + release-note generation |

## 3. Stage design

~~~text
preflight: task-card schema + expiry + branch/PR binding + changed-path allowlist
  -> document/contract validation
  -> format -> lint -> type check -> architecture rules
  -> unit/property/state-machine
  -> schema compatibility
  -> migration upgrade (từ Task 0.3)
  -> integration/contract
  -> replay/golden/chaos theo task
  -> secret/dependency/SAST/container scan
  -> build immutable artifact (khi có runtime)
  -> publish evidence; never auto-promote deployment
~~~

Một stage fail chặn stage downstream và merge. Retry CI không được thay đổi dependency, fixture, task scope hoặc waiver.

## 4. Task-card allowlist enforcement

CI lấy Task ID từ PR metadata/branch theo `branch_pattern`, đọc `tasks/active/<TASK_ID>.yaml`, validate bằng `contracts/config/task-card.v1.schema.json`, kiểm status/expiry/owner/reviewer rồi so Git diff với `allowed_globs` và `forbidden_globs`. Markdown, commit message và AI self-report không thay thế authority YAML.

Rules:

- `forbidden_globs` luôn thắng.
- File generated chỉ sửa qua source contract/template trong allowed scope.
- Migration, API/event/config public, dependency, security/deployment/risk/OMS/ledger chỉ được phép nếu impact flag, reference và reviewer tương ứng xuất hiện trong card.
- Unknown Task ID, expired card, malformed YAML hoặc diff ngoài scope là FAIL, không auto-fix.

## 5. Contract, security và supply-chain checks

- Validate OpenAPI 3.1, JSON Schema 2020-12, fixture và cross-reference contract registry.
- Check contract compatibility: không xóa/đổi semantics v1; required/new enum/event major change cần v2 + plan.
- Detect secrets, dependency vulnerabilities, license policy, SAST; image scan/SBOM chỉ từ khi có image. Secret scanning tool chuẩn là `detect-secrets` (master §13.1).
- Block mutable image tags, unpinned production dependency, raw secret in diff/test artifact, unsupported public schema reference và contract registry drift.
- Do not run external venue call, real credential validation, trade action or LLM request in CI.

## 6. Evidence, retention và approvals

CI lưu test report, coverage summary, schema compatibility, migration result, security scan, source/lock/image digest, task allowlist result và links/checksums. Gate record trỏ chính xác artifact, runner và UTC time.

CI evidence/artifact retention theo ADR-0013 class "evidence"; cho đến khi ADR-0013 được approve, giữ tối thiểu đến khi phase gate liên quan PASS cộng thêm 1 phase.

Deployment không auto-promote từ CI. Paper/testnet/canary cần manifest immutable, human approval đúng role, pre-enable health/lease/reconciliation checks và gate record riêng. Waiver phải có ADR, scope, compensating control, approver, expiry; CI fail khi hết hạn. Safety invariant không waive được.

## 7. Bootstrap acceptance

Task 0.0.5 chỉ cần có design này, task-card schema/fixture và một procedure validate được ghi evidence. Task 0.1/0.2 phải chuyển design thành workflow/commands thực tế, không claim pipeline xanh trước khi command tồn tại và exit code được lưu.

