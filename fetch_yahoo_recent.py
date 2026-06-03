#!/usr/bin/env python3
"""Fetch recent Yahoo Finance chart bars into a simple CSV.

Yahoo's public chart endpoint is useful for quick smoke tests, but it generally
does not provide 12 months of 1-minute bars. For the full research question,
use a vendor CSV with the analyzer.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


NY = ZoneInfo("America/New_York")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="SPY", help="Yahoo symbol, e.g. SPY or ^GSPC")
    parser.add_argument("--range", default="7d", help="Yahoo range, e.g. 1d, 5d, 7d")
    parser.add_argument("--interval", default="1m", help="Yahoo interval, e.g. 1m, 5m")
    parser.add_argument("--start", default="", help="Start date for period query, YYYY-MM-DD")
    parser.add_argument("--end", default="", help="End date for period query, YYYY-MM-DD")
    parser.add_argument("--chunk-days", type=int, default=0, help="Split start/end into N-day chunks")
    parser.add_argument("--out", required=True, help="Output CSV path")
    return parser.parse_args()


def unix_seconds(day: date, end_of_day: bool = False) -> int:
    clock = time(23, 59, 59) if end_of_day else time(0, 0)
    return int(datetime.combine(day, clock, tzinfo=NY).astimezone(timezone.utc).timestamp())


def fetch_chart(
    symbol: str,
    interval: str,
    range_: str = "",
    start: date | None = None,
    end: date | None = None,
) -> dict:
    encoded = urllib.parse.quote(symbol, safe="")
    params = {
        "interval": interval,
        "includePrePost": "false",
        "events": "history",
    }
    if start and end:
        params["period1"] = str(unix_seconds(start))
        params["period2"] = str(unix_seconds(end, end_of_day=True))
    else:
        params["range"] = range_
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}"
        f"?{urllib.parse.urlencode(params)}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def rows_from_payload(payload: dict) -> list[dict[str, object]]:
    chart = payload.get("chart", {})
    if chart.get("error"):
        raise RuntimeError(chart["error"])

    result = chart.get("result") or []
    if not result:
        raise RuntimeError("Yahoo returned no chart result")

    data = result[0]
    timestamps = data.get("timestamp") or []
    quote = (data.get("indicators", {}).get("quote") or [{}])[0]

    rows: list[dict[str, object]] = []
    for i, ts in enumerate(timestamps):
        close = quote.get("close", [None] * len(timestamps))[i]
        if close is None:
            continue
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(NY)
        rows.append(
            {
                "timestamp": dt.isoformat(),
                "open": quote.get("open", [None] * len(timestamps))[i],
                "high": quote.get("high", [None] * len(timestamps))[i],
                "low": quote.get("low", [None] * len(timestamps))[i],
                "close": close,
                "volume": quote.get("volume", [None] * len(timestamps))[i],
            }
        )
    return rows


def write_csv(rows: list[dict[str, object]], out_path: Path) -> int:
    deduped = {str(row["timestamp"]): row for row in rows}
    ordered = [deduped[key] for key in sorted(deduped)]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["timestamp", "open", "high", "low", "close", "volume"]
    with out_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ordered)
    return len(ordered)


def chunk_ranges(start: date, end: date, chunk_days: int) -> list[tuple[date, date]]:
    ranges = []
    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + timedelta(days=chunk_days - 1), end)
        ranges.append((cursor, chunk_end))
        cursor = chunk_end + timedelta(days=1)
    return ranges


def fetch_rows(args: argparse.Namespace) -> tuple[list[dict[str, object]], list[str]]:
    if not args.start and not args.end:
        return rows_from_payload(fetch_chart(args.symbol, args.interval, range_=args.range)), []

    if not args.start or not args.end:
        raise ValueError("--start and --end must be used together")
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    if end < start:
        raise ValueError("--end must be on or after --start")

    ranges = chunk_ranges(start, end, args.chunk_days or (end - start).days + 1)
    rows: list[dict[str, object]] = []
    failures: list[str] = []
    for chunk_start, chunk_end in ranges:
        label = f"{chunk_start.isoformat()}..{chunk_end.isoformat()}"
        try:
            chunk = rows_from_payload(
                fetch_chart(args.symbol, args.interval, start=chunk_start, end=chunk_end)
            )
            rows.extend(chunk)
            print(f"Fetched {len(chunk):,} rows for {label}")
        except Exception as exc:
            failures.append(f"{label}: {exc}")
            print(f"Failed {label}: {exc}", file=sys.stderr)
    return rows, failures


def main() -> int:
    args = parse_args()
    rows, failures = fetch_rows(args)
    written = write_csv(rows, Path(args.out))
    print(f"Wrote {written:,} bars to {args.out}")
    if failures:
        print(f"{len(failures):,} chunk(s) failed.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
