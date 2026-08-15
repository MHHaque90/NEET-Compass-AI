"""Resilient HTTP / local file downloader for MCC source files.

Uses only the standard library so the ETL has no hard third-party dependency.
Retries on transient ``URLError`` / ``OSError`` / 5xx failures, fails fast on
permanent HTTP errors (4xx) and on Content-Type mismatches, and is tolerant of
both ``https://`` and ``file://`` URLs, the latter being what the test-suite
uses to stay network-free.

Hardening objectives (Sprint 3.1A):

* ``expected_content_types`` --- validate the server's ``Content-Type`` before
  the bytes are trusted as a source file (rejects a surrogate PDF served where
  a CSV was expected).
* HTTP status semantics --- 4xx is permanent and raised immediately; 5xx is
  transient and retried with backoff alongside network errors.
* ``probe()`` --- a single-request metadata probe used by the live
  verification script to record status / content-type / length as evidence.
"""

from __future__ import annotations

import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": "neet-compass-etl/0.2 (+https://neetcompass.dev)",
    "Accept": "*/*",
}


class DownloadRejectedError(RuntimeError):
    """A download completed but the response was not an acceptable source file.

    Raised when ``expected_content_types`` is provided and the server's
    delivered ``Content-Type`` does not match. Unlike transient network
    failures this is a permanent condition and is never retried.
    """

    def __init__(self, url: str, actual_content_type: str | None, expected: list[str]) -> None:
        self.url = url
        self.actual_content_type = actual_content_type
        self.expected = sorted(expected)
        super().__init__(
            f"Download from {url!r} rejected: Content-Type "
            f"{actual_content_type!r} is not one of {[*self.expected]!r}"
        )


@dataclass(frozen=True)
class DownloadProbe:
    """Metadata about a single successful HTTP request (evidence capture)."""

    url: str
    status: int
    content_type: str | None
    content_length: str | None
    final_url: str

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300


def _matches_content_type(
    content_type: str | None, expected_types: list[str] | tuple[str, ...]
) -> bool:
    if not content_type:
        return False
    base = content_type.split(";", 1)[0].strip().lower()
    return any(ex.split(";", 1)[0].strip().lower() == base for ex in expected_types)


def download_file(
    url: str,
    dest_path: str | Path,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
    retries: int = 2,
    delay: float = 0.2,
    expected_content_types: list[str] | tuple[str, ...] | None = None,
) -> Path:
    """Download ``url`` to ``dest_path`` and return the destination path.

    Retries up to ``retries`` times on ``URLError`` / ``OSError`` and HTTP 5xx
    responses; raises immediately on HTTP 4xx. If ``expected_content_types``
    is given, a delivered ``Content-Type`` that does not match raises
    ``DownloadRejectedError`` without writing anything to ``dest_path``.
    Network calls use a configurable ``timeout``. ``file://`` URLs are
    supported for hermetic testing.
    """
    hdrs = dict(headers) if headers else dict(DEFAULT_HEADERS)
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            request = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                content_type = response.headers.get("Content-Type")
                data = response.read()
            if expected_content_types and not _matches_content_type(
                content_type, expected_content_types
            ):
                raise DownloadRejectedError(url, content_type, [*expected_content_types])
            dest = Path(dest_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            return dest
        except urllib.error.HTTPError as exc:
            if exc.code < 500:
                raise
            last_error = exc
            if attempt >= retries:
                break
            time.sleep(delay)
        except (urllib.error.URLError, OSError) as exc:
            last_error = exc
            if attempt >= retries:
                break
            time.sleep(delay)
    assert last_error is not None
    raise last_error


def probe(
    url: str,
    headers: dict[str, str] | None = None,
    timeout: float = 10.0,
) -> DownloadProbe | None:
    """Best-effort single-request probe for download evidence.

    Performs a lightweight GET (reading only the first 512 bytes) and returns
    a ``DownloadProbe`` with status / content-type / content-length. Returns
    ``None`` on any error so callers can branch without try/except, and so a
    verification script can record "rejected / unreachable" evidence.
    """
    hdrs = dict(headers) if headers else dict(DEFAULT_HEADERS)
    try:
        request = urllib.request.Request(url, headers=hdrs)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read(512)
            status = getattr(response, "status", 200)
            content_type = response.headers.get("Content-Type")
            content_length = response.headers.get("Content-Length")
            final_url = getattr(response, "geturl", lambda: url)()
            return DownloadProbe(
                url=url,
                status=status,
                content_type=content_type,
                content_length=content_length,
                final_url=final_url,
            )
    except Exception:
        return None


def is_downloadable(url: str) -> bool:
    """Best-effort check that ``url`` is a downloadable resource.

    Performs a lightweight ``probe``; returns ``True`` only for a 2xx response.
    """
    result = probe(url)
    return bool(result is not None and result.ok)


__all__ = [
    "DEFAULT_HEADERS",
    "DownloadProbe",
    "DownloadRejectedError",
    "download_file",
    "is_downloadable",
    "probe",
]
