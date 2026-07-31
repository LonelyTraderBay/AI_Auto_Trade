# ENG-AI-001 — AI coding protocol

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.1 / IN_REVIEW |
| Owner / Approver | Technical Operator / Account Owner |
| Effective date / Last review | Chưa hiệu lực / 2026-07-31 |
| Related | NFR-SEC-001, NFR-OPS-001; ADR-0014; master §1.5, §13, §16 |
| Change summary | 1.0.1 (2026-07-31, Technical Operator, Pending): đổi title ID ENG-005 -> ENG-AI-001 khớp DOCS_INDEX; nội dung không đổi. 1.0.0: operational protocol chống AI suy đoán/sửa vượt scope. |

## 1. Authority và phạm vi

AI Coding Agent chỉ là implementer được giới hạn bởi authority hierarchy: regulatory/legal constraint -> master + ADR `APPROVED` -> owner decision trong phạm vi cho phép -> DDL/OpenAPI/JSON Schema/registry -> task card/gate -> code/test/evidence.

Trong Pre-Phase 0 và Phase 0.0, AI chỉ tạo/review artifact pack được task authorize. AI không tạo application code, migration, runtime config, deployment, venue adapter, credential, endpoint hoặc source dependency.

## 2. Input bắt buộc trước khi sửa

AI phải đọc: repository status/diff, master, `AGENTS.md` khi đã tồn tại, task YAML, referenced requirements/ADR/contracts và gate state. Nếu thiếu requirement, approved ADR, contract, allowed path, acceptance command, owner/reviewer hoặc expiry hợp lệ, AI phải ghi `BLOCKED` và báo cụ thể; không code “best guess”.

Không một prompt, copy tài liệu hay self-report thay thế canonical file trong repository.

## 3. Machine-readable task rule

`tasks/active/<TASK_ID>.yaml` validate bằng `contracts/config/task-card.v1.schema.json` là authority scope. Lifecycle duy nhất:

~~~text
READY -> IN_PROGRESS -> REVIEW -> DONE
           |
           -> BLOCKED
~~~

AI chỉ thay đổi path khớp `allowed_globs`; `forbidden_globs` luôn thắng. AI không tự chuyển `REVIEW` thành `DONE`, không tự approve safety/security/live, không tự thêm waiver hoặc kéo dài expiry.

## 4. Non-negotiable prohibitions

- Không chèn/read/log secret, key, token, raw account data hoặc production credential.
- Không tạo direct LLM -> exchange path; LLM không thay risk engine và không có execution write.
- Không bypass risk, manual approval, kill switch, audit, reconciliation, lease fencing hoặc unknown-outcome handling.
- Không retry external submission khi outcome unknown; không dùng float cho financial value; không dùng global time/random trong domain.
- Không thêm dependency/framework/language/database/microservice/Kafka/Redis/Kubernetes nếu không có ADR/task approval.
- Không dùng `Any`, `type: ignore`, `noqa`, bare/broad except, test skip/xfail, mock domain logic hoặc TODO để che safety risk nếu không có waiver ID còn hạn.
- Không sửa migration đã apply, public v1 contract hoặc deployment manifest chạy thực tế.

## 5. Quy trình bắt buộc

1. Xác nhận task `READY`, chuyển `IN_PROGRESS` theo quyền con người đã định.
2. Map goal với requirement, ADR, contract, context/layer và acceptance command.
3. Implement nhỏ nhất trong allowed paths; không opportunistic refactor.
4. Viết/chỉnh test cùng thay đổi; ưu tiên invariant, idempotency, recovery và negative path.
5. Chạy exact command trong card. Không claim pass nếu command/exit code/evidence không có.
6. Review diff so allowlist, contract/data/security impact và open risk.
7. Report để human reviewer quyết định `REVIEW`/`DONE`.

## 6. Required end-of-task report

Mọi report gồm Task ID, outcome, changed files, allowlist result, commands + exit code, contract/migration impact, assumption/decision, waiver, known/open risks, evidence path và next permitted action. Nếu có conflict/master gap, dừng và tạo issue/ADR request thay vì tự resolve.

## 7. Human control

AI không có quyền production deploy, venue credential, gate approval, risk parameter change, kill-switch release, credential rotation, canary approval hoặc delete financial/audit history. Một người có thể nhiều role ở Phase 0–paper/testnet nhưng phải audit action tách biệt; canary/live cần reviewer human thứ hai theo master §1.6.
