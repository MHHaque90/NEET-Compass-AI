#!/usr/bin/env bash
# Container entrypoint: apply migrations, then start the API.
set -euo pipefail

echo "[entrypoint] Waiting for database..."
python - <<'PY'
import os
import time
import psycopg
url = os.environ["DATABASE_URL"].replace("postgresql+psycopg://", "postgresql://")
for attempt in range(60):
    try:
        with psycopg.connect(url, connect_timeout=2):
            break
    except Exception:
        time.sleep(2)
else:
    raise SystemExit("database did not become ready in time")
PY

echo "[entrypoint] Applying migrations..."
alembic -c /app/alembic.ini upgrade head

echo "[entrypoint] Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
