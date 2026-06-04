#!/usr/bin/env python3
"""Verify the static-only Cloudflare Pages output.

This guardrail intentionally checks the generated `share/` directory rather than
the full repository. Raw market data can exist locally under `data/`, but it must
never be part of the public static site.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


SHARE_DIR = Path("share")
REQUIRED_PAGES = {
    "index.html",
    "atlas.html",
    "leaderboard.html",
    "mag7.html",
    "top100.html",
    "report.html",
    "tuesday-1340.html",
    "charts.html",
    "methodology.html",
}
BLOCKED_SUFFIXES = {
    ".csv",
    ".env",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".duckdb",
    ".parquet",
}


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def verify_required_pages() -> None:
    missing = sorted(page for page in REQUIRED_PAGES if not (SHARE_DIR / page).exists())
    if missing:
        fail(f"missing generated page(s): {', '.join(missing)}")


def verify_no_private_artifacts() -> None:
    bad_files = []
    for path in SHARE_DIR.rglob("*"):
        if not path.is_file():
            continue
        name = path.name
        if name.startswith(".env") or path.suffix.lower() in BLOCKED_SUFFIXES:
            bad_files.append(path)
    if bad_files:
        fail("private/raw artifact(s) found in share/: " + ", ".join(map(str, bad_files)))


def verify_local_links() -> None:
    missing = []
    for html_path in SHARE_DIR.glob("*.html"):
        text = html_path.read_text()
        for target in re.findall(r'(?:src|href)="([^"]+)"', text):
            if target.startswith(("http:", "https:", "mailto:", "#")):
                continue
            target_path = (html_path.parent / target).resolve()
            if not target_path.exists():
                missing.append((html_path, target))
    if missing:
        formatted = ", ".join(f"{page}->{target}" for page, target in missing)
        fail(f"broken local link(s): {formatted}")


def main() -> int:
    if not SHARE_DIR.exists():
        fail("share/ does not exist; run python3 build_share_site.py first")
    verify_required_pages()
    verify_no_private_artifacts()
    verify_local_links()
    print("Static site verification passed.")
    print("Cloudflare Pages output directory: share")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
