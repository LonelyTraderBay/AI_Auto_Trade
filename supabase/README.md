# Supabase Local — AI Auto Trade

This directory contains the non-secret Supabase Local configuration for the
developer environment.

## Pinned local toolchain

- Supabase CLI: `2.113.0`, invoked with `npx --yes supabase@2.113.0`
- PostgreSQL: `17.x` (the running image currently reports `17.6`)
- Project ID: `AI_Auto_Trade`
- Database: `postgres`
- Database port: `54322`
- Studio: `http://127.0.0.1:54323`

## Authority and safe commands

Alembic under `migrations/` remains the application schema authority. Do not
use `supabase db reset`, `supabase db push`, or `supabase db diff` for the
application schema unless a new approved schema workflow explicitly replaces
Alembic. The local Supabase services are development-only and must not be
exposed to external traffic or supplied with production credentials.

Start and stop the local stack from the repository root:

```powershell
npx --yes supabase@2.113.0 start
npx --yes supabase@2.113.0 stop
```

For integration tests, provide `DATABASE_URL` only to the test process. Do not
commit it to a file or shell profile.

Supabase's advisor currently reports RLS disabled on the Alembic bookkeeping
table `public.alembic_version`. Do not expose this table through client roles;
before API exposure, review whether to enable RLS with explicit policies or move
the bookkeeping table to a private schema. Do not enable RLS blindly without
policies.
