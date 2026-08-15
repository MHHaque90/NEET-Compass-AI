"""Controlled live verification of the official MCC sources (Sprint 3.1A).

Manual, one-shot evidence capture -- NOT an automated dependency. Makes
exactly four requests to the two verified official MCC URLs from
``config/data_sources.yaml``:

* ``probe()`` for each URL  -> records status / content-type / content-length
* ``download_file()`` for each URL -> saves the small HTML page as an artifact
  (with the hardened Content-Type validation enabled) plus a SHA-256 + size
  + timestamp manifest

Then culls the archive page's hyperlinks for MCC document families (allotment,
seat matrix, vacancy, ...) and reports which file formats MCC actually serves
(e.g. PDF/XLS vs a machine-readable CSV), which is the evidence for the
"allotment CSV real-source" status. No links are followed -- this is a census
of the page, not a crawl.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.error
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from etl.contracts.sources.mcc.download import DEFAULT_HEADERS, download_file, probe

OFFICIAL_URLS = (
    "https://mcc.nic.in/",
    "https://mcc.nic.in/archive-ug/",
)
HTML_CONTENT_TYPES = ("text/html", "application/xhtml+xml", "text/plain")
DOC_FAMILY_RE = re.compile(
    r"(allot|seat[ _-]?matrix|vacanc|joined|join|admitted|participat|bulletin|schedule)",
    re.IGNORECASE,
)
EXT_RE = re.compile(r"\.(pdf|xls|xlsx|csv|zip|doc|docx)(?:\?[^\"' >]*)?$", re.IGNORECASE)


def _cull_archive_links(html: str) -> Counter[str]:
    """Return a census of MCC document-family links on the archive page."""
    census: Counter[str] = Counter()
    for href in re.findall(r'href=["\']([^"\']+)["\']', html):
        if DOC_FAMILY_RE.search(href) and EXT_RE.search(href):
            family = DOC_FAMILY_RE.search(href).group(0).lower()
            ext = EXT_RE.search(href).group(1).lower()
            census[f"{family}:{ext}"] += 1
    return census


def main() -> int:
    evidence_root = Path("data") / "raw" / "evidence" / datetime.now(UTC).strftime("%Y-%m-%d")
    evidence_root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_at": datetime.now(UTC).isoformat(),
        "user_agent": DEFAULT_HEADERS["User-Agent"],
        "requests": [],
    }

    for url in OFFICIAL_URLS:
        probe_result = probe(url, headers=dict(DEFAULT_HEADERS), timeout=15.0)
        slug = "mcc-portal" if "archive" not in url else "mcc-ug-archive"
        dest = evidence_root / f"{slug}.html"
        download_record: dict[str, object] = {}
        try:
            download_file(
                url,
                dest,
                headers=dict(DEFAULT_HEADERS),
                timeout=30.0,
                retries=2,
                delay=1.0,
                expected_content_types=HTML_CONTENT_TYPES,
            )
            download_record = {
                "ok": True,
                "artifact": str(dest),
                "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
                "bytes": dest.stat().st_size,
            }
        except urllib.error.HTTPError as exc:
            # The hardened downloader fails fast on 4xx (permanent rejection).
            download_record = {
                "ok": False,
                "rejected_by_server": True,
                "status": exc.code,
                "reason": exc.reason,
            }
        record = {
            "url": url,
            "probe": None
            if probe_result is None
            else {
                "status": probe_result.status,
                "content_type": probe_result.content_type,
                "content_length": probe_result.content_length,
                "final_url": probe_result.final_url,
            },
            "download": download_record,
        }
        manifest["requests"].append(record)
        print(f"-> {url}")
        print(f"   probe     : {record['probe']}")
        print(f"   download  : {record['download']}")
        if download_record.get("ok") and url.endswith("archive-ug/"):
            census = _cull_archive_links(dest.read_text(encoding="utf-8", errors="replace"))
            total = sum(census.values())
            print(
                f"   archive census: {total} official document links served "
                f"in {len(census)} family:format combos"
            )
            for key, count in sorted(census.items()):
                print(f"     {key}: {count}")
        else:
            print("   (archive document census skipped: full download blocked)")

    manifest_path = evidence_root / "mcc_live_evidence.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nManifest written: {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
