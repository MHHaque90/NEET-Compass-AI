#!/usr/bin/env python
import os
os.chdir('E:\\NEET Compass AI\\backend')

with open('alembic/versions/0001_initial_schema.py', 'r') as f:
    lines = f.readlines()

# The current state has a stray ')' at line 701 (0-indexed: 700)
# I need to insert the missing index and source_files table before etl_runs

# Find the index of 'op.create_table("etl_runs"' 
etl_runs_idx = None
for i, line in enumerate(lines):
    if 'op.create_table("etl_runs"' in line:
        etl_runs_idx = i
        break

if etl_runs_idx:
    # Insert before etl_runs: the data_sources closing, index, and source_files table
    # Insert these lines at position etl_runs_idx
    insert_lines = [
        '    )\n',
        '    op.create_index(\n',
        '        "ix_data_sources_type_status", "data_sources", ["source_type", "status"]\n',
        '    )\n',
        '    op.create_table(\n',
        '        "source_files",\n',
        '        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),\n',
        '        sa.Column(\n',
        '            "data_source_id",\n',
        '            sa.Uuid(),\n',
        '            sa.ForeignKey("data_sources.id", ondelete="CASCADE"),\n',
        '            nullable=False,\n',
        '        ),\n',
        '        sa.Column("file_name", sa.String(length=255), nullable=False),\n',
        '        sa.Column("file_version", sa.String(length=50), default="1", nullable=False),\n',
        '        sa.Column("academic_year", sa.SmallInteger(), nullable=False, index=True),\n',
        '        sa.Column("counselling_round", sa.String(length=50), nullable=True),\n',
        '        sa.Column("remote_url", sa.String(length=500), nullable=True),\n',
        '        sa.Column("local_path", sa.String(length=500), nullable=True),\n',
        '        sa.Column("file_size_bytes", sa.Integer(), nullable=True),\n',
        '        sa.Column("mime_type", sa.String(length=100), nullable=True),\n',
        '        sa.Column("checksum_sha256", sa.String(length=64), nullable=True, index=True),\n',
        '        sa.Column("row_count", sa.Integer(), nullable=True),\n',
        '        sa.Column("column_names", sa.JSON(), nullable=True),\n',
        '        sa.Column(\n',
        '            "status",\n',
        '            sa.String(length=20),\n',
        '            default="DISCOVERED",\n',
        '            nullable=False,\n',
        '        ),\n',
        '        sa.Column("error_message", sa.String(length=1000), nullable=True),\n',
        '        sa.Column("validation_result", sa.JSON(), nullable=True),\n',
        '        sa.Column(\n',
        '            "discovered_at",\n',
        '            sa.DateTime(timezone=True),\n',
        '            server_default=sa.func.now(),\n',
        '            nullable=False,\n',
        '        ),\n',
        '        sa.Column("downloaded_at", sa.DateTime(timezone=True), nullable=True),\n',
        '        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),\n',
        '        sa.Column("loaded_at", sa.DateTime(timezone=True), nullable=True),\n',
        '        sa.Column("source_version", sa.String(length=50), nullable=True),\n',
        '        sa.Column("etl_version", sa.String(length=50), nullable=True),\n',
        '        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),\n',
        '        sa.Column(\n',
        '            "created_at",\n',
        '            sa.DateTime(timezone=True),\n',
        '            server_default=sa.func.now(),\n',
        '            nullable=False,\n',
        '        ),\n',
        '        sa.Column(\n',
        '            "updated_at",\n',
        '            sa.DateTime(timezone=True),\n',
        '            server_default=sa.func.now(),\n',
        '            nullable=False,\n',
        '        ),\n',
        '        sa.PrimaryKeyConstraint("id"),\n',
        '        sa.UniqueConstraint(\n',
        '            "data_source_id",\n',
        '            "academic_year",\n',
        '            "file_name",\n',
        '            "file_version",\n',
        '            name="uq_source_files_source_year_name_version",\n',
        '        ),\n',
        '    )\n',
        '    op.create_index(\n',
        '        "ix_source_files_source_status", "source_files", ["data_source_id", "status"]\n',
        '    )\n',
        '    op.create_index("ix_source_files_academic_year", "source_files", ["academic_year"]),\n',
        '    op.create_index("ix_source_files_checksum", "source_files", ["checksum_sha256"]),\n',
    ]
    
    # Insert the lines
    new_lines = lines[:etl_runs_idx] + insert_lines + lines[etl_runs_idx:]
    
    with open('alembic/versions/0001_initial_schema.py', 'w') as f:
        f.writelines(new_lines)
    
    print("Fixed the file structure")
else:
    print("Could not find etl_runs line")