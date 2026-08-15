"""Sprint 2 - Production database architecture

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-08-08
Sprint: Sprint 2 - Production Database Architecture

This migration establishes the complete production database schema for
NEET Compass AI. It includes all 24 tables required for a fully
normalised, versioned, and auditable database.

Tables created (in dependency order):
    1.  states             - Indian states and union territories
    2.  districts          - Districts within states
    3.  categories         - Reservation categories
    4.  quotas             - Quota types (AIQ, State, Deemed, etc.)
    5.  rounds             - Counselling rounds
    6.  courses            - NEET courses (MBBS, BDS)
    7.  colleges           - Institution master data
    8.  data_sources       - External data sources for ETL
    9.  source_files       - Individual files from data sources
    10. fees               - Fee structures per college/course/year/category
    11. seat_matrix        - Sanctioned seat counts per college/course/quota/category
    12. users              - Platform users (candidates, admins)
    13. candidates         - Persisted candidate profiles
    14. allotments         - Historical counselling cut-off rows (analytic core)
    15. recommendations    - Legacy recommendation audit (kept for backward compat)
    16. etl_runs           - ETL pipeline execution runs
    17. etl_errors         - Granular ETL error tracking
    18. model_versions     - ML model registry
    19. feature_flags      - Feature flag definitions
    20. system_settings    - System configuration settings
    21. uploads            - File upload tracking
    22. predictions        - Prediction requests and results
    23. prediction_history - Individual college recommendations
    24. logs               - Structured application logs

Design principle: enums are stored as VARCHAR with application-level
validation, not native PostgreSQL enums, so adding new enum values is
trivial without schema migrations.

All tables include:
- UUID primary keys via gen_random_uuid() (PostgreSQL 13+ builtin)
- created_at / updated_at timestamps (where appropriate)
- deleted_at for soft deletes (where appropriate)
- Unique constraints for idempotency and data integrity
- Indexes on hot query paths
- Foreign keys with appropriate ON DELETE actions
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # gen_random_uuid() is built into PostgreSQL 13+ (our compose image is 16),
    # so no extension setup is required.

    # ── Lookup Tables ─────────────────────────────────────────────────────────

    op.create_table(
        "states",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_ut", sa.Boolean(), default=False, nullable=False),
        sa.Column(
            "neet_counselling_authority", sa.String(length=200), nullable=True
        ),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_states_code"),
        sa.UniqueConstraint("name", name="uq_states_name"),
    )
    op.create_index("ix_states_code", "states", ["code"])

    op.create_table(
        "districts",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "state_id", sa.Uuid(), sa.ForeignKey("states.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("state_id", "code", name="uq_districts_state_code"),
        sa.UniqueConstraint("state_id", "name", name="uq_districts_state_name"),
    )
    op.create_index("ix_districts_state", "districts", ["state_id"])

    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("reservation_percentage", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("is_vertical", sa.Boolean(), default=True, nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_categories_code"),
        sa.UniqueConstraint("name", name="uq_categories_name"),
    )
    op.create_index("ix_categories_code", "categories", ["code"])

    op.create_table(
        "quotas",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_all_india", sa.Boolean(), default=False, nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_quotas_code"),
        sa.UniqueConstraint("name", name="uq_quotas_name"),
    )
    op.create_index("ix_quotas_code", "quotas", ["code"])

    op.create_table(
        "rounds",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("round_number", sa.SmallInteger(), nullable=False),
        sa.Column("is_stray_round", sa.Boolean(), default=False, nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_rounds_code"),
        sa.UniqueConstraint("name", name="uq_rounds_name"),
        sa.UniqueConstraint("round_number", name="uq_rounds_number"),
    )
    op.create_index("ix_rounds_code", "rounds", ["code"])
    op.create_index("ix_rounds_number", "rounds", ["round_number"])

    op.create_table(
        "courses",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("duration_years", sa.Integer(), default=5, nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_courses_code"),
        sa.UniqueConstraint("name", name="uq_courses_name"),
    )
    op.create_index("ix_courses_code", "courses", ["code"])

    # ── Data sources must come before source_files ──────────────────────────

    op.create_table(
        "data_sources",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False, index=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column(
            "source_type", sa.String(length=30), nullable=False
        ),
        sa.Column("status", sa.String(length=20), default="ACTIVE", nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("base_url", sa.String(length=500), nullable=True),
        sa.Column("api_endpoint", sa.String(length=500), nullable=True),
        sa.Column("auth_config", sa.JSON(), default={}, nullable=True),
        sa.Column("schedule_cron", sa.String(length=100), nullable=True),
        sa.Column("timezone", sa.String(length=50), default="Asia/Kolkata", nullable=False),
        sa.Column("rate_limit_rpm", sa.Integer(), nullable=True),
        sa.Column("retry_config", sa.JSON(), default={}, nullable=True),
        sa.Column(
            "last_successful_run_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column(
            "last_failed_run_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column("consecutive_failures", sa.Integer(), default=0, nullable=False),
        sa.Column("success_rate", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("schema_version", sa.String(length=50), default="1.0", nullable=False),
        sa.Column("data_version", sa.String(length=50), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_data_sources_code"),
        sa.UniqueConstraint("name", name="uq_data_sources_name"),
    )
    op.create_index("ix_data_sources_type_status", "data_sources", ["source_type", "status"])

    op.create_table(
        "source_files",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "data_source_id", sa.Uuid(), sa.ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_version", sa.String(length=50), default="1", nullable=False),
        sa.Column("academic_year", sa.SmallInteger(), nullable=False, index=True),
        sa.Column("counselling_round", sa.String(length=50), nullable=True),
        sa.Column("remote_url", sa.String(length=500), nullable=True),
        sa.Column("local_path", sa.String(length=500), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True, index=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("column_names", sa.JSON(), nullable=True),
        sa.Column(
            "status", sa.String(length=20), default="DISCOVERED", nullable=False
        ),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("validation_result", sa.JSON(), nullable=True),
        sa.Column(
            "discovered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("downloaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("loaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_version", sa.String(length=50), nullable=True),
        sa.Column("etl_version", sa.String(length=50), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "data_source_id", "academic_year", "file_name", "file_version",
            name="uq_source_files_source_year_name_version"
        ),
    )

    # ── Colleges must come before fees and seat_matrix ────────────────────────

    op.create_table(
        "colleges",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("state", sa.String(length=40), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("course", sa.String(length=10), nullable=False),
        sa.Column("ownership", sa.String(length=32), nullable=False),
        sa.Column("annual_fee_inr", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("total_seats", sa.Integer(), nullable=False),
        sa.Column("aiq_seats", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_colleges_code"),
    )
    op.create_index("ix_colleges_state", "colleges", ["state"])
    op.create_index("ix_colleges_course", "colleges", ["course"])

    # ── Fees and seat_matrix reference colleges and source_files ──────────────

    op.create_table(
        "fees",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "college_id", sa.Uuid(), sa.ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("course", sa.String(length=10), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("ownership", sa.String(length=32), nullable=False),
        sa.Column("academic_year", sa.SmallInteger(), nullable=False, index=True),
        sa.Column("notification_date", sa.Date(), nullable=True),
        sa.Column("tuition_fee_inr", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "hostel_fee_inr", sa.Numeric(precision=12, scale=2), default=0, nullable=False
        ),
        sa.Column(
            "security_deposit_inr", sa.Numeric(precision=12, scale=2), default=0, nullable=False
        ),
        sa.Column(
            "miscellaneous_fee_inr", sa.Numeric(precision=12, scale=2), default=0, nullable=False
        ),
        sa.Column("total_annual_fee_inr", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("is_notified", sa.Boolean(), default=False, nullable=False),
        sa.Column(
            "source_file_id", sa.Uuid(), sa.ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "college_id", "course", "category", "academic_year",
            name="uq_fees_college_course_cat_year"
        ),
    )
    op.create_index("ix_fees_college_year", "fees", ["college_id", "academic_year"])
    op.create_index("ix_fees_ownership_year", "fees", ["ownership", "academic_year"])

    op.create_table(
        "seat_matrix",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "college_id", sa.Uuid(), sa.ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("course", sa.String(length=10), nullable=False),
        sa.Column("quota_type", sa.String(length=16), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("academic_year", sa.SmallInteger(), nullable=False, index=True),
        sa.Column("notification_date", sa.Date(), nullable=True),
        sa.Column("seats_sanctioned", sa.Integer(), nullable=False),
        sa.Column("seats_filled", sa.Integer(), default=0, nullable=False),
        sa.Column("is_notified", sa.Boolean(), default=False, nullable=False),
        sa.Column(
            "source_file_id", sa.Uuid(), sa.ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "college_id", "course", "quota_type", "category", "academic_year",
            name="uq_seat_matrix_college_course_quota_cat_year"
        ),
    )
    op.create_index("ix_seat_matrix_college_year", "seat_matrix", ["college_id", "academic_year"])
    op.create_index("ix_seat_matrix_cohort", "seat_matrix", ["quota_type", "category", "academic_year"])

    # ── User & Authentication ─────────────────────────────────────────────────

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("is_verified", sa.Boolean(), default=False, nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        # Candidate profile fields
        sa.Column("air", sa.Integer(), nullable=True, index=True),
        sa.Column("marks", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(length=32), nullable=True),
        sa.Column(
            "domicile_state_id", sa.Uuid(), sa.ForeignKey("states.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("gender", sa.String(length=16), nullable=True),
        sa.Column("is_pwd", sa.Boolean(), default=False, nullable=False),
        sa.Column("is_minority", sa.Boolean(), default=False, nullable=False),
        sa.Column("quota_type", sa.String(length=16), nullable=True),
        sa.Column("budget_inr", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("preferred_states", sa.JSON(), default=[], nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("phone", name="uq_users_phone"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_phone", "users", ["phone"])
    op.create_index("ix_users_air", "users", ["air"])

    # ── Domain Data ───────────────────────────────────────────────────────────

    op.create_table(
        "candidates",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("air", sa.Integer(), nullable=False, index=True),
        sa.Column("marks", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("domicile_state", sa.String(length=40), nullable=False),
        sa.Column("gender", sa.String(length=16), nullable=False),
        sa.Column("is_pwd", sa.Boolean(), nullable=False),
        sa.Column("is_minority", sa.Boolean(), nullable=False),
        sa.Column("quota_type", sa.String(length=16), nullable=False),
        sa.Column("budget_inr", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("preferred_states", sa.JSON(), default=[], nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidates_air", "candidates", ["air"])

    op.create_table(
        "allotments",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "college_id", sa.Uuid(), sa.ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("college_code", sa.String(length=20), nullable=False),
        sa.Column("course", sa.String(length=10), nullable=False),
        sa.Column("counselling_year", sa.SmallInteger(), nullable=False),
        sa.Column("counselling_date", sa.Date(), nullable=True),
        sa.Column("round_number", sa.SmallInteger(), nullable=False),
        sa.Column("is_stray_round", sa.Boolean(), nullable=False),
        sa.Column("quota_type", sa.String(length=16), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("gender", sa.String(length=16), nullable=False),
        sa.Column("is_pwd", sa.Boolean(), nullable=False),
        sa.Column("opening_rank", sa.Integer(), nullable=False),
        sa.Column("closing_rank", sa.Integer(), nullable=False),
        sa.Column("opening_marks", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("closing_marks", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("seats_offered", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "college_id", "counselling_year", "round_number", "quota_type", "category", "gender", "is_pwd",
            name="uq_allotments_college_round_cohort"
        ),
    )
    op.create_index("ix_allotments_college_year_round", "allotments", ["college_id", "counselling_year", "round_number"])
    op.create_index("ix_allotments_cohort", "allotments", ["quota_type", "category", "gender", "is_pwd", "counselling_year"])

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "candidate_id", sa.Uuid(), sa.ForeignKey("candidates.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column(
            "college_id", sa.Uuid(), sa.ForeignKey("colleges.id", ondelete="CASCADE"), nullable=True
        ),
        sa.Column("course", sa.String(length=10), nullable=False),
        sa.Column("probability", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column("expected_round", sa.SmallInteger(), nullable=True),
        sa.Column("confidence", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column("engine_name", sa.String(length=50), nullable=False),
        sa.Column("engine_version", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("reasons", sa.JSON(), default=[], nullable=False),
        sa.Column("strategy", sa.JSON(), default={}, nullable=False),
        sa.Column("choice_filling_order", sa.JSON(), default=[], nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recommendations_candidate", "recommendations", ["candidate_id", "created_at"])

    # ── ETL Infrastructure ────────────────────────────────────────────────────

    op.create_table(
        "etl_runs",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "data_source_id", sa.Uuid(), sa.ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column(
            "source_file_id", sa.Uuid(), sa.ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("pipeline_name", sa.String(length=100), nullable=False, index=True),
        sa.Column(
            "run_type", sa.String(length=20), default="INCREMENTAL", nullable=False
        ),
        sa.Column(
            "status", sa.String(length=20), default="PENDING", nullable=False
        ),
        sa.Column("config_snapshot", sa.JSON(), default={}, nullable=False),
        sa.Column("academic_year", sa.SmallInteger(), nullable=True, index=True),
        sa.Column("counselling_round", sa.String(length=50), nullable=True),
        sa.Column("total_files", sa.Integer(), default=0, nullable=False),
        sa.Column("processed_files", sa.Integer(), default=0, nullable=False),
        sa.Column("total_rows", sa.Integer(), default=0, nullable=False),
        sa.Column("loaded_rows", sa.Integer(), default=0, nullable=False),
        sa.Column("skipped_rows", sa.Integer(), default=0, nullable=False),
        sa.Column("error_rows", sa.Integer(), default=0, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("error_count", sa.Integer(), default=0, nullable=False),
        sa.Column("last_error", sa.String(length=1000), nullable=True),
        sa.Column("error_summary", sa.JSON(), nullable=True),
        sa.Column("quality_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("validation_passed", sa.Integer(), default=0, nullable=False),
        sa.Column("validation_failed", sa.Integer(), default=0, nullable=False),
        sa.Column("etl_version", sa.String(length=50), nullable=False),
        sa.Column("code_version", sa.String(length=50), nullable=True),
        sa.Column("triggered_by", sa.String(length=100), nullable=True),
        sa.Column("trigger_type", sa.String(length=50), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_etl_runs_source_status", "etl_runs", ["data_source_id", "status"])
    op.create_index("ix_etl_runs_started", "etl_runs", ["started_at"])
    op.create_index("ix_etl_runs_pipeline", "etl_runs", ["pipeline_name"])

    op.create_table(
        "etl_errors",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "etl_run_id", sa.Uuid(), sa.ForeignKey("etl_runs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "source_file_id", sa.Uuid(), sa.ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("stage", sa.String(length=20), nullable=False),
        sa.Column(
            "severity", sa.String(length=10), default="ERROR", nullable=False
        ),
        sa.Column("error_code", sa.String(length=50), nullable=False, index=True),
        sa.Column("error_message", sa.String(length=2000), nullable=False),
        sa.Column("error_details", sa.JSON(), nullable=True),
        sa.Column("row_number", sa.Integer(), nullable=True),
        sa.Column("column_name", sa.String(length=100), nullable=True),
        sa.Column("raw_value", sa.String(length=500), nullable=True),
        sa.Column("expected_value", sa.String(length=500), nullable=True),
        sa.Column("is_resolved", sa.Boolean(), default=False, nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.String(length=100), nullable=True),
        sa.Column("resolution_notes", sa.String(length=1000), nullable=True),
        sa.Column("stack_trace", sa.Text(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_etl_errors_run_severity", "etl_errors", ["etl_run_id", "severity"])
    op.create_index("ix_etl_errors_stage", "etl_errors", ["stage"])
    op.create_index("ix_etl_errors_code", "etl_errors", ["error_code"])

    # ── Model & Feature Flag Versioning ─────────────────────────────────────

    op.create_table(
        "model_versions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False, index=True),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column(
            "model_type", sa.String(length=30), nullable=False
        ),
        sa.Column(
            "status", sa.String(length=20), default="TRAINING", nullable=False
        ),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("training_data_version", sa.String(length=50), nullable=True),
        sa.Column("training_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("training_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("training_duration_seconds", sa.Integer(), nullable=True),
        sa.Column("training_config", sa.JSON(), default={}, nullable=False),
        sa.Column("training_metrics", sa.JSON(), default={}, nullable=False),
        sa.Column("validation_metrics", sa.JSON(), nullable=True),
        sa.Column("validation_data_version", sa.String(length=50), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("validated_by", sa.String(length=100), nullable=True),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deployed_by", sa.String(length=100), nullable=True),
        sa.Column("deployment_config", sa.JSON(), nullable=True),
        sa.Column("model_path", sa.String(length=500), nullable=True),
        sa.Column("artifact_path", sa.String(length=500), nullable=True),
        sa.Column("feature_names", sa.JSON(), nullable=True),
        sa.Column("target_name", sa.String(length=100), nullable=True),
        sa.Column("min_accuracy", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column("min_precision", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column("min_recall", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column("max_latency_ms", sa.Integer(), nullable=True),
        sa.Column(
            "parent_model_id", sa.Uuid(), sa.ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("experiment_id", sa.String(length=100), nullable=True),
        sa.Column("run_id", sa.String(length=100), nullable=True),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("deprecated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deprecated_by", sa.String(length=100), nullable=True),
        sa.Column("deprecation_reason", sa.String(length=500), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model_name", "version", name="uq_model_versions_name_version"),
    )
    op.create_index("ix_model_versions_name_status", "model_versions", ["model_name", "status"])
    op.create_index("ix_model_versions_production", "model_versions", ["is_production", "model_name"])

    op.create_table(
        "feature_flags",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False, index=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column(
            "flag_type", sa.String(length=10), default="BOOLEAN", nullable=False
        ),
        sa.Column("default_value", sa.String(), nullable=False),
        sa.Column("default_value_parsed", sa.JSON(), nullable=True),
        sa.Column("current_value", sa.String(), nullable=False),
        sa.Column("current_value_parsed", sa.JSON(), nullable=True),
        sa.Column(
            "current_source", sa.String(length=20), default="DEFAULT", nullable=False
        ),
        sa.Column("targeting_rules", sa.JSON(), nullable=True),
        sa.Column("rollout_percentage", sa.Integer(), default=100, nullable=False),
        sa.Column("is_enabled", sa.Boolean(), default=True, nullable=False, index=True),
        sa.Column("is_system", sa.Boolean(), default=False, nullable=False),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("owner", sa.String(length=100), nullable=True),
        sa.Column("team", sa.String(length=100), nullable=True),
        sa.Column("version", sa.Integer(), default=1, nullable=False),
        sa.Column("last_modified_by", sa.String(length=100), nullable=True),
        sa.Column("last_modified_source", sa.String(length=20), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", name="uq_feature_flags_key"),
    )
    op.create_index("ix_feature_flags_enabled", "feature_flags", ["is_enabled"])
    op.create_index("ix_feature_flags_type", "feature_flags", ["flag_type"])

    # ── System & Infrastructure ─────────────────────────────────────────────

    op.create_table(
        "system_settings",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "scope", sa.String(length=20), nullable=False, index=True
        ),
        sa.Column("key", sa.String(length=100), nullable=False, index=True),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column(
            "value_type", sa.String(length=10), nullable=False
        ),
        sa.Column("version", sa.Integer(), default=1, nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_sensitive", sa.Boolean(), default=False, nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("feature_flag_id", sa.Uuid(), sa.ForeignKey("feature_flags.id", ondelete="SET NULL"), nullable=True),
        sa.Column("validation_rules", sa.JSON(), nullable=True),
        sa.Column("allowed_values", sa.JSON(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope", "key", "version", name="uq_system_settings_scope_key_version"),
    )
    op.create_index("ix_system_settings_scope_key", "system_settings", ["scope", "key"])
    op.create_index("ix_system_settings_feature", "system_settings", ["feature_flag_id"])

    op.create_table(
        "uploads",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column(
            "source_file_id", sa.Uuid(), sa.ForeignKey("source_files.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column(
            "upload_type", sa.String(length=20), nullable=False
        ),
        sa.Column(
            "status", sa.String(length=16), default="PENDING", nullable=False
        ),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("error_count", sa.Integer(), default=0, nullable=False),
        sa.Column("error_details", sa.JSON(), default={}, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_uploads_user", "uploads", ["user_id"])
    op.create_index("ix_uploads_source_file", "uploads", ["source_file_id"])
    op.create_index("ix_uploads_status_type", "uploads", ["status", "upload_type"])

    # ── Predictions ───────────────────────────────────────────────────────────

    op.create_table(
        "predictions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("session_id", sa.String(length=100), nullable=False, index=True),
        sa.Column("air", sa.Integer(), nullable=False),
        sa.Column("marks", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column(
            "domicile_state_id", sa.Uuid(), sa.ForeignKey("states.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("gender", sa.String(length=16), nullable=False),
        sa.Column("is_pwd", sa.Boolean(), default=False, nullable=False),
        sa.Column("is_minority", sa.Boolean(), default=False, nullable=False),
        sa.Column("quota_type", sa.String(length=16), nullable=False),
        sa.Column("budget_inr", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("preferred_states", sa.JSON(), default=[], nullable=False),
        sa.Column("counselling_year", sa.SmallInteger(), nullable=False, index=True),
        sa.Column("target_round", sa.SmallInteger(), nullable=True),
        sa.Column("engine_name", sa.String(length=50), nullable=False),
        sa.Column("engine_version", sa.String(length=50), nullable=True),
        sa.Column(
            "model_version_id", sa.Uuid(), sa.ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("total_colleges_evaluated", sa.Integer(), default=0, nullable=False),
        sa.Column("total_recommendations", sa.Integer(), default=0, nullable=False),
        sa.Column("top_probability", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column(
            "prediction_status", sa.String(length=16), default="PENDING", nullable=False
        ),
        sa.Column("request_metadata", sa.JSON(), default={}, nullable=False),
        sa.Column("response_metadata", sa.JSON(), default={}, nullable=False),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "session_id", "counselling_year", "engine_name", "engine_version",
            name="uq_predictions_user_session_year_engine"
        ),
    )
    op.create_index("ix_predictions_user_created", "predictions", ["user_id", "created_at"])
    op.create_index("ix_predictions_session", "predictions", ["session_id"])
    op.create_index("ix_predictions_engine_version", "predictions", ["engine_name", "engine_version"])

    op.create_table(
        "prediction_history",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "prediction_id", sa.Uuid(), sa.ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "college_id", sa.Uuid(), sa.ForeignKey("colleges.id", ondelete="CASCADE"), nullable=True
        ),
        sa.Column("course", sa.String(length=10), nullable=False),
        sa.Column("probability", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column("expected_round", sa.SmallInteger(), nullable=True),
        sa.Column("confidence", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column("status", sa.String(length=16), default="PENDING", nullable=False),
        sa.Column("reasons", sa.JSON(), default=[], nullable=False),
        sa.Column("strategy", sa.JSON(), default={}, nullable=False),
        sa.Column("choice_filling_order", sa.Integer(), nullable=True),
        sa.Column("quota_type", sa.String(length=16), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("gender", sa.String(length=16), nullable=False),
        sa.Column("is_pwd", sa.Boolean(), default=False, nullable=False),
        sa.Column("historical_closing_rank", sa.Integer(), nullable=True),
        sa.Column("historical_closing_marks", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("seats_available", sa.Integer(), nullable=True),
        sa.Column("feature_contributions", sa.JSON(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_predictions_history_prediction", "prediction_history", ["prediction_id"])

    # ── Logs ──────────────────────────────────────────────────────────────────

    op.create_table(
        "logs",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("message", sa.String(length=1000), nullable=False),
        sa.Column("module", sa.String(length=100), nullable=True),
        sa.Column("line_number", sa.Integer(), nullable=True),
        sa.Column("details", sa.JSON(), default={}, nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_logs_created", "logs", ["created_at"])