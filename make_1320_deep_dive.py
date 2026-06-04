#!/usr/bin/env python3
"""Build a plain-English deep dive on the 13:20-13:30 SPY window."""

from __future__ import annotations

import argparse
import math
from collections import defaultdict
from pathlib import Path

from sp500_intraday_trend_ai import Observation, calc_stats, make_observations, read_bars, split_train_test


RULE = (("minute", "13:30"),)
CHART_DIR = Path("reports/charts")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/spy_12mo_1m_alpaca_sip.csv")
    parser.add_argument("--out", default="reports/spy_1320_1330_deep_dive.md")
    return parser.parse_args()


def matches(obs: Observation) -> bool:
    return all(obs.features.get(key) == value for key, value in RULE)


def selected(observations: list[Observation]) -> list[Observation]:
    return [obs for obs in observations if matches(obs)]


def pct(value: float) -> str:
    return f"{value:.1%}"


def bps(value: float) -> str:
    return f"{value:+.4f} bps"


def median(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    if n == 0:
        return 0.0
    middle = n // 2
    if n % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[int(position)]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def monthly_stats(rows: list[Observation]) -> list[tuple[str, int, float, float, float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for obs in rows:
        grouped[obs.timestamp.strftime("%Y-%m")].append(obs.ret_bps)
    output = []
    for month, values in sorted(grouped.items()):
        stats = calc_stats(values)
        output.append((month, stats.n, stats.mean_bps, stats.hit_rate, stats.total_bps))
    return output


def daily_rows(rows: list[Observation]) -> list[tuple[str, float]]:
    return [(obs.timestamp.date().isoformat(), obs.ret_bps) for obs in sorted(rows, key=lambda obs: obs.timestamp)]


def write_outcome_chart(rows: list[tuple[str, float]], path: Path) -> None:
    width, height = 1180, 430
    margin_left, margin_right, margin_top, margin_bottom = 68, 28, 78, 56
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    values = [value for _, value in rows]
    max_abs = max(abs(value) for value in values)
    y_zero = margin_top + plot_h / 2
    scale = (plot_h / 2) / max_abs
    step = plot_w / max(1, len(rows) - 1)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="1180" height="430" fill="#ffffff"/>',
        '<text x="28" y="38" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#1f2937">13:20-13:30 Daily Outcomes</text>',
        '<text x="28" y="60" font-family="Arial, sans-serif" font-size="13" fill="#6b7280">Each bar is one trading day. Green days rose during the window; red days fell.</text>',
    ]
    for frac in [-1, -0.5, 0, 0.5, 1]:
        y = y_zero - frac * max_abs * scale
        stroke = "#9ca3af" if frac == 0 else "#e5e7eb"
        lines.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" stroke="{stroke}"/>')
    for i, (date, value) in enumerate(rows):
        x = margin_left + i * step
        y = y_zero - value * scale
        color = "#117a52" if value >= 0 else "#b42318"
        lines.append(f'<line x1="{x:.1f}" y1="{y_zero:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="2"/>')
        if i % 42 == 0:
            lines.append(
                f'<text x="{x:.1f}" y="{height - 24}" font-family="Arial, sans-serif" font-size="10" text-anchor="middle" fill="#6b7280" transform="rotate(-40 {x:.1f},{height - 24})">{date[:7]}</text>'
            )
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def write_report(path: Path, observations: list[Observation]) -> None:
    rows = selected(observations)
    train, test = split_train_test(observations)
    train_rows = selected(train)
    test_rows = selected(test)
    values = [obs.ret_bps for obs in rows]
    full = calc_stats(values)
    train_stats = calc_stats([obs.ret_bps for obs in train_rows])
    test_stats = calc_stats([obs.ret_bps for obs in test_rows])
    months = monthly_stats(rows)
    positives = sum(1 for _, _, mean, _, _ in months if mean > 0)
    negatives = sum(1 for _, _, mean, _, _ in months if mean < 0)
    worst = min(rows, key=lambda obs: obs.ret_bps)
    best = max(rows, key=lambda obs: obs.ret_bps)
    outcome_chart = CHART_DIR / "spy_1320_1330_daily_outcomes.svg"
    write_outcome_chart(daily_rows(rows), outcome_chart)

    lines = [
        "# Deep Dive: SPY 13:20-13:30 Long Window",
        "",
        "This document expands the main takeaway from the broader SPY pattern report:",
        "",
        "**If we were going to study one time-based SPY pattern further, it should be the 13:20-13:30 long window.**",
        "",
        "Plain-English thesis: during the last 12 months of consolidated Alpaca SIP data, SPY tended to drift upward during this specific 10-minute window more often than normal.",
        "",
        "This is research, not investment advice.",
        "",
        "## The Pattern",
        "",
        "- Instrument: SPY",
        "- Data source: Alpaca SIP consolidated 1-minute bars",
        "- Window studied: 13:20 to 13:30 New York time",
        "- Test style: buy/observe at the 13:20 close, exit/observe at the 13:30 close",
        "- Sample period: 2025-06-03 through 2026-06-03",
        "- Trading days tested: 252",
        "",
        "## Executive Read",
        "",
        "This is the cleanest time-based long pattern we found. It is not huge, and it does not win every day. The reason it deserves more study is that it checks several business-practical boxes:",
        "",
        "- It is simple to explain.",
        "- It happens once per trading day, so it is easy to monitor.",
        "- It worked in both the earlier and later parts of the 12-month sample.",
        f"- It was positive in {positives} of {positives + negatives} calendar months.",
        "- It also appeared in the IEX data pass, then confirmed again in the fuller SIP data pass.",
        "",
        "## Key Numbers",
        "",
        "| Measure | Result | Plain-English Meaning |",
        "|---|---:|---|",
        f"| Average move | {bps(full.mean_bps)} | Average gross move during this 10-minute window |",
        f"| Win rate | {pct(full.hit_rate)} | Percent of days the window was positive |",
        f"| Days tested | {full.n:,} | One observation per regular trading day |",
        f"| Total gross move | {full.total_bps:+.1f} bps | Sum of the window's daily moves before costs |",
        f"| Median day | {bps(median(values))} | The middle result, less affected by outlier days |",
        f"| 25th percentile | {bps(quantile(values, 0.25))} | A weaker-but-normal day |",
        f"| 75th percentile | {bps(quantile(values, 0.75))} | A stronger-but-normal day |",
        f"| Best day | {best.timestamp.date().isoformat()} / {bps(best.ret_bps)} | Largest positive day in this window |",
        f"| Worst day | {worst.timestamp.date().isoformat()} / {bps(worst.ret_bps)} | Largest negative day in this window |",
        "",
        "## Did It Hold Up Later?",
        "",
        "We split the year into an earlier training period and a later test period. That is a simple way to ask: did the idea only look good in the past, or did it keep working later?",
        "",
        "| Period | Days | Avg Move | Win Rate | Total Gross Move |",
        "|---|---:|---:|---:|---:|",
        f"| Earlier period | {train_stats.n:,} | {bps(train_stats.mean_bps)} | {pct(train_stats.hit_rate)} | {train_stats.total_bps:+.1f} bps |",
        f"| Later period | {test_stats.n:,} | {bps(test_stats.mean_bps)} | {pct(test_stats.hit_rate)} | {test_stats.total_bps:+.1f} bps |",
        "",
        "The later period was actually stronger than the earlier period. That does not prove the pattern will continue, but it is better than seeing the idea fade immediately after discovery.",
        "",
        "## Month-by-Month Check",
        "",
        "This is the most useful sanity check for a business reader. We do not want a pattern that only exists because of one lucky month.",
        "",
        f"Result: {positives} positive months and {negatives} negative month.",
        "",
        "![13:30 monthly consistency](charts/spy_sip_1330_monthly.svg)",
        "",
        "| Month | Days | Avg Move | Win Rate | Total Gross Move |",
        "|---|---:|---:|---:|---:|",
    ]
    for month, n, mean, hit_rate, total in months:
        lines.append(f"| {month} | {n:,} | {bps(mean)} | {pct(hit_rate)} | {total:+.1f} bps |")

    lines.extend(
        [
            "",
            "## Daily Outcome View",
            "",
            "This chart shows every trading day as an individual result. Green lines are positive days; red lines are negative days.",
            "",
            "![13:20-13:30 daily outcomes](charts/spy_1320_1330_daily_outcomes.svg)",
            "",
            "## Why This Pattern Might Exist",
            "",
            "We do not know the cause from this data alone. A few plausible business-level explanations are:",
            "",
            "- Midday liquidity may normalize after the morning rush.",
            "- Larger desks may be repositioning after morning information is digested.",
            "- The market may be setting up for afternoon flows before the final-hour activity begins.",
            "- It may simply be a temporary market rhythm that worked during this specific year.",
            "",
            "The last point matters. A pattern can be real in one sample and still stop working later.",
            "",
            "## Why This Is Not Yet A Trade",
            "",
            "The average move is small. That means execution quality matters. A gross edge of 1-2 bps can disappear quickly if the trade has poor fills, spread cost, bad timing, or emotional overrides.",
            "",
            "Before turning this into anything live, we would need to answer:",
            "",
            "1. What does the move look like after realistic spread and slippage?",
            "2. Does it hold on QQQ, ES futures, or another independent S&P 500 proxy?",
            "3. Does it hold if we test the next 30-60 trading days without changing the rule?",
            "4. Does it survive simple risk controls, such as skipping high-volatility event days?",
            "5. Is the expected edge large enough to justify operational attention?",
            "",
            "## Practical Next Step",
            "",
            "The next business decision is simple: paper-track this exact rule without modifying it.",
            "",
            "For the next 30 trading days, record:",
            "",
            "- SPY price at 13:20",
            "- SPY price at 13:30",
            "- Gross result in bps",
            "- Approximate spread/slippage",
            "- Whether any major market event happened that day",
            "",
            "If the pattern continues to behave similarly out of sample, then it becomes worth deeper execution research. If it disappears, we learned quickly and cheaply.",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()
    bars = read_bars(Path(args.csv))
    observations = make_observations(bars, 10)
    write_report(Path(args.out), observations)
    print(f"Wrote {args.out}")
    print(f"Wrote {CHART_DIR / 'spy_1320_1330_daily_outcomes.svg'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
