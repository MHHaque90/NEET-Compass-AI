"""Loaders: persist validated rows into PostgreSQL."""

from app.infrastructure.etl.loaders.allotment_loader import AllotmentLoader

__all__ = ["AllotmentLoader"]
