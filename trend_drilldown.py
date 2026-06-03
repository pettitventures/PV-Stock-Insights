#!/usr/bin/env python3
"""Create a focused findings report for selected SPY intraday trends."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from sp500_intraday_trend_ai import (
    Observation,
    calc_stats,
    make_observations,
    read_bars,
    split_train_test,
    stats_line,
)


Rule = tuple[tuple[str, str], ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def matches(obs: Observation, rule: Rule) -> bool:
    return all(obs.features.get(key) == value for key, value in rule)


def stats_for_rule(observations: list[Observation], rule: Rule):
    return calc_stats([obs.ret_bps for obs in observations if matches(obs, rule)])


def monthly_table(observations: list[Observation], rule: Rule) -> list[tuple[str, int, float, float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for obs in observations:
        if matches(obs, rule):
            grouped[obs.timestamp.strftime("%Y-%m")].append(obs.ret_bps)
    rows = []
    for month, values in sorted(grouped.items()):
        stats = calc_stats(values)
        rows.append((month, stats.n, stats.mean_bps, stats.hit_rate))
    return rows


def rule_label(rule: Rule) -> str:
    return " + ".join(f"{key}={value}" for key, value in rule)


def write_report(path: Path, observations_by_horizon: dict[int, list[Observation]]) -> None:
    candidates: list[tuple[str, int, Rule, str]] = [
        (
            "Strongest Intraday Long",
            10,
            (("minute", "13:30"),),
            "The 13:20-13:30 close-to-close window.",
        ),
        (
            "Tuesday Midday Long",
            10,
            (("dow", "Tue"), ("midday", "True")),
            "Any 10-minute bar from 11:00 through 13:59 on Tuesdays.",
        ),
        (
            "Day 14 Long",
            10,
            (("day_of_month", "14"),),
            "All 10-minute bars on the 14th calendar day when it is a trading day.",
        ),
        (
            "First Trading Day Midday Long",
            10,
            (("first_trading_day_month", "True"), ("midday", "True")),
            "Midday 10-minute bars on the first trading day of each month.",
        ),
        (
            "Late-Day Short Bias",
            10,
            (("minute", "15:30"),),
            "The 15:20-15:30 close-to-close window.",
        ),
        (
            "5-Minute Late-Day Short Bias",
            5,
            (("minute", "15:25"),),
            "The 15:20-15:25 close-to-close window.",
        ),
        (
            "5-Minute Morning Short Bias",
            5,
            (("minute", "10:50"),),
            "The 10:45-10:50 close-to-close window.",
        ),
    ]

    lines = [
        "# SPY 12-Month SIP Trend Findings",
        "",
        "Data source: Alpaca SIP 1-minute bars, 2025-06-03 through 2026-06-03.",
        "This is exploratory research only and is not investment advice.",
        "",
    ]

    for title, horizon, rule, description in candidates:
        observations = observations_by_horizon[horizon]
        train, test = split_train_test(observations)
        full_stats = stats_for_rule(observations, rule)
        train_stats = stats_for_rule(train, rule)
        test_stats = stats_for_rule(test, rule)
        months = monthly_table(observations, rule)
        positive_months = sum(1 for _, _, mean, _ in months if mean > 0)
        negative_months = sum(1 for _, _, mean, _ in months if mean < 0)

        lines.extend(
            [
                f"## {title}",
                "",
                f"- Rule: `{rule_label(rule)}`",
                f"- Horizon: {horizon} minute(s)",
                f"- Window: {description}",
                f"- Full sample: {stats_line(full_stats)}",
                f"- Train: {stats_line(train_stats)}",
                f"- Test: {stats_line(test_stats)}",
                f"- Monthly direction: {positive_months} positive, {negative_months} negative",
                "",
                "| Month | n | Mean bps | Hit Rate |",
                "|---|---:|---:|---:|",
            ]
        )
        for month, n, mean, hit_rate in months:
            lines.append(f"| {month} | {n:,} | {mean:.4f} | {hit_rate:.1%} |")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()
    bars = read_bars(Path(args.csv))
    observations_by_horizon = {
        5: make_observations(bars, 5),
        10: make_observations(bars, 10),
    }
    write_report(Path(args.out), observations_by_horizon)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
