# Deployment Guide

> This guide covers deploying NEET Compass AI in production using Docker
> Compose. For cloud-specific instructions (AWS ECS, GCP Cloud Run), see
> the cloud deployment playbooks in `deploy/`.

---

## Architecture Overview

```
                        ┌─────────────────────┐
                        │   Load Balancer     │
                        │  (AWS ALB / nginx)  │
                        └────────┬────────────┘
                                 │
                 ┌───────────────┼──────────────┐
                 ▼               ▼              ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │   Backend   │ │   Frontend  │ │   Worker    │
        │ (FastAPI)   │ │ (React)     │ │ (Celery)    │
        │             │ │             │ │             │
        └──────┬──────┘ └─────────────┘ └──────┬──────┘
               │                               │
               ▼                               ▼
        ┌─────────────┐                ┌─────────────┐
        │ PostgreSQL  │                │   Redis     │
        │ (Primary)   │◄──────────────►│ (Broker)    │
        └─────────────┘                └─────────────┘
                │                         │
                ▼                         ▼
        ┌─────────────┐           ┌─────────────┐
        │  Backups    │           │  Celery     │
        │  (S3)       │           │  Results    │
        │             │           │  (Postgres) │
        └─────────────┘           └─────────────┘
```

---

## Prerequisites

- Docker Engine 24.x+
- Docker Compose v2.20+
- A domain name with DNS pointing to your server
- SSL certificate (we use Let's Encrypt via nginx-proxy)

---

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|---|---|---|
| `POSTGRES_USER` | PostgreSQL user | `neetcompass` |
| `POSTGRES_PASSWORD` | PostgreSQL password | *(generated)* |
| `POSTGRES_DB` | PostgreSQL database name | `neet_compass` |
| `POSTGRES_HOST` | PostgreSQL host | `postgres` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT signing secret | *(32+ char string)* |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `API_BASE_URL` | Public API URL | `https://api.neetcompass.in` |
| `FRONTEND_URL` | Public frontend URL | `https://neetcompass.in` |

### Optional Environment Variables

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `WORKER_CONCURRENCY` | `4` | Celery ETL worker concurrency |
| `ML_WORKER_CONCURRENCY` | `1` | Celery ML worker concurrency |
| `DB_POOL_SIZE` | `20` | SQLAlchemy connection pool size |
| `RATE_LIMIT_ENABLED` | `true` | Enable/disable rate limiting |

Create a `.env` file from the template:

```bash
cp .env.example .env
# Edit .env with your values
```

### Generating Secrets

```bash
# PostgreSQL password
openssl rand -base64 24

# JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Quick Start (Docker Compose)

### 1. Clone the repository

```bash
git clone https://github.com/neetcompass/neet-compass-api.git
cd neet-compass-api
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your production values
```

### 3. Start services

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 4. Run database migrations

```bash
docker compose exec backend alembic upgrade head
```

### 5. Verify deployment

```bash
# Health check
curl https://api.neetcompass.in/health

# Expected response
{"status": "healthy", "postgres": true, "redis": true}
```

---

## Data Persistence

### PostgreSQL

Volume mount: `./postgres-data:/var/lib/postgresql/data`

**Backup:**
```bash
docker compose exec postgres pg_dump -U neetcompass neet_compass > backup.sql
```

**Restore:**
```bash
docker compose exec postgres psql -U neetcompass neet_compass < backup.sql
```

### Automated Backups

A cron job backs up PostgreSQL daily to S3:

```bash
# Runs at 2 AM daily
0 2 * * * docker compose exec postgres pg_dump -U neetcompass neet_compass | \
  gzip | aws s3 cp - s3://neetcompass-backups/db-$(date +%Y-%m-%d).sql.gz
```

---

## Scaling

### Backend API

Scale horizontally behind a load balancer:

```bash
docker compose up -d --scale backend=4 --scale nginx=1
```

### Celery Workers

Scale workers independently by queue:

```bash
# Scale ETL workers (default queue)
docker compose up -d --scale celery-etl=4

# Scale ML workers
docker compose up -d --scale celery-ml=2

# Scale batch workers
docker compose up -d --scale celery-batch=2
```

### Database

For production with >10k daily users:
- Use a managed PostgreSQL service (AWS RDS, GCP Cloud SQL).
- Enable read replicas for reporting queries.
- Set `CONN_MAX_AGE=60` in Django (if using Django admin).

---

## Monitoring & Observability

### Logging

All services log to stdout/stderr, structured as JSON:

```json
{
  "timestamp": "2026-08-10T12:00:00Z",
  "level": "INFO",
  "service": "backend",
  "event": "prediction_completed",
  "user_id": "550e8400-...",
  "prediction_id": "550e8400-...",
  "duration_ms": 42
}
```

### Metrics (Prometheus)

Exposed at `/metrics` on the backend and workers. Key metrics:

- `http_requests_total` — request count by endpoint and status.
- `prediction_duration_seconds` — histogram of prediction latency.
- `celery_task_duration_seconds` — task execution time.
- `database_query_duration_seconds` — DB query latency.
- `active_connections` — current DB connection pool size.

### Health Checks

| Endpoint | Frequency | Purpose |
|---|---|---|
| `/health` | 30s | Liveness probe (app + DB + Redis) |
| `/health/ready` | 10s | Readiness probe (migration status) |
| `/metrics` | — | Prometheus scraping |

### Alerts

| Alert | Threshold | Action |
|---|---|---|
| API latency >95th percentile | >500ms for 5 min | Scale backend workers |
| DB connection pool >90% | >18/20 connections | Alert on-call |
| ETL error rate | >5% for 1 hour | Pause ETL, notify ML team |
| Redis memory | >80% | Scale Redis or evict old keys |

---

## Security

### Network

- Backend listens on port 8000 (internal only in production).
- Nginx terminates TLS and proxies to backend.
- Redis should not be publicly accessible.
- PostgreSQL should only accept connections from backend/worker containers.

### JWT

- Access tokens expire in 15 minutes.
- Refresh tokens expire in 30 days and are rotated on each use.
- Token revocation list stored in `auth_events` table (checked on each request).
- Signing algorithm: HS256 (rotate to RS256 for multi-region deployments).

### Headers

Nginx adds security headers:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

---

## Rollback Procedure

If a deployment fails:

```bash
# Stop new containers
docker compose down

# Restore to previous version
git checkout <previous-tag>

# Restore database if migration was destructive
aws s3 cp s3://neetcompass-backups/db-<date>.sql.gz .
gunzip db-<date>.sql.gz
docker compose up -d postgres
docker compose exec postgres psql -U neetcompass neet_compass < db-<date>.sql
docker compose up -d -d

# Verify
curl https://api.neetcompass.in/health
```

---

## Deployment Checklist

- [ ] `.env` file populated with production secrets
- [ ] SSL certificate configured and valid
- [ ] PostgreSQL data volume exists and is writable
- [ ] Redis container is running
- [ ] Alembic migrations applied (check `alembic_version` table)
- [ ] Health check returns 200
- [ ] Swagger docs accessible at `/docs`
- [ ] Monitoring stack (Prometheus + Grafana) configured
- [ ] Backup cron job scheduled
- [ ] CDN configured for frontend static assets
- [ ] Rate limiter enabled and tested
- [ ] Security headers verified via securityheaders.com
