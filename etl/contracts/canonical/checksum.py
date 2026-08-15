"""File identity using SHA-256 checksums."""

from __future__ import annotations

import hashlib
from pathlib import Path


def compute_checksum(data: bytes) -> str:
    """Compute SHA-256 checksum for given bytes.

    Same file → same checksum
    Different file contents → different checksum
    """
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()


def compute_file_checksum(file_path: str) -> str:
    """Compute SHA-256 checksum for a file.

    Args:
        file_path: Path to the file.

    Returns:
        Hex digest of SHA-256 hash.

    """
    hasher = hashlib.sha256()
    with Path(file_path).open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_string_checksum(text: str) -> str:
    """Compute SHA-256 checksum for a string."""
    return compute_checksum(text.encode("utf-8"))
