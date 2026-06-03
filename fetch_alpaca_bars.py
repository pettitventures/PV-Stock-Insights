#!/usr/bin/env python3
"""Fetch historical Alpaca stock bars into analyzer-ready CSV.

Credentials are read from environment variables:

    ALPACA_API_KEY_ID
    ALPACA_API_SECRET_KEY

Do not commit API keys to this repository.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from datetime import date, datetime, time as dt_time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


NY = ZoneInfo("America/New_York")
DATA_BASE_URL = "https://data.alpaca.markets/v2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="SPY", help="Ticker symbol, e.g. SPY")
    parser.add_argument("--start", required=True, help="Start date, YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date, YYYY-MM-DD")
    parser.add_argument("--timeframe", default="1Min", help="Alpaca timeframe, e.g. 1Min, 5Min, 10Min")
    parser.add_argument("--feed", default="sip", help="Alpaca feed, commonly sip or iex")
    parser.add_argument("--adjustment", default="all", help="raw, split, dividend, all, etc.")
    parser.add_argument("--limit", type=int, default=10000, help="Page size, max 10000")
    parser.add_argument("--sleep", type=float, default=0.15, help="Seconds between paged requests")
    parser.add_argument("--out", required=True, help="Output CSV path")
    return parser.parse_args()


def require_credentials() -> tuple[str, str]:
    load_local_env(Path(".env"))
    load_local_env(Path(".env.local"))
    key_id = os.environ.get("ALPACA_API_KEY_ID", "").strip()
    secret_key = os.environ.get("ALPACA_API_SECRET_KEY", "").strip()
    if not key_id or not secret_key:
        raise RuntimeError(
            "Missing Alpaca credentials. Set ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY."
        )
    return key_id, secret_key


def load_local_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def rfc3339_market_boundary(raw_date: str, end_of_day: bool = False) -> str:
    day = date.fromisoformat(raw_date)
    if end_of_day:
        requested = datetime.combine(day, dt_time(23, 59, 59), tzinfo=NY)
        latest_basic_safe = datetime.now(tz=timezone.utc) - timedelta(minutes=20)
        if requested.astimezone(timezone.utc) > latest_basic_safe:
            return latest_basic_safe.isoformat()
        return requested.astimezone(timezone.utc).isoformat()
    return datetime.combine(day, dt_time(0, 0, 0), tzinfo=NY).astimezone(timezone.utc).isoformat()


def request_json(url: str, key_id: str, secret_key: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "APCA-API-KEY-ID": key_id,
            "APCA-API-SECRET-KEY": secret_key,
            "User-Agent": "stock-trends-research/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc


def normalize_bar(symbol: str, bar: dict) -> dict[str, object]:
    timestamp = datetime.fromisoformat(bar["t"].replace("Z", "+00:00")).astimezone(NY)
    return {
        "timestamp": timestamp.isoformat(),
        "symbol": symbol,
        "open": bar.get("o"),
        "high": bar.get("h"),
        "low": bar.get("l"),
        "close": bar.get("c"),
        "volume": bar.get("v"),
        "trade_count": bar.get("n"),
        "vwap": bar.get("vw"),
    }


def fetch_bars(args: argparse.Namespace, key_id: str, secret_key: str) -> list[dict[str, object]]:
    symbol = args.symbol.upper()
    endpoint = f"{DATA_BASE_URL}/stocks/{urllib.parse.quote(symbol)}/bars"
    params = {
        "timeframe": args.timeframe,
        "start": rfc3339_market_boundary(args.start),
        "end": rfc3339_market_boundary(args.end, end_of_day=True),
        "limit": str(args.limit),
        "adjustment": args.adjustment,
        "feed": args.feed,
    }

    rows: list[dict[str, object]] = []
    page = 0
    while True:
        url = f"{endpoint}?{urllib.parse.urlencode(params)}"
        payload = request_json(url, key_id, secret_key)
        bars = payload.get("bars") or []
        page += 1
        rows.extend(normalize_bar(symbol, bar) for bar in bars)
        print(f"Fetched page {page}: {len(bars):,} bars; total {len(rows):,}")

        token = payload.get("next_page_token")
        if not token:
            break
        params["page_token"] = token
        if args.sleep > 0:
            time.sleep(args.sleep)
    return rows


def write_csv(rows: list[dict[str, object]], out_path: Path) -> int:
    deduped = {str(row["timestamp"]): row for row in rows}
    ordered = [deduped[key] for key in sorted(deduped)]
    fields = ["timestamp", "symbol", "open", "high", "low", "close", "volume", "trade_count", "vwap"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ordered)
    return len(ordered)


def main() -> int:
    args = parse_args()
    key_id, secret_key = require_credentials()
    rows = fetch_bars(args, key_id, secret_key)
    written = write_csv(rows, Path(args.out))
    print(f"Wrote {written:,} bars to {args.out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
