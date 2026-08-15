"""Versioned API router.

Phase 1 ships the router skeleton and the health probe only. Domain
endpoints (recommendations, colleges, pipelines) are intentionally deferred
to Phase 2; the router is the single place they will be mounted.
"""

from fastapi import APIRouter

from app.api.v1.routes import health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
