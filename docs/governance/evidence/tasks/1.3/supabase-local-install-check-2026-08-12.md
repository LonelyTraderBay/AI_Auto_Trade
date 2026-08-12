# Task 1.3 — Supabase Local installation check

**Date:** 2026-08-12  
**Branch:** `task/1.3-durable-submit-fake-venue`  
**Operator:** Technical Operator  
**Proposed state:** `BLOCKED`

## Scope

This check evaluates whether Supabase Local can provide the isolated PostgreSQL
test environment required by Task 1.3 without changing the approved database
authority. It does not authorize a schema migration, runtime code, or a task
status transition.

## Checks performed

| Check | Result | Evidence |
|---|---|---|
| Docker Desktop available and daemon reachable | PASS | Docker Server `29.7.2` responded to `docker info` |
| Supabase CLI available without changing project dependencies | PASS | `npx --yes supabase --version` → `2.113.0` |
| CLI command discovery | PASS | `--help` checked for `init`, `start`, `status`, and `db query` |
| Project scaffold | PASS | `npx --yes supabase init --yes` created `supabase/config.toml` and `supabase/.gitignore` |
| PostgreSQL 16 configuration | BLOCKED | `supabase start` and `supabase status` reject `db.major_version = 16` with `Invalid db.major_version: 16` |
| Older CLI compatibility probe | BLOCKED | CLI `2.64.1`, `2.70.0`, `2.76.17`, and `2.79.0` all generate PostgreSQL `major_version = 17` |

## Authority conflict

The master specification and approved persistence ADRs require PostgreSQL 16.x
as the system of record. The current Supabase Local CLI/templates require
PostgreSQL 17 and do not accept 16 in `supabase/config.toml`. Supabase Local is
therefore not a compliant replacement for the project's required PostgreSQL
16.x test authority at this time.

The generated project scaffold remains intentionally unstarted. No Supabase
container for `AI_Auto_Trade` was started, and no application credential was
persisted. An unrelated existing Docker project was not modified.

## Required owner decision

Choose one governed path before Task 1.3 can become READY:

1. Keep the approved PostgreSQL 16.x authority and provide an isolated
   PostgreSQL 16 test container/instance through `DATABASE_URL`; or
2. Approve an ADR/master amendment to move the project's pinned major version
   to PostgreSQL 17, then update the task authority and start Supabase Local.

Until one path is approved and verified with a no-skip migration/concurrency
test, the PostgreSQL blocker remains open and no implementation code may start.

