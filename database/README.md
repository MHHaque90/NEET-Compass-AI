# database/

SQL material that does not belong in Alembic migrations:

- `init/` — optional first-start SQL for the Postgres container (currently
  empty; the schema needs no extensions — `gen_random_uuid()` is core in
  PostgreSQL 13+).

Migrations live in [`backend/alembic`](../backend/alembic). Seed/backfill
scripts that operate on real data should live in `scripts/` or the ETL layer.
