# Docker build artifacts

This directory holds Docker-specific configuration.

- `postgres/init/` — optional SQL executed once on first container start.
  The current schema needs no extensions (`gen_random_uuid()` is core in
  PostgreSQL 13+), so this is reserved for future needs (e.g. `pgvector`
  for semantic search over counselling documents).
