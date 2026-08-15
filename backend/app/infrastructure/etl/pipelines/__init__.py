"""Concrete ETL pipeline factories."""

from app.infrastructure.etl.pipelines.allotment_pipeline import build_allotment_pipeline

__all__ = ["build_allotment_pipeline"]
