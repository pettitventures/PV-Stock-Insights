#!/usr/bin/env python3
"""Build the Market-Wide Pattern Atlas research universe.

The script tries to pull current ETF holdings from public holdings pages and
falls back to a curated large-cap seed list if a source is unavailable. The
output is a timestamped, commit-safe universe file; it is not raw market data.
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import sys
import urllib.request
from collections import OrderedDict
from datetime import date
from pathlib import Path


MAG7 = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"]
SOURCES = {
    "sp500_proxy_spy": "https://stockanalysis.com/etf/spy/holdings/",
    "voo": "https://stockanalysis.com/etf/voo/holdings/",
    "vti": "https://stockanalysis.com/etf/vti/holdings/",
}

# A fallback keeps the project usable when holdings pages change markup or the
# network is unavailable. It is intentionally broad and deduped later.
FALLBACK_TOP = [
    "NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "META", "AVGO", "TSLA", "BRK.B",
    "JPM", "LLY", "WMT", "V", "ORCL", "MA", "NFLX", "XOM", "COST", "JNJ",
    "HD", "PG", "ABBV", "BAC", "PLTR", "KO", "PM", "UNH", "GE", "CSCO",
    "TMUS", "WFC", "CRM", "ABT", "IBM", "MS", "AXP", "LIN", "MCD", "GS",
    "DIS", "MRK", "INTU", "RTX", "T", "NOW", "PEP", "UBER", "CAT", "AMD",
    "VZ", "ISRG", "BKNG", "QCOM", "TXN", "SCHW", "C", "BA", "BLK", "AMGN",
    "SPGI", "TJX", "PGR", "ADBE", "SYK", "BSX", "GILD", "DHR", "HON", "NEE",
    "AMAT", "UNP", "PFE", "LOW", "DE", "PANW", "CMCSA", "ETN", "COF", "ANET",
    "VRTX", "MU", "ADP", "LRCX", "COP", "KLAC", "MDT", "ADI", "CB", "NKE",
    "MMC", "PLD", "CRWD", "SBUX", "SO", "MO", "ICE", "HCA", "DUK", "BMY",
    "MCK", "CEG", "ELV", "SHW", "WM", "APH", "MCO", "UPS", "INTC", "FI",
    "CME", "CDNS", "SNPS", "WELL", "AON", "EQIX", "PH", "MMM", "ZTS", "ORLY",
    "CL", "CVX", "USB", "PYPL", "REGN", "EOG", "PNC", "ITW", "APO", "MAR",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="universes")
    parser.add_argument("--limit-per-source", type=int, default=100)
    parser.add_argument("--offline", action="store_true", help="Use the fallback universe only")
    return parser.parse_args()


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "PV-Stock-Insights/1.0 research universe builder",
            "Accept": "text/html,*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_stockanalysis_holdings(text: str, limit: int) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", text, flags=re.S | re.I):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, flags=re.S | re.I)
        if len(cells) < 3:
            continue
        clean = [html.unescape(re.sub(r"<[^>]+>", "", cell)).strip() for cell in cells]
        symbol = clean[1].upper().replace("/", ".")
        if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,7}", symbol):
            continue
        name = clean[2] if len(clean) > 2 else ""
        weight = clean[3].replace("%", "") if len(clean) > 3 else ""
        rows.append((symbol, name, weight))
        if len(rows) >= limit:
            break
    return rows


def add_symbol(
    universe: OrderedDict[str, dict[str, str]],
    symbol: str,
    name: str,
    source: str,
    source_rank: int,
    weight: str = "",
) -> None:
    symbol = symbol.upper().strip().replace("/", ".")
    if not symbol or symbol in {"CASH", "USD", "SYMBOL"}:
        return
    if symbol not in universe:
        universe[symbol] = {
            "symbol": symbol,
            "name": name,
            "is_mag7": "yes" if symbol in MAG7 else "no",
            "sources": source,
            "best_source_rank": str(source_rank),
            "source_weight_pct": weight,
        }
        return
    row = universe[symbol]
    sources = set(row["sources"].split(";"))
    sources.add(source)
    row["sources"] = ";".join(sorted(sources))
    row["is_mag7"] = "yes" if symbol in MAG7 else row["is_mag7"]
    if source_rank < int(row["best_source_rank"]):
        row["best_source_rank"] = str(source_rank)
        row["source_weight_pct"] = weight
    if not row["name"] and name:
        row["name"] = name


def build_universe(args: argparse.Namespace) -> OrderedDict[str, dict[str, str]]:
    universe: OrderedDict[str, dict[str, str]] = OrderedDict()
    for rank, symbol in enumerate(MAG7, start=1):
        add_symbol(universe, symbol, symbol, "mag7", rank)

    loaded_any = False
    if not args.offline:
        for source, url in SOURCES.items():
            try:
                rows = parse_stockanalysis_holdings(fetch_text(url), args.limit_per_source)
            except Exception as exc:
                print(f"warning: could not load {source}: {exc}", file=sys.stderr)
                rows = []
            if rows:
                loaded_any = True
            for rank, (symbol, name, weight) in enumerate(rows, start=1):
                add_symbol(universe, symbol, name, source, rank, weight)

    if not loaded_any or len(universe) < 100:
        if loaded_any:
            print(
                f"warning: live holdings exposed only {len(universe):,} symbols; merging fallback seed",
                file=sys.stderr,
            )
        for rank, symbol in enumerate(FALLBACK_TOP, start=1):
            add_symbol(universe, symbol, symbol, "fallback_large_cap_seed", rank)
    return universe


def write_universe(rows: OrderedDict[str, dict[str, str]], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"research_universe_{date.today().isoformat()}.csv"
    fields = ["symbol", "name", "is_mag7", "sources", "best_source_rank", "source_weight_pct"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows.values())
    return path


def main() -> int:
    args = parse_args()
    universe = build_universe(args)
    path = write_universe(universe, Path(args.out_dir))
    mag7_count = sum(1 for row in universe.values() if row["is_mag7"] == "yes")
    print(f"Wrote {len(universe):,} symbols to {path}")
    print(f"MAG7 symbols represented: {mag7_count}/7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
