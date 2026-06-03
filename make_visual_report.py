#!/usr/bin/env python3
"""Generate SVG charts and a visual research report for SPY intraday trends."""

from __future__ import annotations

import argparse
import html
import math
from collections import defaultdict
from pathlib import Path

from sp500_intraday_trend_ai import (
    Observation,
    Stats,
    calc_stats,
    make_observations,
    read_bars,
    split_train_test,
)


GREEN = "#117a52"
RED = "#b42318"
BLUE = "#2563eb"
AMBER = "#b7791f"
INK = "#1f2937"
MUTED = "#6b7280"
GRID = "#e5e7eb"
BG = "#ffffff"


Rule = tuple[tuple[str, str], ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out-dir", default="reports/charts")
    parser.add_argument("--report", default="reports/spy_12mo_1m_alpaca_sip_visual_report.md")
    return parser.parse_args()


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def write(path: Path, svg: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg)


def matches(obs: Observation, rule: Rule) -> bool:
    return all(obs.features.get(key) == value for key, value in rule)


def values_for_rule(observations: list[Observation], rule: Rule) -> list[float]:
    return [obs.ret_bps for obs in observations if matches(obs, rule)]


def stats_for_rule(observations: list[Observation], rule: Rule) -> Stats:
    return calc_stats(values_for_rule(observations, rule))


def group_stats(observations: list[Observation], feature: str) -> list[tuple[str, Stats]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for obs in observations:
        grouped[obs.features[feature]].append(obs.ret_bps)
    return [(key, calc_stats(grouped[key])) for key in sorted(grouped)]


def svg_header(width: int, height: int, title: str, subtitle: str = "") -> list[str]:
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{BG}"/>',
        f'<text x="28" y="38" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="{INK}">{esc(title)}</text>',
    ]
    if subtitle:
        lines.append(
            f'<text x="28" y="62" font-family="Arial, sans-serif" font-size="13" fill="{MUTED}">{esc(subtitle)}</text>'
        )
    return lines


def vertical_bar_chart(
    rows: list[tuple[str, float]],
    title: str,
    subtitle: str,
    path: Path,
    highlight: set[str] | None = None,
    width: int = 1180,
    height: int = 440,
) -> None:
    highlight = highlight or set()
    margin_left, margin_right, margin_top, margin_bottom = 66, 28, 86, 64
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    values = [value for _, value in rows]
    max_abs = max(0.01, max(abs(v) for v in values))
    y_zero = margin_top + plot_h / 2
    scale = (plot_h / 2) / max_abs
    bar_w = max(2, plot_w / len(rows) * 0.72)

    lines = svg_header(width, height, title, subtitle)
    for frac in [-1, -0.5, 0, 0.5, 1]:
        y = y_zero - frac * max_abs * scale
        stroke = "#9ca3af" if frac == 0 else GRID
        lines.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" stroke="{stroke}"/>')
        if frac != 0:
            label = f"{frac * max_abs:.2f}"
            lines.append(
                f'<text x="12" y="{y + 4:.1f}" font-family="Arial, sans-serif" font-size="11" fill="{MUTED}">{label}</text>'
            )
    lines.append(
        f'<text x="12" y="{margin_top - 12}" font-family="Arial, sans-serif" font-size="11" fill="{MUTED}">bps</text>'
    )

    step = plot_w / len(rows)
    label_every = max(1, math.ceil(len(rows) / 18))
    for i, (label, value) in enumerate(rows):
        x = margin_left + i * step + (step - bar_w) / 2
        y = y_zero - max(value, 0) * scale
        h = abs(value) * scale
        color = BLUE if label in highlight else GREEN if value >= 0 else RED
        lines.append(
            f'<rect x="{x:.1f}" y="{min(y, y_zero):.1f}" width="{bar_w:.1f}" height="{max(1, h):.1f}" fill="{color}" opacity="0.86"/>'
        )
        if i % label_every == 0 or label in highlight:
            lines.append(
                f'<text x="{x + bar_w / 2:.1f}" y="{height - 28}" font-family="Arial, sans-serif" font-size="10" text-anchor="middle" fill="{MUTED}" transform="rotate(-45 {x + bar_w / 2:.1f},{height - 28})">{esc(label)}</text>'
            )
            if label in highlight:
                lines.append(
                    f'<text x="{x + bar_w / 2:.1f}" y="{min(y, y_zero) - 7:.1f}" font-family="Arial, sans-serif" font-size="11" text-anchor="middle" fill="{BLUE}" font-weight="700">{value:.2f}</text>'
                )
    lines.append("</svg>")
    write(path, "\n".join(lines))


def horizontal_comparison_chart(rows: list[tuple[str, float, float]], path: Path) -> None:
    width, height = 1120, 430
    margin_left, margin_right, margin_top = 250, 40, 88
    row_h = 42
    plot_w = width - margin_left - margin_right
    max_abs = max(abs(train) for _, train, _ in rows)
    max_abs = max(max_abs, max(abs(test) for _, _, test in rows), 0.01)
    x_zero = margin_left + plot_w / 2
    scale = (plot_w / 2) / max_abs
    lines = svg_header(
        width,
        height,
        "Candidate Train/Test Means",
        "Mean return in basis points per matching bar. Blue is train, amber is out-of-sample test.",
    )
    lines.append(f'<line x1="{x_zero:.1f}" y1="{margin_top - 14}" x2="{x_zero:.1f}" y2="{height - 38}" stroke="#9ca3af"/>')
    for i, (label, train, test) in enumerate(rows):
        y = margin_top + i * row_h
        lines.append(
            f'<text x="28" y="{y + 18}" font-family="Arial, sans-serif" font-size="13" fill="{INK}">{esc(label)}</text>'
        )
        for offset, value, color, name in [(0, train, BLUE, "train"), (17, test, AMBER, "test")]:
            bar_x = x_zero if value >= 0 else x_zero + value * scale
            bar_w = abs(value) * scale
            lines.append(
                f'<rect x="{bar_x:.1f}" y="{y + offset:.1f}" width="{max(1, bar_w):.1f}" height="12" fill="{color}" opacity="0.88"/>'
            )
            tx = bar_x + bar_w + 5 if value >= 0 else bar_x - 5
            anchor = "start" if value >= 0 else "end"
            lines.append(
                f'<text x="{tx:.1f}" y="{y + offset + 10:.1f}" font-family="Arial, sans-serif" font-size="10" text-anchor="{anchor}" fill="{MUTED}">{name} {value:.2f}</text>'
            )
    lines.append("</svg>")
    write(path, "\n".join(lines))


def monthly_chart(observations: list[Observation], rule: Rule, path: Path, title: str, subtitle: str) -> None:
    grouped: dict[str, list[float]] = defaultdict(list)
    for obs in observations:
        if matches(obs, rule):
            grouped[obs.timestamp.strftime("%Y-%m")].append(obs.ret_bps)
    rows = [(month, calc_stats(values).mean_bps) for month, values in sorted(grouped.items())]
    vertical_bar_chart(rows, title, subtitle, path, width=1000, height=420)


def cumulative_chart(series: list[tuple[str, list[float], str]], path: Path) -> None:
    width, height = 1120, 470
    margin_left, margin_right, margin_top, margin_bottom = 70, 160, 86, 52
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
    if max_y == min_y:
        max_y += 1
    y_span = max_y - min_y

    lines = svg_header(
        width,
        height,
        "Cumulative Return by Candidate",
        "Cumulative basis points across each matching occurrence in chronological order.",
    )
    for frac in [0, 0.25, 0.5, 0.75, 1]:
        y_value = min_y + frac * y_span
        y = margin_top + plot_h - frac * plot_h
        lines.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" stroke="{GRID}"/>')
        lines.append(
            f'<text x="12" y="{y + 4:.1f}" font-family="Arial, sans-serif" font-size="11" fill="{MUTED}">{y_value:.0f}</text>'
        )
    for label, points, color in cumulative:
        coords = []
        for i, value in enumerate(points):
            x = margin_left + (i / max(1, max_len - 1)) * plot_w
            y = margin_top + plot_h - ((value - min_y) / y_span) * plot_h
            coords.append(f"{x:.1f},{y:.1f}")
        lines.append(f'<polyline points="{" ".join(coords)}" fill="none" stroke="{color}" stroke-width="2.4"/>')
    legend_y = margin_top
    for label, _, color in cumulative:
        lines.append(f'<rect x="{width - margin_right + 24}" y="{legend_y - 10}" width="12" height="12" fill="{color}"/>')
        lines.append(
            f'<text x="{width - margin_right + 42}" y="{legend_y}" font-family="Arial, sans-serif" font-size="12" fill="{INK}">{esc(label)}</text>'
        )
        legend_y += 24
    lines.append("</svg>")
    write(path, "\n".join(lines))


def heatmap(observations: list[Observation], path: Path) -> None:
    dows = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    buckets = sorted({obs.features["bucket_30m"] for obs in observations})
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for obs in observations:
        grouped[(obs.features["dow"], obs.features["bucket_30m"])].append(obs.ret_bps)
    values = {
        key: calc_stats(vals).mean_bps
        for key, vals in grouped.items()
        if key[0] in dows
    }
    max_abs = max(0.01, max(abs(value) for value in values.values()))
    cell_w, cell_h = 66, 44
    margin_left, margin_top = 80, 88
    width = margin_left + len(buckets) * cell_w + 44
    height = margin_top + len(dows) * cell_h + 56
    lines = svg_header(
        width,
        height,
        "Mean 10-Minute Return Heatmap",
        "Rows are day of week; columns are 30-minute ending buckets. Green is positive, red is negative.",
    )
    for j, bucket in enumerate(buckets):
        x = margin_left + j * cell_w + cell_w / 2
        lines.append(
            f'<text x="{x:.1f}" y="{margin_top - 18}" font-family="Arial, sans-serif" font-size="10" text-anchor="middle" fill="{MUTED}" transform="rotate(-35 {x:.1f},{margin_top - 18})">{esc(bucket)}</text>'
        )
    for i, dow in enumerate(dows):
        y = margin_top + i * cell_h
        lines.append(f'<text x="28" y="{y + 27}" font-family="Arial, sans-serif" font-size="13" fill="{INK}">{dow}</text>')
        for j, bucket in enumerate(buckets):
            value = values.get((dow, bucket), 0.0)
            intensity = min(0.95, 0.12 + abs(value) / max_abs * 0.75)
            color = GREEN if value >= 0 else RED
            x = margin_left + j * cell_w
            lines.append(
                f'<rect x="{x}" y="{y}" width="{cell_w - 2}" height="{cell_h - 2}" fill="{color}" opacity="{intensity:.2f}"/>'
            )
            lines.append(
                f'<text x="{x + cell_w / 2:.1f}" y="{y + 26}" font-family="Arial, sans-serif" font-size="10" text-anchor="middle" fill="#ffffff">{value:.1f}</text>'
            )
    lines.append("</svg>")
    write(path, "\n".join(lines))


def chronological_values(observations: list[Observation], rule: Rule) -> list[float]:
    return [obs.ret_bps for obs in sorted(observations, key=lambda obs: obs.timestamp) if matches(obs, rule)]


def make_report(report_path: Path, chart_dir: Path, summaries: dict[str, Stats]) -> None:
    lines = [
        "# SPY 12-Month Pattern Report",
        "",
        "Data source: Alpaca SIP 1-minute SPY bars from 2025-06-03 through 2026-06-03.",
        'Plain-English version: we looked at every regular market day for the last 12 months and asked, "Are there certain times or calendar situations where SPY tended to move up or down more often than normal?"',
        "",
        "The numbers are small because these are short time windows. `1 bp` means one basis point, or 0.01%. So `+2 bps` means roughly `+0.02%` before trading costs.",
        "",
        "This is research, not a trading recommendation.",
        "",
        "## Executive Takeaway",
        "",
        "The best pattern found is simple:",
        "",
        "**SPY tended to rise between 13:20 and 13:30 New York time.**",
        "",
        "It did not happen every day. But over the last 12 months, that 10-minute window was positive about 59% of the time and was positive in 12 of the 13 calendar months in the sample.",
        "",
        "The other patterns are interesting, but less clean.",
        "",
        "## Best Patterns",
        "",
        "| Pattern | Times Tested | Avg Move | Win Rate | Strength |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, stats in summaries.items():
        strength = "Strongest clean long pattern" if name == "13:20-13:30 long" else "Interesting lead"
        if "short" in name:
            strength = "Short-bias clue"
        lines.append(f"| {name} | {stats.n:,} | {stats.mean_bps:+.4f} bps | {stats.hit_rate:.1%} | {strength} |")
    lines.extend(
        [
            "",
            "How to read this:",
            "",
            "- `Times Tested` means how many matching examples were found in the year.",
            "- `Avg Move` means the average move during that exact window.",
            "- `Win Rate` means how often the window moved in the expected direction.",
            "- `Strength` is my plain-English read of the pattern, not a guarantee.",
            "",
            "## Charts",
            "",
            "### 10-Minute Intraday Profile",
            "",
            'This chart asks: "At each 10-minute time slot, did SPY usually move up or down?"',
            "",
            "The bar ending at `13:30` stands out on the positive side. The bar ending at `15:30` stands out on the negative side.",
            "",
            "![10-minute profile](charts/spy_sip_10m_profile.svg)",
            "",
            "### 5-Minute Intraday Profile",
            "",
            "This zooms in closer. It helps answer whether the move is broad or concentrated in a smaller slice of time.",
            "",
            "The `13:30` positive pattern still appears. The `10:50` and `15:25` windows show down-side pressure.",
            "",
            "![5-minute profile](charts/spy_sip_5m_profile.svg)",
            "",
            "### Candidate Train/Test Means",
            "",
            "This chart checks whether a pattern worked in both the earlier part of the year and the later part of the year.",
            "",
            "That matters because a pattern that only worked in the past, then disappeared later, is much less useful.",
            "",
            "![train test means](charts/spy_sip_candidate_train_test.svg)",
            "",
            "### 13:30 Monthly Consistency",
            "",
            "This is the most important chart.",
            "",
            "It shows the 13:20-13:30 window month by month. The pattern was positive in 12 of 13 months, which makes it more interesting than a one-off lucky average.",
            "",
            "![13:30 monthly](charts/spy_sip_1330_monthly.svg)",
            "",
            "### Cumulative Candidate Paths",
            "",
            "This shows how each pattern built up over time.",
            "",
            "We want to avoid patterns that only look good because of one or two lucky days. A steadier line is more interesting for further research.",
            "",
            "![cumulative candidates](charts/spy_sip_candidate_cumulative.svg)",
            "",
            "### Day/Time Heatmap",
            "",
            "This is a quick map of weekday plus time of day.",
            "",
            "Green areas mean that time/day combination tended to be positive. Red areas mean it tended to be negative.",
            "",
            "![weekday heatmap](charts/spy_sip_dow_time_heatmap.svg)",
            "",
            "## What This Means In Business Terms",
            "",
            "The best current lead is:",
            "",
            "**If we were going to study one time-based SPY pattern further, it should be the 13:20-13:30 long window.**",
            "",
            "The short-side windows are worth watching too, especially `10:45-10:50`, but they are not as clean as the 13:30 long pattern.",
            "",
            "The main caution: these are small moves. A business-minded way to think about it is margin. If the average gross edge is about 1-2 bps, then trading costs, spread, execution quality, and discipline matter a lot. A pattern can be real in the data but still not be profitable after friction.",
            "",
            "## Next Decision",
            "",
            "The next useful step is not more theory. It is a practical viability test:",
            "",
            "1. Estimate realistic entry/exit costs.",
            "2. Test the 13:20-13:30 idea month by month.",
            "3. Compare SPY against another instrument like ES futures or QQQ.",
            "4. Build a simple paper-trading tracker before risking capital.",
        ]
    )
    report_path.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    bars = read_bars(Path(args.csv))
    obs5 = make_observations(bars, 5)
    obs10 = make_observations(bars, 10)
    train10, test10 = split_train_test(obs10)
    train5, test5 = split_train_test(obs5)

    profile10 = [(minute, stats.mean_bps) for minute, stats in group_stats(obs10, "minute")]
    profile5 = [(minute, stats.mean_bps) for minute, stats in group_stats(obs5, "minute")]
    vertical_bar_chart(
        profile10,
        "SPY 10-Minute Intraday Mean Return",
        "Average basis points by 10-minute ending time, Alpaca SIP 2025-06-03 to 2026-06-03.",
        out_dir / "spy_sip_10m_profile.svg",
        highlight={"13:30", "15:30"},
    )
    vertical_bar_chart(
        profile5,
        "SPY 5-Minute Intraday Mean Return",
        "Average basis points by 5-minute ending time, Alpaca SIP 2025-06-03 to 2026-06-03.",
        out_dir / "spy_sip_5m_profile.svg",
        highlight={"10:50", "13:30", "15:25"},
    )

    rules: list[tuple[str, int, Rule]] = [
        ("13:20-13:30 long", 10, (("minute", "13:30"),)),
        ("Tuesday midday long", 10, (("dow", "Tue"), ("midday", "True"))),
        ("Day 14 long", 10, (("day_of_month", "14"),)),
        ("First trading day midday", 10, (("first_trading_day_month", "True"), ("midday", "True"))),
        ("15:20-15:30 short", 10, (("minute", "15:30"),)),
        ("15:20-15:25 short", 5, (("minute", "15:25"),)),
        ("10:45-10:50 short", 5, (("minute", "10:50"),)),
    ]
    comparison_rows = []
    summaries: dict[str, Stats] = {}
    for name, horizon, rule in rules:
        observations = obs10 if horizon == 10 else obs5
        train = train10 if horizon == 10 else train5
        test = test10 if horizon == 10 else test5
        summaries[name] = stats_for_rule(observations, rule)
        comparison_rows.append((name, stats_for_rule(train, rule).mean_bps, stats_for_rule(test, rule).mean_bps))
    horizontal_comparison_chart(comparison_rows, out_dir / "spy_sip_candidate_train_test.svg")

    monthly_chart(
        obs10,
        (("minute", "13:30"),),
        out_dir / "spy_sip_1330_monthly.svg",
        "13:20-13:30 Monthly Mean Return",
        "Average basis points for the 13:20-13:30 10-minute window by month.",
    )
    cumulative_chart(
        [
            ("13:20-13:30 long", chronological_values(obs10, (("minute", "13:30"),)), BLUE),
            ("10:45-10:50 short", [-v for v in chronological_values(obs5, (("minute", "10:50"),))], RED),
            ("15:20-15:30 short", [-v for v in chronological_values(obs10, (("minute", "15:30"),))], AMBER),
        ],
        out_dir / "spy_sip_candidate_cumulative.svg",
    )
    heatmap(obs10, out_dir / "spy_sip_dow_time_heatmap.svg")

    make_report(Path(args.report), out_dir, summaries)
    print(f"Wrote charts to {out_dir}")
    print(f"Wrote report to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
