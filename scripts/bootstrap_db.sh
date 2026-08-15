#!/usr/bin/env bash
# Local development helper: create the Postgres database/role for dev.
# Assumes `docker compose up -d db` is already running.
set -euo pipefail

POSTGRES_USER="${POSTGRES_USER:-neet}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-neet_dev_password}"
POSTGRES_DB="${POSTGRES_DB:-neet_compass}"

echo "Bootstrapping database '${POSTGRES_DB}' with role '${POSTGRES_USER}'..."

docker compose exec -T db psql -U postgres -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${POSTGRES_USER}') THEN
      CREATE ROLE ${POSTGRES_USER} LOGIN PASSWORD '${POSTGRES_PASSWORD}';
   END IF;
END
\$\$;
SQL

docker compose exec -T db psql -U postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};"

echo "Done. Run 'make migrate' to apply schema."
