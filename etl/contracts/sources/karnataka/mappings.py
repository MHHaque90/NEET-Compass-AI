"""Karnataka KEA abbreviation vocabulary and normalisation helpers.

Karnataka CET Authority (KEA) uses category tokens and quota names that
map onto the canonical ``category_id`` / ``quota_id`` strings declared by
the canonical ``SeatMatrix`` / ``Allotment`` dataclasses.

Category tokens seen in Karnataka KEA sources:
  - ``GM``    -> ``gn``  (General Merit / General)
  - ``SC``    -> ``sc``  (Scheduled Caste)
  - ``ST``    -> ``st``  (Scheduled Tribe)
  - ``CAT-1`` -> ``bc``  (Category 1 - Backward Class)
  - ``2A``    -> ``bc``  (Backward Class category 2)
  - ``3B``    -> ``bc``  (Backward Class category 3)
  - ``GM PwD``-> ``gn_pwd`` (General Merit with PwD)

Quota tokens seen in Karnataka KEA sources:
  - ``AI``    -> ``ai``  (All India)
  - ``COMEDK``-> ``so``  (Management/Institute quota, mapped to state open)
  - ``SO``    -> ``so``  (State Open)
"""
from __future__ import annotations

import re
from typing import Final

# --- Category token map ----------------------------------------------------
KARNATAKA_CATEGORY_BASE: Final[dict[str, str]] = {
    "GM": "gn",
    "SC": "sc",
    "ST": "st",
    "CAT-1": "bc",
    "2A": "bc",
    "3B": "bc",
}


def _slug_token(token: str) -> str:
    """Lower-case, underscore-joined slug of a free-text token."""
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", token.strip()).strip("_").lower()
    return cleaned if cleaned else "unknown"


def normalize_karnataka_category(raw: str) -> tuple[str, bool]:
    """Normalise a Karnataka ``Category`` value.

    Returns ``(category_id, pwd)``. ``PH`` / ``PwD`` / ``NO`` suffix sets
    ``pwd`` and is stripped before the base token lookup, keeping the composite
    unique key faithful to the source row granularity.
    """
    token = raw.strip()
    pwd = token.endswith(" PwD") or token.endswith(" PH") or token.endswith(" NO")
    if pwd:
        token = token.removesuffix(" PwD").removesuffix(" PH").removesuffix(" NO").strip()
    base = KARNATAKA_CATEGORY_BASE.get(token, _slug_token(token))
    category_id = f"{base}_pwd" if pwd else base
    return category_id, pwd


def normalize_karnataka_quota(raw: str) -> str:
    """Normalise a Karnataka ``Quota`` value.

    Mappings:
      - ``AI``     -> ``ai``  (All India)
      - ``COMEDK``-> ``so``  (Management quota, mapped to state open)
      - ``SO``    -> ``so``  (State Open)
      - others    -> slugged
    """
    token = raw.strip().upper()
    mapped = {
        "AI": "ai",
        "COMEDK": "so",
        "SO": "so",
    }.get(token)
    if mapped is not None:
        return mapped
    return _slug_token(token)
