"""Create historical_cutoffs table

Revision ID: 0002
Revises: 0001_initial_schema
Create Date: 2026-08-12
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0002"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "historical_cutoffs",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "college_id",
            sa.Uuid(),
            sa.ForeignKey("colleges.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "course_id",
            sa.Uuid(),
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column(
            "round_id",
            sa.Uuid(),
            sa.ForeignKey("rounds.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "quota_id",
            sa.Uuid(),
            sa.ForeignKey("quotas.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "category_id",
            sa.Uuid(),
            sa.ForeignKey("categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("opening_rank", sa.Integer(), nullable=False),
        sa.Column("closing_rank", sa.Integer(), nullable=False),
        sa.Column(
            "opening_marks",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
        ),
        sa.Column(
            "closing_marks",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
        ),
        sa.Column(
            "source_file_id",
            sa.Uuid(),
            sa.ForeignKey("source_files.id", ondelete="SET NULL"),
            nullable=True,
        ),
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
    )
    op.create_index(
        "ix_historical_cutoffs_college_year",
        "historical_cutoffs",
        ["college_id", "year"],
    )
    op.create_index(
        "ix_historical_cutoffs_course_round",
        "historical_cutoffs",
        ["course_id", "round_id"],
    )
    op.create_index(
        "ix_historical_cutoffs_quota_category",
        "historical_cutoffs",
        ["quota_id", "category_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_historical_cutoffs_quota_category",
        table_name="historical_cutoffs",
    )
    op.drop_index(
        "ix_historical_cutoffs_course_round",
        table_name="historical_cutoffs",
    )
    op.drop_index(
        "ix_historical_cutoffs_college_year",
        table_name="historical_cutoffs",
    )
    op.drop_table("historical_cutoffs")