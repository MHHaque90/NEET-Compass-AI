"""
Modelling Readiness Configuration
Reads from config/modelling_readiness.yaml
"""

from pathlib import Path

import yaml
from modelling.contracts.dataset import AuthorityType


def get_modelling_ready_years() -> dict[AuthorityType, list[int]]:
    """Get verified modelling-ready years from config."""
    config_path = Path(__file__).parent.parent.parent / "config" / "modelling_readiness.yaml"
    if not config_path.exists():
        return {
            AuthorityType.MCC: [2025],
            AuthorityType.MAHARASHTRA: [],
            AuthorityType.KARNATAKA: [],
            AuthorityType.UTTAR_PRADESH: [],
        }

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Map authority strings from config to AuthorityType enum
    authority_map = {
        "MEDICAL COUNSELLING COMMITTEE": AuthorityType.MCC,
        "STATE COMMON ENTRANCE TEST CELL, MAHARASHTRA": AuthorityType.MAHARASHTRA,
        "KARNATAKA EXAMINATIONS AUTHORITY": AuthorityType.KARNATAKA,
        "DIRECTORATE OF MEDICAL EDUCATION, UTTAR PRADESH": AuthorityType.UTTAR_PRADESH,
    }

    ready_years = {}
    for auth in AuthorityType:
        ready_years[auth] = []

    for dataset in config.get("datasets", []):
        if (
            dataset.get("readiness") == "READY"
            and dataset.get("lifecycle_stage") == "MODELLING_READY"
        ):
            auth_str = dataset.get("authority", "").upper()
            year = dataset.get("year")
            if auth_str in authority_map and year:
                auth = authority_map[auth_str]
                ready_years[auth].append(year)

    # Deduplicate and sort
    for auth in ready_years:
        ready_years[auth] = sorted(set(ready_years[auth]))

    return ready_years


def get_target_readiness() -> str:
    """Get current target readiness from config."""
    config_path = Path(__file__).parent.parent.parent / "config" / "modelling_readiness.yaml"
    if not config_path.exists():
        return "NO_TARGET_READY"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    return config.get("summary", {}).get("first_modelling_target", "NO_TARGET_READY")


def get_temporal_validation_status() -> str:
    """Get temporal validation status from config."""
    config_path = Path(__file__).parent.parent.parent / "config" / "modelling_readiness.yaml"
    if not config_path.exists():
        return "BLOCKED"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    min_years = config.get("summary", {}).get("minimum_years_for_temporal_validation", 3)
    current_max = config.get("summary", {}).get("current_max_consecutive_years", 1)

    if current_max < min_years:
        return "BLOCKED"
    return "READY"
