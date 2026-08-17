"""Uttar Pradesh abbreviation vocabulary and normalisation helpers.

Karnataka CET Authority (KEA) uses category tokens and quota names that
map onto the canonical ``category_id`` / ``quota_id`` strings declared by
the canonical ``SeatMatrix`` / ``Allotment`` dataclasses.

Research actual UP terminology before relying on these mappings.

Category tokens seen in Uttar Pradesh sources (to be verified):
  - ``GM``    -> ``gn``  (General Merit / General)
  - ``SC``    -> ``sc``  (Scheduled Caste)
  - ``ST``    -> ``st``  (Scheduled Tribe)
  - ``BC``    -> ``bc``  (Backward Class)
  - ``EW``    -> ``ew``  (Ethnically weak)

Quota tokens seen in Uttar Pradesh sources (to be verified):
  - ``AI``    -> ``ai``  (All India)
  - ``SO``    -> ``so``  (State Open)

Note: These mappings are placeholder values based on common Indian state
counselling terminology. They MUST be verified against the actual UP
source data before use. Unknown tokens should be handled by the adapter
with explicit error handling, not silently mapped.
"""

from __future__ import annotations

import re
from typing import Final

# --- Category token map ----------------------------------------------------
# Placeholder map - MUST be verified against actual UP source data.
# These values are common Indian state counselling abbreviations but
# must be confirmed for Uttar Pradesh.
UP_CATEGORY_BASE: Final[dict[str, str]] = {
    "GM": "gn",
    "SC": "sc",
    "ST": "st",
    "BC": "bc",
    "EW": "ew",
}


def _slug_token(token: str) -> str:
    """Lower-case, underscore-joined slug of a free-text token."""
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", token.strip()).strip("_").lower()
    return cleaned if cleaned else "unknown"


def normalize_up_category(raw: str) -> tuple[str, bool]:
    """Normalise a Uttar Pradesh ``Category`` value.

    Returns ``(category_id, pwd)``. ``PH`` / ``PwD`` / ``NO`` suffix sets
    ``pwd`` and is stripped before the base token lookup, keeping the composite
    unique key faithful to the source row granularity.

    Note: This is a placeholder implementation. MUST be verified against
    actual UP source data. Unknown tokens fall back to slugging.
    """
    token = raw.strip()
    pwd = token.endswith(" PwD") or token.endswith(" PH") or token.endswith(" NO")
    if pwd:
        token = token.removesuffix(" PwD").removesuffix(" PH").removesuffix(" NO").strip()
    base = UP_CATEGORY_BASE.get(token, _slug_token(token))
    category_id = f"{base}_pwd" if pwd else base
    return category_id, pwd


def normalize_up_quota(raw: str) -> str:
    """Normalise a Uttar Pradesh ``Quota`` value.

    Placeholder implementation. MUST be verified against actual UP source data.

    Mappings (placeholder):
      - ``AI``     -> ``ai``  (All India)
      - ``SO``    -> ``so``  (State Open)
      - others    -> slugged
    """
    token = raw.strip().upper()
    mapped = {
        "AI": "ai",
        "SO": "so",
    }.get(token)
    if mapped is not None:
        return mapped
    return _slug_token(token)
