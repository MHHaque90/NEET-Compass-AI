"""Tests for the network-resilient downloader.

Network independence is preserved: every HTTP interaction below is served by
``FakeResponse`` objects injected via ``patch``, so the suite never touches
the wire even though the downloader itself performs real ``urllib`` calls.
"""

from __future__ import annotations

import urllib.error
from typing import Self
from unittest.mock import patch

import pytest
from etl.contracts.sources.mcc.download import (
    DownloadRejectedError,
    download_file,
    is_downloadable,
    probe,
)

_URL = "https://mcc.nic.in/archive-ug/seatmatrix_aiq_r1_2025.csv"


class FakeResponse:
    """Minimal stand-in for ``urllib.request.urlopen`` responses."""

    def __init__(
        self,
        status: int = 200,
        headers: dict[str, str] | None = None,
        body: bytes = b"",
        url: str = _URL,
    ) -> None:
        self.status = status
        self.headers = headers or {}
        self._body = body
        self._url = url

    def read(self, size: int = -1) -> bytes:
        return self._body if size is None or size < 0 else self._body[:size]

    def geturl(self) -> str:
        return self._url

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


def _mock_urlopen(fn):
    return patch("etl.contracts.sources.mcc.download.urllib.request.urlopen", side_effect=fn)


# ── local file:// behaviour (unchanged from pre-existing coverage) ───────────


def test_download_file_from_file_uri(tmp_path) -> None:
    src = tmp_path / "src.csv"
    src.write_bytes(b"a,b\n1,2\n")
    dest = tmp_path / "dest.csv"
    result = download_file(src.as_uri(), dest, timeout=5, retries=0)
    assert result == dest
    assert dest.read_bytes() == b"a,b\n1,2\n"


def test_download_file_creates_parent_dirs(tmp_path) -> None:
    src = tmp_path / "src.csv"
    src.write_bytes(b"hello")
    dest = tmp_path / "nested" / "dir" / "out.csv"
    download_file(src.as_uri(), dest, timeout=5, retries=0)
    assert dest.read_bytes() == b"hello"


def test_download_file_retries_then_raises(tmp_path) -> None:
    dest = tmp_path / "missing.csv"
    with pytest.raises((urllib.error.URLError, OSError)):
        download_file("file:///nonexistent/missing.csv", dest, timeout=2, retries=1, delay=0)


def test_is_downloadable_false_for_missing() -> None:
    assert is_downloadable("file:///nonexistent/missing.csv") is False


# ── HTTP semantics: content-type validation ──────────────────────────────────


def test_content_type_mismatch_is_rejected_without_writing(tmp_path) -> None:
    dest = tmp_path / "allot.csv"
    fake = FakeResponse(headers={"Content-Type": "application/pdf"}, body=b"%PDF-1.4 fake")
    with (
        patch("etl.contracts.sources.mcc.download.urllib.request.urlopen", return_value=fake),
        pytest.raises(DownloadRejectedError) as exc_info,
    ):
        download_file(_URL, dest, expected_content_types=["text/csv"])
    assert "application/pdf" in str(exc_info.value)
    assert dest.exists() is False  # never trusted a surrogate file


def test_content_type_match_accepts_charset_param(tmp_path) -> None:
    dest = tmp_path / "allot.csv"
    fake = FakeResponse(headers={"Content-Type": "text/csv; charset=utf-8"}, body=b"a,b\n1,2\n")
    with patch("etl.contracts.sources.mcc.download.urllib.request.urlopen", return_value=fake):
        result = download_file(_URL, dest, expected_content_types=["text/csv"])
    assert result == dest
    assert dest.read_bytes() == b"a,b\n1,2\n"


def test_missing_content_type_is_rejected_when_expected(tmp_path) -> None:
    dest = tmp_path / "allot.csv"
    fake = FakeResponse(body=b"a,b\n1,2\n")  # no Content-Type header
    with (
        patch("etl.contracts.sources.mcc.download.urllib.request.urlopen", return_value=fake),
        pytest.raises(DownloadRejectedError),
    ):
        download_file(_URL, dest, expected_content_types=["text/csv"])
    assert dest.exists() is False


# ── HTTP semantics: status handling and retries ──────────────────────────────


def test_http_404_fails_immediately_without_retry(tmp_path) -> None:
    calls: list[int] = []

    def urlopen_factory(request, **kwargs):
        calls.append(1)
        raise urllib.error.HTTPError(_URL, 404, "Not Found", {}, None)

    with _mock_urlopen(urlopen_factory), pytest.raises(urllib.error.HTTPError):
        download_file(_URL, tmp_path / "x.csv", retries=2, delay=0)
    assert len(calls) == 1  # permanent error is never retried


def test_http_503_retries_then_succeeds(tmp_path) -> None:
    calls: list[int] = []

    def urlopen_factory(request, **kwargs):  # pragma: no branch
        calls.append(1)
        if len(calls) == 1:
            raise urllib.error.HTTPError(_URL, 503, "Service Unavailable", {}, None)
        return FakeResponse(body=b"recovered")

    with _mock_urlopen(urlopen_factory):
        dest = download_file(_URL, tmp_path / "x.csv", retries=2, delay=0)
    assert dest.read_bytes() == b"recovered"
    assert len(calls) == 2


def test_urlerror_retries_then_succeeds(tmp_path) -> None:
    calls: list[int] = []

    def urlopen_factory(request, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise urllib.error.URLError("temporary outage")
        return FakeResponse(body=b"recovered")

    with _mock_urlopen(urlopen_factory):
        dest = download_file(_URL, tmp_path / "x.csv", retries=2, delay=0)
    assert dest.read_bytes() == b"recovered"
    assert len(calls) == 2


def test_per_attempt_timeout_default_is_30_seconds(tmp_path) -> None:
    seen: dict[str, object] = {}

    def urlopen_factory(request, **kwargs):
        seen.update(kwargs)
        return FakeResponse(body=b"ok")

    with _mock_urlopen(urlopen_factory):
        download_file(_URL, tmp_path / "x.csv", retries=0)
    assert seen["timeout"] == 30.0


# ── probe: single-request metadata for evidence capture ──────────────────────


def test_probe_captures_status_and_headers() -> None:
    fake = FakeResponse(
        status=200,
        headers={"Content-Type": "text/html; charset=UTF-8", "Content-Length": "12345"},
        body=b"<html>",
        url="https://mcc.nic.in/",
    )
    with patch("etl.contracts.sources.mcc.download.urllib.request.urlopen", return_value=fake):
        result = probe("https://mcc.nic.in/")
    assert result is not None
    assert result.ok is True
    assert result.status == 200
    assert result.content_type == "text/html; charset=UTF-8"
    assert result.content_length == "12345"
    assert result.final_url == "https://mcc.nic.in/"


def test_probe_returns_none_on_failure() -> None:
    def urlopen_factory(request, **kwargs):
        raise urllib.error.URLError("blocked")

    with _mock_urlopen(urlopen_factory):
        result = probe(_URL)
    assert result is None


def test_is_downloadable_only_for_2xx() -> None:
    fake_ok = FakeResponse(status=200, body=b"ok")
    with patch("etl.contracts.sources.mcc.download.urllib.request.urlopen", return_value=fake_ok):
        assert is_downloadable(_URL) is True
    # HEAD-equivalent non-2xx (e.g. a 403 Cloudflare challenge) must be false.
    fake_denied = FakeResponse(status=403, body=b"denied")
    with patch(
        "etl.contracts.sources.mcc.download.urllib.request.urlopen", return_value=fake_denied
    ):
        assert is_downloadable(_URL) is False
