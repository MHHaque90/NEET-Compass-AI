"""PII Gate — Sprint 3.9.

Strengthens the existing PII boundary with deterministic detection
of candidate-specific identifiers. The system fails closed where a
clearly candidate-specific identifier is detected.

Does NOT destroy source evidence — PII gate applies to what enters
the canonical modelling boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Comprehensive PII blocklist for NEET counselling data
# Covers all known candidate-specific identifier patterns
PII_BLOCKLIST: frozenset[str] = frozenset({
    # Direct identifiers
    "candidate_name",
    "candidate name",
    "father_name",
    "father name",
    "mother_name",
    "mother name",
    "guardian_name",
    "guardian name",
    "roll_number",
    "roll number",
    "application_number",
    "application number",
    "registration_number",
    "registration number",
    "neet_roll_number",
    "neet_application_number",
    "neet_registration_number",
    # Contact
    "phone",
    "mobile",
    "contact_no",
    "contact number",
    "email",
    "email_id",
    "address",
    "permanent_address",
    "correspondence_address",
    # Identity documents
    "aadhaar",
    "aadhar",
    "aadhaar_number",
    "pan",
    "pan_number",
    "passport_number",
    "voter_id",
    "caste_certificate_number",
    "disability_certificate_number",
    # Scores/percentiles linked to candidate
    "percentile",
    "neet_percentile",
    "neet_score",
    "all_india_rank",
    "air",
    "state_rank",
    "category_rank",
    # Photos/signatures
    "photograph",
    "signature",
    "thumb_impression",
    # Application specific
    "application_id",
    "app_id",
    "form_number",
    "form_no",
    "user_id",
    "login_id",
    # Other candidate-specific
    "date_of_birth",
    "dob",
    "gender",
    "category",
    "sub_category",
    "pwd_status",
    "ews_status",
    "minority_status",
    "domicile_state",
    "nationality",
    "religion",
    "community",
    "mother_tongue",
    "blood_group",
})


# Additional patterns for fuzzy matching
PII_PATTERNS: tuple[str, ...] = (
    "candidate",
    "applicant",
    "student",
    "roll",
    "application",
    "registration",
    "aadhaar",
    "aadhar",
    "pan_card",
    "passport",
    "voter",
    "certificate",
    "percentile",
    "score",
    "rank",
    "photograph",
    "signature",
    "thumb",
    "form",
    "login",
    "user",
    "dob",
    "date_of_birth",
    "gender",
    "pwd",
    "ews",
    "minority",
    "domicile",
    "nationality",
    "religion",
    "community",
    "mother_tongue",
    "blood_group",
)


@dataclass(frozen=True)
class PIIGateResult:
    """Result of PII gate validation."""

    passed: bool
    detected_fields: tuple[str, ...]
    scanned_fields: tuple[str, ...]
    details: dict[str, Any]

    def __bool__(self) -> bool:
        return self.passed


class PIIGate:
    """Detects candidate PII in historical artifacts.

    Fails closed: if any candidate-specific identifier is detected,
    the artifact cannot enter the canonical modelling boundary.
    """

    def __init__(
        self,
        blocklist: frozenset[str] = PII_BLOCKLIST,
        patterns: tuple[str, ...] = PII_PATTERNS,
        case_sensitive: bool = False,
    ):
        self.blocklist = blocklist
        self.patterns = patterns
        self.case_sensitive = case_sensitive
        self._normalized_blocklist = self._normalize(blocklist)
        self._normalized_patterns = self._normalize(patterns)

    def _normalize(self, items: frozenset[str] | tuple[str, ...]) -> frozenset[str]:
        if self.case_sensitive:
            return frozenset(items)
        return frozenset(item.lower().replace(" ", "_").replace("-", "_") for item in items)

    def _normalize_field(self, field: str) -> str:
        if self.case_sensitive:
            return field
        return field.lower().replace(" ", "_").replace("-", "_")

    def detect_pii(self, fields: list[str] | dict[str, Any]) -> tuple[str, ...]:
        """Detect PII fields in a list of column names or record keys.

        Args:
            fields: List of field names or dict keys.

        Returns:
            Tuple of detected PII field names (original case).

        """
        if isinstance(fields, dict):
            field_names = list(fields.keys())
        else:
            field_names = list(fields)

        detected = []
        for field in field_names:
            normalized = self._normalize_field(field)
            if normalized in self._normalized_blocklist:
                detected.append(field)
                continue
            # Check patterns
            for pattern in self._normalized_patterns:
                if pattern in normalized:
                    detected.append(field)
                    break

        return tuple(detected)

    def validate(self, fields: list[str] | dict[str, Any]) -> PIIGateResult:
        """Validate that no PII fields are present.

        Args:
            fields: List of field names or record dict.

        Returns:
            PIIGateResult with pass/fail and detected fields.

        """
        detected = self.detect_pii(fields)
        field_list = list(fields.keys()) if isinstance(fields, dict) else list(fields)

        return PIIGateResult(
            passed=len(detected) == 0,
            detected_fields=detected,
            scanned_fields=tuple(field_list),
            details={
                "total_scanned": len(field_list),
                "detected_count": len(detected),
                "blocklist_size": len(self.blocklist),
            },
        )


def detect_pii(fields: list[str] | dict[str, Any], blocklist: frozenset[str] = PII_BLOCKLIST) -> tuple[str, ...]:
    """Convenience function to detect PII fields."""
    gate = PIIGate(blocklist=blocklist)
    return gate.detect_pii(fields)


def validate_no_pii(fields: list[str] | dict[str, Any], blocklist: frozenset[str] = PII_BLOCKLIST) -> PIIGateResult:
    """Convenience function to validate no PII."""
    gate = PIIGate(blocklist=blocklist)
    return gate.validate(fields)
