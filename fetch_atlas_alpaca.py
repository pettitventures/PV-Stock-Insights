#!/usr/bin/env python3
"""Fetch Alpaca SIP 1-minute bars for the Pattern Atlas universe.

Raw CSV outputs go under data/atlas/ and remain ignored by git.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from datetime import date
from pathlib import Path

from fetch_alpaca_bars import fetch_bars, require_credentials, write_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", default="", help="Universe CSV. Defaults to newest universes/*.csv")
    parser.add_argument("--symbols", default="", help="Optional comma-separated symbol override")
    parser.add_argument("--start", default="2021-01-01")
    parser.add_argument("--end", default=date.today().isoformat())
    parser.add_argument("--feed", default="sip")
    parser.add_argument("--timeframe", default="1Min")
    parser.add_argument("--adjustment", default="all")
    parser.add_argument("--limit", type=int, default=10000)
    parser.add_argument("--sleep", type=float, default=0.15, help="Sleep between paged requests")
    parser.add_argument("--symbol-sleep", type=float, default=1.0, help="Sleep between symbols")
    parser.add_argument("--out-dir", default="data/atlas")
    parser.add_argument("--max-symbols", type=int, default=0)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def safe_symbol(symbol: str) -> str:
    return symbol.upper().replace(".", "_").replace("/", "_")


def newest_universe() -> Path:
    paths = sorted(Path("universes").glob("research_universe_*.csv"))
    if not paths:
        raise FileNotFoundError("No universe file found. Run build_research_universe.py first.")
    return paths[-1]


def read_symbols(path: Path) -> list[str]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return [row["symbol"].strip().upper() for row in reader if row.get("symbol")]


def symbol_list(args: argparse.Namespace) -> list[str]:
    if args.symbols:
        symbols = [symbol.strip().upper() for symbol in args.symbols.split(",") if symbol.strip()]
    else:
        symbols = read_symbols(Path(args.universe) if args.universe else newest_universe())
    if args.max_symbols > 0:
        symbols = symbols[: args.max_symbols]
    return symbols


def main() -> int:
    args = parse_args()
    key_id, secret_key = require_credentials()
    symbols = symbol_list(args)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(
        f"Fetching {len(symbols):,} symbols from {args.start} through {args.end} using {args.feed.upper()} {args.timeframe}.",
        flush=True,
    )

    failures: list[tuple[str, str]] = []
    for index, symbol in enumerate(symbols, start=1):
        out_path = out_dir / f"{safe_symbol(symbol)}_{args.start}_{args.end}_{args.timeframe.lower()}_{args.feed}.csv"
        if out_path.exists() and not args.force:
            print(f"[{index}/{len(symbols)}] {symbol}: exists, skipping {out_path}", flush=True)
            continue
        request_args = argparse.Namespace(
            symbol=symbol,
            start=args.start,
            end=args.end,
            timeframe=args.timeframe,
            feed=args.feed,
            adjustment=args.adjustment,
            limit=args.limit,
            sleep=args.sleep,
            out=str(out_path),
        )
        try:
            print(f"[{index}/{len(symbols)}] {symbol}: fetching", flush=True)
            rows = fetch_bars(request_args, key_id, secret_key)
            written = write_csv(rows, out_path)
            print(f"[{index}/{len(symbols)}] {symbol}: wrote {written:,} bars to {out_path}", flush=True)
        except Exception as exc:
            failures.append((symbol, str(exc)))
            print(f"[{index}/{len(symbols)}] {symbol}: error: {exc}", file=sys.stderr, flush=True)
        if args.symbol_sleep > 0 and index < len(symbols):
            time.sleep(args.symbol_sleep)

    if failures:
        print("Fetch completed with failures:", file=sys.stderr, flush=True)
        for symbol, message in failures:
            print(f"- {symbol}: {message}", file=sys.stderr, flush=True)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
