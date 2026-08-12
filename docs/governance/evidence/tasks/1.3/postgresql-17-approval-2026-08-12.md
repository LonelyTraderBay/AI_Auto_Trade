# ADR-0003 amendment — PostgreSQL 17 approval record

| Field | Value |
|---|---|
| Decision ID | `GOV-ADR-0003-PG17-20260812-111553` |
| ADR | ADR-0003 — PostgreSQL/Parquet persistence strategy |
| Decision | `APPROVE` |
| Approver | Account Owner |
| UTC timestamp | `2026-08-12T11:15:53Z` |
| Scope | PostgreSQL system-of-record major version 16.x → 17.x |
| Reason | Supabase Local CLI currently provides the supported local stack on PostgreSQL 17; this enables a reproducible Docker-based local database for Task 1.3. |

## Approved change

PostgreSQL 17.x is approved as the project's system-of-record major version for
local, test, paper/testnet and future isolated environments, replacing the
previous 16.x pin. The change is a compatibility/toolchain decision only.

The following invariants are unchanged and remain non-waivable:

- PostgreSQL remains the sole OLTP system of record; Supabase Local is the local
  Docker distribution of that database and its development services.
- Decimal domain values map to `NUMERIC(38,18)`; API/event values remain strings.
- IDs remain application-generated UUIDv7; timestamps remain UTC `TIMESTAMPTZ`.
- Transaction/isolation/locking, append-only audit/financial history,
  no-blind-retry for `UNKNOWN`, least privilege and fail-closed rules remain
  governed by the existing ADRs.
- No external venue, live credential, LLM execution path, ledger activation or
  production deployment is authorized by this amendment.

## Required follow-through

1. Synchronize master, ADR, data/architecture standards, task authority and
   documentation indexes to PostgreSQL 17.x.
2. Pin the Supabase CLI version used by the local workflow and commit only
   non-secret `supabase/config.toml`.
3. Start Supabase Local with Docker, verify the server version is PostgreSQL 17,
   apply only approved migrations, and expose `DATABASE_URL` ephemerally to the
   integration test process.
4. Keep Task 1.3 `BLOCKED` until migration/concurrency tests run without skip
   and the resulting evidence is reviewed.

This record approves the version amendment; it does not approve a migration,
runtime implementation, task transition or production capability.

