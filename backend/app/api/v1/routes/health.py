"""Health/liveness probe — required by orchestrators, not a product endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db

router = APIRouter()


@router.get("/health")
def health(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    """Return service + database liveness status."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "service": "ok",
        "database": db_status,
        "environment": settings.app_env.value,
        "version": settings.app_version,
    }
