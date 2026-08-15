-- Feature flag table schema (PostgreSQL).
--
-- Managed/production databases: apply this through the platform's migration
-- tooling. Local development and tests may instead call
-- DatabaseFlagProvider.ensure_schema() (idempotent CREATE TABLE).

CREATE TABLE IF NOT EXISTS feature_flags (
    name       VARCHAR(100) PRIMARY KEY,
    enabled    BOOLEAN NOT NULL,
    comment    VARCHAR(500),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
