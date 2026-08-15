"""Semantic contract versioning."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ContractVersion:
    """Semantic version for data contracts.

    Format: MAJOR.MINOR.PATCH

    MAJOR = breaking contract change
    MINOR = backward-compatible extension
    PATCH = non-breaking correction
    """

    major: int
    minor: int
    patch: int

    VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

    @classmethod
    def parse(cls, version_str: str) -> ContractVersion:
        """Parse a version string like '1.2.3'."""
        match = cls.VERSION_PATTERN.match(version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str!r}")
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
        )

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def is_compatible_with(self, required: ContractVersion) -> bool:
        """Check if this version satisfies the required version.

        Rules:
        - Same MAJOR required
        - MINOR must be >= required
        - PATCH is ignored for compatibility
        """
        if self.major != required.major:
            return False
        return not self.minor < required.minor

    def is_breaking_change_from(self, other: ContractVersion) -> bool:
        """Check if this version is a breaking change from another."""
        return self.major != other.major

    def next_major(self) -> ContractVersion:
        """Return next major version."""
        return ContractVersion(self.major + 1, 0, 0)

    def next_minor(self) -> ContractVersion:
        """Return next minor version."""
        return ContractVersion(self.major, self.minor + 1, 0)

    def next_patch(self) -> ContractVersion:
        """Return next patch version."""
        return ContractVersion(self.major, self.minor, self.patch + 1)
