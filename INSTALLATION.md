# Installation Guide

## Prerequisites

### For Local Development

- **Python 3.12+** — https://www.python.org/downloads/
- **Docker** — https://docs.docker.com/get-docker/
- **Docker Compose** (usually included with Docker Desktop)
- **Make** — (optional, for convenience scripts)

### For Production Deployment

- **Linux server** (Ubuntu 22.04 LTS recommended)
- **Docker Engine** (not Docker Desktop)
- **Docker Compose plugin**
- **At least 4GB RAM, 20GB disk** (minimum)
- **SSD storage** for database performance
- **Backups** — automated, encrypted, off-site

## Quick Start (Local Development)

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/neet-compass/neet-compass-ai.git
cd neet-compass-ai

# 2. Set environment variables
cp .env.example .env
# Edit .env if needed (defaults work for local dev)

# 3. Start all services
docker compose up -d --build

# 4. Apply database migrations
docker compose run --rm backend alembic upgrade head

# 5. Seed lookup tables
docker compose run --rm backend python scripts/seed_lookup_tables.py

# 6. Access the API
# http://localhost:8000/docs (interactive API docs)
# http://localhost:8000/health (health check)
```

### Option 2: Local Development (No Docker)

```bash
# 1. Clone and enter directory
git clone https://github.com/neet-compass/neet-compass-ai.git
cd neet-compass-ai

# 2. Start PostgreSQL and Redis
make db-up

# 3. Set up Python environment
make setup  # Creates .venv and installs dev dependencies

# 4. Apply migrations
make migrate

# 5. Seed lookup tables
make seed

# 6. Run the application
make dev
# Server starts at http://localhost:8000
```

## Production Deployment

### Option 1: Docker Compose (Single Node)

```bash
# 1. Clone the repository
git clone https://github.com/neet-compass/neet-compass-ai.git
cd neet-compass-ai

# 2. Create production environment
cp .env.example .env.production

# 3. Edit .env.production with production values:
#    - POSTGRES_PASSWORD: strong password (min 32 chars)
#    - SECRET_KEY: strong random key
#    - APP_ENV: production
#    - CORS_ORIGINS: your domain(s)

# 4. Build and deploy
docker compose -f docker-compose.yml up -d --build

# 5. Run migrations
docker compose exec backend alembic upgrade head

# 6. Set up automated backups
# See section below
```

### Option 2: Kubernetes (Advanced)

The application is containerized and can be deployed to any Kubernetes
cluster. A Helm chart is planned for Phase 3.

**Basic steps:**
1. Build and push the backend image to your registry
2. Create a PostgreSQL instance (CloudSQL, RDS, or self-hosted)
3. Create a Redis instance
4. Deploy the backend as a Deployment with proper health checks
5. Configure Ingress with TLS termination
6. Set up secrets via Kubernetes Secrets or sealed-secrets

### Production Security Checklist

- [ ] Generate strong `POSTGRES_PASSWORD` (min 32 chars)
- [ ] Generate strong `SECRET_KEY` (min 50 chars)
- [ ] Set `APP_ENV=production`
- [ ] Configure CORS origins explicitly
- [ ] Enable HTTPS (TLS 1.2+) via load balancer
- [ ] Enable SSL for database connections
- [ ] Run containers as non-root user
- [ ] Set up automated database backups
- [ ] Configure log retention and rotation
- [ ] Set up monitoring and alerting
- [ ] Review and apply PostgreSQL security best practices
- [ ] Keep Docker images updated

### Database Backups

#### Using pg_dump

```bash
# Automated backup script
#!/bin/bash
set -euo pipefail

BACKUP_DIR="/data/backups"
DATE=$(date +%Y%m%d_%H%M%S)
PG_CONTAINER=$(docker ps -q -f name=neet-db)

# Create backup
docker exec -t $PG_CONTAINER \
  pg_dump -U neet neet_compass > "$BACKUP_DIR/backup_$DATE.sql"

# Compress
gzip "$BACKUP_DIR/backup_$DATE.sql"

# Keep last 7 days
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +7 -delete

# Health check
if [ $? -eq 0 ]; then
    echo "Backup successful: backup_$DATE.sql.gz"
else
    echo "Backup failed!" | tee -a /var/log/backup.log
    exit 1
fi
```

#### Using Docker Volume Snapshot

```bash
# Stop the database container
docker compose stop db

# Snapshot the volume
docker run --rm \
  -v neetcompass_pgdata:/var/lib/postgresql/data \
  -v /data/backup:/backup \
  alpine tar czf /backup/pgdata_$(date +%Y%m%d).tar.gz /var/lib/postgresql/data

# Restart
docker compose up -d db
```

### Environment Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `POSTGRES_USER` | No | `neet` | Database user |
| `POSTGRES_PASSWORD` | No | `neet_dev_password` | Database password |
| `POSTGRES_DB` | No | `neet_compass` | Database name |
| `DATABASE_URL` | No | `postgresql+psycopg://...` | Database connection URL |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection |
| `SECRET_KEY` | No | `dev-only-secret` | JWT signing key |
| `APP_ENV` | No | `development` | Environment (dev/test/prod) |
| `APP_DEBUG` | No | `False` | Debug mode |
| `CORS_ORIGINS` | No | `[]` | Allowed CORS origins |
| `ML_RECOMMENDATION_ENGINE` | No | `unavailable` | ML engine to use |

### Updating the Deployment

```bash
# 1. Pull latest changes
git pull origin main

# 2. Rebuild containers
docker compose pull
docker compose build

# 3. Run migrations (if any)
docker compose run --rm backend alembic upgrade head

# 4. Restart services
docker compose up -d
```

### Rollback

```bash
# 1. Stop services
docker compose down

# 2. Restore database from backup
gunzip -c /data/backup/backup_20260810.sql.gz | \
  docker exec -i $(docker ps -q -f name=neet-db) \
  psql -U neet neet_compass

# 3. Redeploy previous version
git checkout v0.1.2
docker compose up -d --build
```

## Troubleshooting

### Database Connection Errors

```bash
# Check if database is running
docker compose ps

# Check database logs
docker compose logs db

# Test connection
docker compose run --rm backend python -c "
from app.core.database import engine
print(engine.connect())
"
```

### Migration Errors

```bash
# Check current revision
docker compose run --rm backend alembic current

# Check revision history
docker compose run --rm backend alembic history

# Roll back one migration
docker compose run --rm backend alembic downgrade -1

# Re-apply
docker compose run --rm backend alembic upgrade head
```

### Permission Errors

```bash
# Check file permissions
ls -la data/

# Fix permissions
chmod 755 data/
chown -R $(id -u):$(id -g) data/
```

## Verification

After installation, verify the setup:

1. **API Health**: `curl http://localhost:8000/health` should return `{"status": "healthy"}`
2. **API Docs**: `http://localhost:8000/docs` should show the OpenAPI UI
3. **Database**: `docker compose run --rm backend alembic current` should show `0001`
4. **Tests**: `make test` should pass all tests

## Next Steps

After installation, see [docs/ETL_SPEC.md](ETL_SPEC.md) for data ingestion
and [docs/PREDICTION_SPEC.md](PREDICTION_SPEC.md) for running predictions.
