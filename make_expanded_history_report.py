#!/usr/bin/env python3
"""Build plain-English reports and charts for the 2021-2026 SPY analysis."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from sp500_intraday_trend_ai import Observation, calc_stats, make_observations, read_bars, split_train_test


CHART_DIR = Path("reports/charts")


Rule = tuple[tuple[str, str], ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/spy_2021_2026_1m_alpaca_sip.csv")
    parser.add_argument("--out", default="reports/spy_2021_2026_expanded_pattern_report.md")
    parser.add_argument("--deep-dive-out", default="reports/spy_2021_2026_1340_tuesday_deep_dive.md")
    return parser.parse_args()


def matches(obs: Observation, rule: Rule) -> bool:
    return all(obs.features.get(key) == value for key, value in rule)


def selected(observations: list[Observation], rule: Rule) -> list[Observation]:
    return [obs for obs in observations if matches(obs, rule)]


def stats_for(observations: list[Observation], rule: Rule):
    return calc_stats([obs.ret_bps for obs in selected(observations, rule)])


def pct(value: float) -> str:
    return f"{value:.1%}"


def bps(value: float) -> str:
    return f"{value:+.4f} bps"


def monthly_rows(rows: list[Observation]) -> list[tuple[str, int, float, float, float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for obs in rows:
        grouped[obs.timestamp.strftime("%Y-%m")].append(obs.ret_bps)
    output = []
    for month, values in sorted(grouped.items()):
        stats = calc_stats(values)
        output.append((month, stats.n, stats.mean_bps, stats.hit_rate, stats.total_bps))
    return output


def yearly_rows(rows: list[Observation]) -> list[tuple[str, int, float, float, float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for obs in rows:
        grouped[obs.timestamp.strftime("%Y")].append(obs.ret_bps)
    output = []
    for year, values in sorted(grouped.items()):
        stats = calc_stats(values)
        output.append((year, stats.n, stats.mean_bps, stats.hit_rate, stats.total_bps))
    return output


def window_name(rule: Rule) -> str:
    if rule == (("dow", "Tue"), ("minute", "13:40")):
        return "Tuesday 13:30-13:40 up move"
    if rule == (("minute", "13:30"),):
        return "Daily 13:20-13:30 up move"
    if rule == (("bucket_15m", "13:30"),):
        return "Daily 13:20-13:40 zone"
    if rule == (("month", "03"), ("hour", "14:00")):
        return "March 14:00 hour up move"
    if rule == (("dow", "Thu"), ("minute", "10:10")):
        return "Thursday 10:05-10:10 down move"
    if rule == (("day_of_month", "03"), ("hour", "15:00")):
        return "3rd day 15:00 hour down move"
    return " + ".join(f"{key}={value}" for key, value in rule)


def chronological_values(rows: list[Observation]) -> list[float]:
    return [obs.ret_bps for obs in sorted(rows, key=lambda obs: obs.timestamp)]


def write_bar_chart(rows: list[tuple[str, float]], path: Path, title: str, subtitle: str) -> None:
    width, height = 1080, 430
    margin_left, margin_right, margin_top, margin_bottom = 70, 28, 82, 62
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    values = [value for _, value in rows]
    max_abs = max(0.01, max(abs(v) for v in values))
    y_zero = margin_top + plot_h / 2
    scale = (plot_h / 2) / max_abs
    step = plot_w / max(1, len(rows))
    bar_w = max(4, step * 0.7)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="1080" height="430" fill="#ffffff"/>',
        f'<text x="28" y="38" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#1f2937">{title}</text>',
        f'<text x="28" y="60" font-family="Arial, sans-serif" font-size="13" fill="#6b7280">{subtitle}</text>',
    ]
    for frac in [-1, -0.5, 0, 0.5, 1]:
        y = y_zero - frac * max_abs * scale
        stroke = "#9ca3af" if frac == 0 else "#e5e7eb"
        lines.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" stroke="{stroke}"/>')
    for i, (label, value) in enumerate(rows):
        x = margin_left + i * step + (step - bar_w) / 2
        y = y_zero - max(value, 0) * scale
        h = abs(value) * scale
        color = "#117a52" if value >= 0 else "#b42318"
        lines.append(f'<rect x="{x:.1f}" y="{min(y, y_zero):.1f}" width="{bar_w:.1f}" height="{max(1, h):.1f}" fill="{color}" opacity="0.86"/>')
        label_y = height - 28
        lines.append(f'<text x="{x + bar_w / 2:.1f}" y="{label_y}" font-family="Arial, sans-serif" font-size="10" text-anchor="middle" fill="#6b7280" transform="rotate(-40 {x + bar_w / 2:.1f},{label_y})">{label}</text>')
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def write_cumulative_chart(series: list[tuple[str, list[float], str]], path: Path) -> None:
    width, height = 1120, 470
    margin_left, margin_right, margin_top, margin_bottom = 70, 190, 86, 52
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    cumulative = []
    max_len = 1
    min_y = 0.0
    max_y = 0.0
    for label, values, color in series:
        total = 0.0
        points = [0.0]
        for value in values:
            total += value
            points.append(total)
        cumulative.append((label, points, color))
        max_len = max(max_len, len(points))
        min_y = min(min_y, min(points))
        max_y = max(max_y, max(points))
    span = max(max_y - min_y, 1)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="1120" height="470" fill="#ffffff"/>',
        '<text x="28" y="38" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#1f2937">Expanded-History Candidate Paths</text>',
        '<text x="28" y="60" font-family="Arial, sans-serif" font-size="13" fill="#6b7280">Cumulative gross basis points in chronological order.</text>',
    ]
    for frac in [0, 0.25, 0.5, 0.75, 1]:
        y_value = min_y + frac * span
        y = margin_top + plot_h - frac * plot_h
        lines.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        lines.append(f'<text x="12" y="{y + 4:.1f}" font-family="Arial, sans-serif" font-size="11" fill="#6b7280">{y_value:.0f}</text>')
    for label, points, color in cumulative:
        coords = []
        for i, value in enumerate(points):
            x = margin_left + (i / max(1, max_len - 1)) * plot_w
            y = margin_top + plot_h - ((value - min_y) / span) * plot_h
            coords.append(f"{x:.1f},{y:.1f}")
        lines.append(f'<polyline points="{" ".join(coords)}" fill="none" stroke="{color}" stroke-width="2.4"/>')
    legend_y = margin_top
    for label, _, color in cumulative:
        lines.append(f'<rect x="{width - margin_right + 24}" y="{legend_y - 10}" width="12" height="12" fill="{color}"/>')
        lines.append(f'<text x="{width - margin_right + 42}" y="{legend_y}" font-family="Arial, sans-serif" font-size="12" fill="#1f2937">{label}</text>')
        legend_y += 24
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def stats_table(observations: list[Observation], rules: list[Rule]) -> list[str]:
    train, test = split_train_test(observations)
    lines = [
        "| Pattern | Full Avg | Full Win | Train Avg | Test Avg | Test Win | Test Days | Read |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    reads = {
        "Tuesday 13:30-13:40 up move": "Best simple intraday lead",
        "Daily 13:20-13:30 up move": "Weaker alone, but part of the 13:30 zone",
        "Daily 13:20-13:40 zone": "Broad 13:30-area support",
        "March 14:00 hour up move": "Strong seasonal/calendar hypothesis",
        "Thursday 10:05-10:10 down move": "Best 5-minute short-bias lead",
        "3rd day 15:00 hour down move": "Calendar short-bias hypothesis",
    }
    for rule in rules:
        full = stats_for(observations, rule)
        tr = stats_for(train, rule)
        te = stats_for(test, rule)
        name = window_name(rule)
        lines.append(
            f"| {name} | {bps(full.mean_bps)} | {pct(full.hit_rate)} | "
            f"{bps(tr.mean_bps)} | {bps(te.mean_bps)} | {pct(te.hit_rate)} | {te.n:,} | {reads.get(name, 'Research lead')} |"
        )
    return lines


def write_expanded_report(path: Path, obs10: list[Observation], obs5: list[Observation]) -> None:
    rules10 = [
        (("dow", "Tue"), ("minute", "13:40")),
        (("minute", "13:30"),),
        (("bucket_15m", "13:30"),),
        (("month", "03"), ("hour", "14:00")),
        (("day_of_month", "03"), ("hour", "15:00")),
    ]
    rules5 = [
        (("dow", "Thu"), ("minute", "10:10")),
    ]
    start = min(obs.timestamp for obs in obs10).date().isoformat()
    end = max(obs.timestamp for obs in obs10).date().isoformat()
    rows_1340 = selected(obs10, (("dow", "Tue"), ("minute", "13:40")))
    yearly_1340 = yearly_rows(rows_1340)
    positive_years = sum(1 for _, _, mean, _, _ in yearly_1340 if mean > 0)
    lines = [
        "# SPY Expanded Pattern Report: 2021-2026",
        "",
        f"Data source: Alpaca SIP consolidated 1-minute SPY bars. Regular-session analysis window: {start} through {end}.",
        "",
        "Plain-English update: adding the 2021-2026 history changes the lead pattern. The original 13:20-13:30 window is still interesting, but the stronger multi-year timing lead is more specific:",
        "",
        "**Tuesday 13:30-13:40 New York time showed the cleanest intraday long behavior in the expanded sample.**",
        "",
        "This is research, not investment advice.",
        "",
        "## Executive Takeaway",
        "",
        "The old 12-month report pointed at 13:20-13:30 as the best daily window. With more than five years of data, that exact daily window becomes less dominant. The broader 13:30 area still matters, but the stronger version is Tuesday-specific and ends at 13:40.",
        "",
        "The practical read:",
        "",
        "- Do not throw away the 13:30 idea.",
        "- Refine it: study Tuesday 13:30-13:40 first.",
        "- Treat March 14:00-hour behavior as a separate seasonal hypothesis.",
        "- Treat all calendar-specific findings as hypotheses, because more combinations create more chances for accidental patterns.",
        "",
        "## Best Expanded-History Patterns",
        "",
    ]
    lines.extend(stats_table(obs10, rules10))
    lines.extend(stats_table(obs5, rules5)[2:])
    lines.extend(
        [
            "",
            "## Tuesday 13:30-13:40 Deep Read",
            "",
            f"This pattern appeared in {sum(n for _, n, _, _, _ in yearly_1340)} Tuesday observations and was positive in {positive_years} of {len(yearly_1340)} years represented in the expanded sample.",
            "",
            "![Tuesday 13:30-13:40 yearly results](charts/spy_2021_2026_tue_1340_yearly.svg)",
            "",
            "| Year | Days | Avg Move | Win Rate | Total Gross Move |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for year, n, mean, hit, total in yearly_1340:
        lines.append(f"| {year} | {n:,} | {bps(mean)} | {pct(hit)} | {total:+.1f} bps |")
    lines.extend(
        [
            "",
            "## Candidate Path Comparison",
            "",
            "This chart compares how the strongest expanded-history leads accumulated over time. The goal is to spot whether a pattern built gradually or relied on a single lucky patch.",
            "",
            "![Expanded-history candidate paths](charts/spy_2021_2026_candidate_paths.svg)",
            "",
            "## What Changed From The 12-Month Report?",
            "",
            "The earlier report was not wrong; it was narrower. In the last 12 months, 13:20-13:30 looked unusually clean. When we add 2021, 2022, 2023, and 2024, the signal is still nearby but shifts into a more specific version: Tuesday 13:30-13:40 and the broader 13:30 zone.",
            "",
            "That is exactly why expanding the history was useful. It prevented us from overcommitting to one recent-year pattern.",
            "",
            "## Next Decision",
            "",
            "The next practical study should paper-track two variants side by side:",
            "",
            "1. The original daily 13:20-13:30 window.",
            "2. The refined Tuesday 13:30-13:40 window.",
            "",
            "For each observation, record gross move, estimated spread/slippage, and whether the day had a major market event. If Tuesday 13:30-13:40 continues to lead over the next 30-60 trading days, it becomes the better candidate for execution research.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def write_tuesday_deep_dive(path: Path, obs10: list[Observation]) -> None:
    rule = (("dow", "Tue"), ("minute", "13:40"))
    rows = selected(obs10, rule)
    train, test = split_train_test(obs10)
    full = stats_for(obs10, rule)
    tr = stats_for(train, rule)
    te = stats_for(test, rule)
    years = yearly_rows(rows)
    months = monthly_rows(rows)
    lines = [
        "# Deep Dive: Tuesday 13:30-13:40 SPY Long Window",
        "",
        "After expanding the dataset back to 2021, this became the strongest simple intraday long candidate.",
        "",
        "Plain-English thesis: on Tuesdays, SPY tended to rise from the 13:30 close to the 13:40 close more than normal.",
        "",
        "This is research, not investment advice.",
        "",
        "## Key Numbers",
        "",
        "| Measure | Result | Plain-English Meaning |",
        "|---|---:|---|",
        f"| Average move | {bps(full.mean_bps)} | Average gross Tuesday move during this 10-minute window |",
        f"| Win rate | {pct(full.hit_rate)} | Percent of matching Tuesdays that were positive |",
        f"| Times tested | {full.n:,} | Number of Tuesday observations in the sample |",
        f"| Total gross move | {full.total_bps:+.1f} bps | Sum before spread/slippage/costs |",
        "",
        "## Earlier vs Later Period",
        "",
        "| Period | Days | Avg Move | Win Rate | Total Gross Move |",
        "|---|---:|---:|---:|---:|",
        f"| Earlier period | {tr.n:,} | {bps(tr.mean_bps)} | {pct(tr.hit_rate)} | {tr.total_bps:+.1f} bps |",
        f"| Later period | {te.n:,} | {bps(te.mean_bps)} | {pct(te.hit_rate)} | {te.total_bps:+.1f} bps |",
        "",
        "## Year-by-Year",
        "",
        "![Tuesday 13:30-13:40 yearly results](charts/spy_2021_2026_tue_1340_yearly.svg)",
        "",
        "| Year | Days | Avg Move | Win Rate | Total Gross Move |",
        "|---|---:|---:|---:|---:|",
    ]
    for year, n, mean, hit, total in years:
        lines.append(f"| {year} | {n:,} | {bps(mean)} | {pct(hit)} | {total:+.1f} bps |")
    lines.extend(
        [
            "",
            "## Month-by-Month",
            "",
            "| Month | Days | Avg Move | Win Rate | Total Gross Move |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for month, n, mean, hit, total in months:
        lines.append(f"| {month} | {n:,} | {bps(mean)} | {pct(hit)} | {total:+.1f} bps |")
    lines.extend(
        [
            "",
            "## Business Read",
            "",
            "This pattern is more specific than the old daily 13:20-13:30 idea. That is both good and bad. Good, because the numbers are stronger. Bad, because a narrower rule gives us fewer examples and can be easier to overfit.",
            "",
            "The next step is not to trade it blindly. The next step is to paper-track it exactly as written and compare it against the original daily 13:20-13:30 rule.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()
    bars = read_bars(Path(args.csv))
    obs10 = make_observations(bars, 10)
    obs5 = make_observations(bars, 5)

    tue_rows = selected(obs10, (("dow", "Tue"), ("minute", "13:40")))
    write_bar_chart(
        [(year, mean) for year, _, mean, _, _ in yearly_rows(tue_rows)],
        CHART_DIR / "spy_2021_2026_tue_1340_yearly.svg",
        "Tuesday 13:30-13:40 Yearly Mean Return",
        "Average gross basis points by year.",
    )
    write_cumulative_chart(
        [
            ("Tue 13:30-13:40 long", chronological_values(tue_rows), "#2563eb"),
            ("Daily 13:20-13:30 long", chronological_values(selected(obs10, (("minute", "13:30"),))), "#117a52"),
            ("Thu 10:05-10:10 short", [-v for v in chronological_values(selected(obs5, (("dow", "Thu"), ("minute", "10:10"))))], "#b42318"),
        ],
        CHART_DIR / "spy_2021_2026_candidate_paths.svg",
    )
    write_expanded_report(Path(args.out), obs10, obs5)
    write_tuesday_deep_dive(Path(args.deep_dive_out), obs10)
    print(f"Wrote {args.out}")
    print(f"Wrote {args.deep_dive_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
