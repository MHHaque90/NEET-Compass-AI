"""Tests for the machine-readable source registry (config/data_sources.yaml).

The registry is a research inventory only. These tests validate its structure;
they never touch the network and never depend on any external site being
online.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "config" / "data_sources.yaml"

REQUIRED_FIELDS = (
    "source_id",
    "source_name",
    "authority",
    "official_url",
    "dataset",
    "scope",
    "course",
    "state",
    "year_support",
    "format",
    "authority_level",
    "priority",
    "verification_status",
    "publication_status",
    "notes",
)

SOURCE_ID_RE = re.compile(r"^[a-z0-9_]+$")

VERIFIED_STATUSES = ("VERIFIED", "VERIFIED_URL_PURPOSE_NOT_FULLY_VERIFIED")


def _load_registry() -> dict[str, Any]:
    with REGISTRY_PATH.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise AssertionError("registry must load to a mapping")
    return data


def _enum_values(registry: dict[str, Any], name: str) -> list[str]:
    return list(registry["enums"][name])


@pytest.fixture()
def registry() -> dict[str, Any]:
    return _load_registry()


@pytest.fixture()
def sources(registry: dict[str, Any]) -> list[dict[str, Any]]:
    return list(registry["sources"])


def test_registry_yaml_loads(registry: dict[str, Any]) -> None:
    assert registry["version"] == 1
    assert "enums" in registry
    assert "sources" in registry


def test_sources_is_nonempty_list(sources: list[dict[str, Any]]) -> None:
    assert len(sources) > 0


def test_required_fields_present(sources: list[dict[str, Any]]) -> None:
    for source in sources:
        missing = [field for field in REQUIRED_FIELDS if field not in source]
        assert not missing, f"source {source.get('source_id')!r} missing: {missing}"


def test_source_ids_unique_and_valid(sources: list[dict[str, Any]]) -> None:
    ids = [source["source_id"] for source in sources]
    assert len(ids) == len(set(ids)), "duplicate source_id values"
    for source_id in ids:
        assert SOURCE_ID_RE.match(source_id), f"invalid source_id: {source_id!r}"


def test_priorities_valid(registry: dict[str, Any], sources: list[dict[str, Any]]) -> None:
    allowed = set(_enum_values(registry, "priorities"))
    for source in sources:
        assert source["priority"] in allowed, (
            f"{source['source_id']}: invalid priority {source['priority']!r}"
        )


def test_verification_statuses_valid(
    registry: dict[str, Any], sources: list[dict[str, Any]]
) -> None:
    allowed = set(_enum_values(registry, "verification_statuses"))
    for source in sources:
        assert source["verification_status"] in allowed, (
            f"{source['source_id']}: invalid verification_status {source['verification_status']!r}"
        )


def test_scope_valid(registry: dict[str, Any], sources: list[dict[str, Any]]) -> None:
    allowed = set(_enum_values(registry, "scopes"))
    for source in sources:
        assert source["scope"] in allowed, (
            f"{source['source_id']}: invalid scope {source['scope']!r}"
        )


def test_course_valid(registry: dict[str, Any], sources: list[dict[str, Any]]) -> None:
    allowed = set(_enum_values(registry, "courses"))
    for source in sources:
        assert source["course"] in allowed, (
            f"{source['source_id']}: invalid course {source['course']!r}"
        )


def test_authority_level_valid(registry: dict[str, Any], sources: list[dict[str, Any]]) -> None:
    allowed = set(_enum_values(registry, "authority_levels"))
    for source in sources:
        assert source["authority_level"] in allowed, (
            f"{source['source_id']}: invalid authority_level {source['authority_level']!r}"
        )


def test_publication_status_valid(registry: dict[str, Any], sources: list[dict[str, Any]]) -> None:
    allowed = set(_enum_values(registry, "publication_statuses"))
    for source in sources:
        assert source["publication_status"] in allowed, (
            f"{source['source_id']}: invalid publication_status {source['publication_status']!r}"
        )


def test_format_valid(registry: dict[str, Any], sources: list[dict[str, Any]]) -> None:
    allowed = set(_enum_values(registry, "formats"))
    for source in sources:
        assert source["format"] in allowed, (
            f"{source['source_id']}: invalid format {source['format']!r}"
        )


def test_urls_valid_when_required(sources: list[dict[str, Any]]) -> None:
    for source in sources:
        status = source["verification_status"]
        url = source["official_url"]
        if status in VERIFIED_STATUSES:
            assert url and url.startswith(("http://", "https://")), (
                f"{source['source_id']}: verified source must carry an http(s) URL"
            )
        else:
            assert url in (None, ""), (
                f"{source['source_id']}: not-verified source must not carry a URL"
            )


def test_documented_counts_match_registry(sources: list[dict[str, Any]]) -> None:
    total = len(sources)
    verified = sum(1 for source in sources if source["verification_status"] in VERIFIED_STATUSES)
    p0 = sum(1 for source in sources if source["priority"] == "P0")
    p1 = sum(1 for source in sources if source["priority"] == "P1")

    assert total == 28
    assert verified == 25
    assert total - verified == 3
    assert p0 == 15
    assert p1 == 13
