"""ETL infrastructure — the ingestion automation layer.

Pipeline stages are small, single-responsibility classes:

    Source      -> emits raw rows (Excel/CSV/API/scraper)
    Transformer -> normalizes raw rows into validated domain records
    Loader      -> persists records (upsert) into PostgreSQL

The composition is done by concrete pipeline modules (see ``pipelines``).
Nothing here knows about HTTP or the frontend.
"""
