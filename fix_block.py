with open('E:\\NEET Compass AI\\backend\\alembic\\versions\\0001_initial_schema.py', 'r') as f:
    content = f.read()

old_block = """    )
    op.create_index(
        "ix_data_sources_type_status", "data_sources", ["source_type", "status"]
    )

    op.create_table(
        "source_files",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column(
            "data_source_id",
            sa.Uuid(),
            sa.ForeignKey("data_sources.id", ondelete="CASCADE"),
            nullable=False,
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
            "status",
            sa.String(length=20),
            default="DISCOVERED",
            nullable=False,
        ),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("validation_result", sa.JSON(), nullable=True),
        sa.Column(
            "discovered_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("downloaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("loaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_version", sa.String(length=50), nullable=True),
        sa.Column("etl_version", sa.String(length=50), nullable=True),
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
        sa.UniqueConstraint(
            "data_source_id",
            "academic_year",
            "file_name",
            "file_version",
            name="uq_source_files_source_year_name_version",
        ),
    )
    op.create_index(
        "ix_source_files_source_status", "source_files", ["data_source_id", "status"]
    )
    op.create_index("ix_source_files_academic_year", "source_files", ["academic_year"])
    op.create_index("ix_source_files_checksum", "source_files", ["checksum_sha256"])

    op.create_table(
"""

new_block = """    )
    op.create_index(
        "ix_data_sources_type_status", "data_sources", ["source_type", "status"]
    )

    op.create_table(
"""

if old_block in content:
    new_content = content.replace(old_block, new_block)
    with open('E:\\NEET Compass AI\\backend\\alembic\\versions\\0001_initial_schema.py', 'w') as f:
        f.write(new_content)
    print('Removed old source_files block')
else:
    print('old_block not found')