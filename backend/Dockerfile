# NEET Compass AI - backend runtime image
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ─── Dependencies ──────────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ─── Application ───────────────────────────────────────────────────────────────
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./alembic.ini
COPY scripts ./scripts
COPY etl ./etl

RUN chmod +x /app/scripts/entrypoint.sh && mkdir -p /data/cache /data/processed /data/exports

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
