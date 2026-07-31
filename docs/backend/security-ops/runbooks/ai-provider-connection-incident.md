# RB-009 — AI provider connection incident

| Trường | Giá trị |
|---|---|
| Version / Status | 1.0.0 / DRAFT — Phase 6 only |
| Trigger / Severity | Suspected BYOK key exposure, unexpected provider/endpoint egress, cross-owner access attempt, revoke/rotation failure, provider outage, budget/quota exhaustion or invalid/unknown provider outcome / Medium to Critical by data-security impact |
| Scope / Incident commander | Affected AI connection, owner scope, environment, provider/model/profile / Security/Backup Owner; Account Owner for owner-scope decision |
| Related | ADR-0008, ADR-0016; SEC-001, SEC-002, SEC-004, OPS-001; Master §10.6, §12.1, §12.4–§12.7 |
| Safe objective | Stop new AI provider calls for affected connection/scope, preserve safe metadata, contain secret/egress exposure, and keep trading independently safe |

## 1. Preconditions and hard prohibitions

This runbook is not executable until Phase 6 gate, authentication/RBAC, secret-provider topology and provider catalog are approved. Never paste API key, secret reference resolution, authorization header, raw prompt/response, raw provider error or key fingerprint into command output, evidence, ticket, chat or this runbook.

An AI incident must not be resolved by switching silently to another provider/key. The default action is disable the affected AI connection/capability. Do not use this runbook to alter trading risk, execution, venue credential, deployment or ledger state.

## 2. Immediate containment

1. Authenticate as Security/Backup Owner; obtain Account Owner participation when owner-scope policy requires it. Record incident/correlation ID, safe connection ID, provider/model/catalog revision, environment, reason and active role — never secret material.
2. Suspend the affected `AIProviderConnection` through the approved control path. Verify new AI requests and binding lease issuance are denied for that connection and owner scope; capture only safe revision/timestamp evidence. An already departed request cannot be unsent, so cancel it if provider supports it and ensure its output is discarded if suspension/revocation wins.
3. If suspected credential compromise, revoke/disable the secret binding through the approved secret-provider procedure. If provider-side revoke cannot be verified, record status as unverified and keep connection suspended.
4. If suspected arbitrary endpoint or data egress, block the endpoint/profile/network route and suspend related catalog entry as approved. Preserve only redacted/hash-based egress metadata.
5. Do not restart `ai_worker`, re-enable AI, retry unknown provider request or use another owner’s connection as a workaround.

## 3. Classification and investigation

| Condition | Required classification/action |
|---|---|
| Key may have appeared in log/trace/fixture/DB/UI/browser | High/Critical security incident; treat credential as compromised, rotate/revoke and run secret-leak investigation. |
| Provider outage/rate limit/budget exhausted/invalid output | AI availability incident; keep AI disabled or circuit-open per policy; trading remains unaffected. |
| Unknown provider outcome after request departure | `AI_OUTCOME_UNKNOWN`; no blind retry/fallback; inspect safe request metadata and provider status when allowed. |
| Cross-owner connection/binding access attempt | Authorization/security incident; deny, investigate actor/session/machine scope and preserve audit evidence. |
| Arbitrary endpoint/model/egress policy bypass attempt | Security incident; block profile/route, verify catalog and adapter integrity. |

Collect only allowed evidence: audit lifecycle records, actor/role, connection/provider/model/catalog/adapter/policy revision, normalized error/status, budget reservation/usage metadata, network/egress decision, timestamps and correlation IDs. Confirm whether sanitized prompt/response retention was enabled by approved policy before accessing any content.

## 4. Recovery / rotation

1. For a replacement key, start a rotation command with no key, then create a new candidate opaque binding/revision using one-time isolated write-only/no-store enrollment; do not overwrite, hash, fingerprint or reveal the old key.
2. Validate with a bounded synthetic/sanitized probe under the correct owner/egress/budget policy.
3. Account Owner and Security/Backup Owner review the validation, catalog status, egress policy, usage/budget state and incident findings. Re-authenticate for activation.
4. Atomically activate the new revision only after approval; retain the old active binding until cutover, then disable/revoke it per policy. If candidate validation fails, destroy candidate and keep old binding active. Verify `ai_worker` can resolve only the new active binding for the authorized scope.
5. Run negative checks: old/revoked binding denied, cross-owner use denied, raw secret absent from safe telemetry and no execution capability exists.

## 5. Verification and close

Before close, record:

- affected scope/connection/provider/model/catalog/adapter and policy revisions;
- containment/revoke/rotation result without raw secret;
- whether data egress occurred, its approved classification and any provider-side evidence available;
- budget/quota reconciliation and any unknown outcome disposition;
- proof that AI remains isolated from trading and no silent fallback happened;
- binding-lease invalidation/recheck and any in-flight request disposition;
- approval to create and review a replacement connection lifecycle, or explicit decision to keep connection/provider disabled;
- follow-up task/ADR/catalog/policy change and due date.

Escalate to Account Owner/Security/Backup Owner if provider cannot revoke, egress cannot be bounded, raw secret may have leaked, cross-owner use is confirmed or adapter/catalog integrity is uncertain. No Phase 6 gate may pass while such a condition remains unresolved.
