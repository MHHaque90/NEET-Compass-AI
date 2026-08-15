"""ETL CLI entry point.

Runs a named pipeline defined in ``etl/config/pipelines.yaml``. The heavy
lifting lives in the backend package (``app.infrastructure.etl``) so pipelines
share the ORM models, session factory and validators with the rest of the
platform.

Usage:
    PYTHONPATH=backend python etl/run.py --pipeline allotments --year 2025
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.core.database import SessionLocal
from app.infrastructure.etl.pipelines import build_allotment_pipeline

logger = logging.getLogger("etl.run")


def load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="neet-etl", description="NEET Compass ETL runner")
    parser.add_argument("--pipeline", required=True, help="Pipeline name from pipelines.yaml")
    parser.add_argument("--year", type=int, required=True, help="Counselling year to ingest")
    parser.add_argument(
        "--config", default="etl/config/pipelines.yaml", help="Pipeline config file"
    )
    args = parser.parse_args(argv)

    config = load_config(Path(args.config))
    spec = config.get("pipelines", {}).get(args.pipeline)
    if spec is None:
        logger.error(
            "Unknown pipeline %r. Available: %s", args.pipeline, list(config.get("pipelines", {}))
        )
        return 2

    pipeline = build_allotment_pipeline(
        source_type=spec["source"]["type"],
        path=spec["source"]["path"].format(year=args.year),
        year=args.year,
        column_map=spec["column_map"],
        session_factory=SessionLocal,
        batch_size=spec.get("batch_size", 1000),
    )
    result = pipeline.run()
    logger.info("Pipeline result: %s", result)
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    raise SystemExit(main())
