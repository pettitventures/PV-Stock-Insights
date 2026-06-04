#!/usr/bin/env python3
"""Build the Market-Wide Pattern Atlas reports and charts."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from sp500_intraday_trend_ai import (
    Observation,
    Stats,
    calc_stats,
    make_observations,
    read_bars,
    split_train_test,
)


CHART_DIR = Path("reports/charts")
TARGET_RULE = (("dow", "Tue"), ("minute", "13:40"))
MAG7 = {"AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"}


@dataclass(frozen=True)
class PatternScore:
    symbol: str
    group: str
    rule_type: str
    direction: str
    label: str
    rule_key: str
    full: Stats
    train: Stats
    test: Stats
    positive_years: int
    total_years: int
    survival_score: float
    confidence_grade: str
    business_read: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", default="", help="Defaults to newest universes/research_universe_*.csv")
    parser.add_argument("--data-dir", default="data/atlas")
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument("--symbols", default="", help="Optional comma-separated subset")
    parser.add_argument("--bar-minutes", type=int, default=10)
    parser.add_argument("--top", type=int, default=25)
    parser.add_argument("--min-n", type=int, default=80)
    return parser.parse_args()


def pct(value: float) -> str:
    return f"{value:.1%}"


def bps(value: float) -> str:
    return f"{value:+.3f} bps"


def safe_symbol(symbol: str) -> str:
    return symbol.upper().replace(".", "_").replace("/", "_")


def newest_universe() -> Path | None:
    paths = sorted(Path("universes").glob("research_universe_*.csv"))
    return paths[-1] if paths else None


def read_universe(path: Path | None) -> dict[str, dict[str, str]]:
    if not path or not path.exists():
        return {"SPY": {"symbol": "SPY", "is_mag7": "no", "sources": "spy_baseline"}}
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return {row["symbol"].upper(): row for row in reader if row.get("symbol")}


def wanted_symbols(args: argparse.Namespace, universe: dict[str, dict[str, str]]) -> list[str]:
    if args.symbols:
        return [symbol.strip().upper() for symbol in args.symbols.split(",") if symbol.strip()]
    return list(universe)


def find_symbol_csv(symbol: str, data_dir: Path) -> Path | None:
    safe = safe_symbol(symbol)
    matches = sorted(data_dir.glob(f"{safe}_*_1min_sip.csv"))
    if matches:
        return matches[-1]
    if symbol == "SPY":
        fallback = Path("data/spy_2021_2026_1m_alpaca_sip.csv")
        if fallback.exists():
            return fallback
    return None


def matches(obs: Observation, key: tuple[str, str] | tuple[tuple[str, str], ...]) -> bool:
    if isinstance(key[0], str):  # type: ignore[index]
        feature, value = key  # type: ignore[misc]
        return obs.features.get(feature) == value
    return all(obs.features.get(feature) == value for feature, value in key)  # type: ignore[union-attr]


def values_for(observations: list[Observation], key: tuple[str, str] | tuple[tuple[str, str], ...]) -> list[float]:
    return [obs.ret_bps for obs in observations if matches(obs, key)]


def label_for(key: tuple[str, str] | tuple[tuple[str, str], ...]) -> str:
    if isinstance(key[0], str):  # type: ignore[index]
        feature, value = key  # type: ignore[misc]
        if feature == "minute":
            hour, minute = map(int, value.split(":"))
            end = hour * 60 + minute
            start = end - 10
            return f"Daily {start // 60:02d}:{start % 60:02d}-{value}"
        return f"{feature}={value}"
    parts = dict(key)  # type: ignore[arg-type]
    if "dow" in parts and "minute" in parts:
        hour, minute = map(int, parts["minute"].split(":"))
        end = hour * 60 + minute
        start = end - 10
        return f"{parts['dow']} {start // 60:02d}:{start % 60:02d}-{parts['minute']}"
    return " + ".join(f"{feature}={value}" for feature, value in key)  # type: ignore[union-attr]


def rule_key(key: tuple[str, str] | tuple[tuple[str, str], ...]) -> str:
    if isinstance(key[0], str):  # type: ignore[index]
        feature, value = key  # type: ignore[misc]
        return f"{feature}={value}"
    return " + ".join(f"{feature}={value}" for feature, value in key)  # type: ignore[union-attr]


def yearly_direction(observations: list[Observation], key: tuple[str, str] | tuple[tuple[str, str], ...], direction: str) -> tuple[int, int]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for obs in observations:
        if matches(obs, key):
            grouped[str(obs.timestamp.year)].append(obs.ret_bps)
    positive = 0
    total = 0
    for values in grouped.values():
        if len(values) < 3:
            continue
        total += 1
        mean = calc_stats(values).mean_bps
        if (direction == "long" and mean > 0) or (direction == "short" and mean < 0):
            positive += 1
    return positive, total


def confidence(score: float, full: Stats, test: Stats, year_ratio: float) -> tuple[str, str]:
    if full.n < 60 or test.n < 20:
        return "D", "Likely noise"
    if score >= 78 and abs(test.t_stat) >= 1.5 and year_ratio >= 0.65:
        return "A", "Worth studying"
    if score >= 62 and abs(test.t_stat) >= 1.0 and year_ratio >= 0.55:
        return "B", "Worth studying"
    if score >= 45:
        return "C", "Interesting but fragile"
    return "D", "Likely noise"


def survival_score(full: Stats, train: Stats, test: Stats, positive_years: int, total_years: int, direction: str) -> float:
    if full.n == 0:
        return 0.0
    sign = 1 if direction == "long" else -1
    same_train_test = train.mean_bps * sign > 0 and test.mean_bps * sign > 0
    year_ratio = positive_years / total_years if total_years else 0.0
    sample_score = min(1.0, math.sqrt(full.n / 260))
    t_score = min(1.0, abs(test.t_stat) / 2.5)
    mean_score = min(1.0, abs(full.mean_bps) / 3.0)
    score = 100 * (
        0.30 * year_ratio
        + 0.25 * (1.0 if same_train_test else 0.0)
        + 0.20 * sample_score
        + 0.15 * t_score
        + 0.10 * mean_score
    )
    return round(score, 1)


def score_pattern(
    symbol: str,
    group: str,
    rule_type: str,
    direction: str,
    key: tuple[str, str] | tuple[tuple[str, str], ...],
    observations: list[Observation],
    train: list[Observation],
    test: list[Observation],
) -> PatternScore:
    full = calc_stats(values_for(observations, key))
    train_stats = calc_stats(values_for(train, key))
    test_stats = calc_stats(values_for(test, key))
    positive_years, total_years = yearly_direction(observations, key, direction)
    score = survival_score(full, train_stats, test_stats, positive_years, total_years, direction)
    grade, read = confidence(score, full, test_stats, positive_years / total_years if total_years else 0.0)
    return PatternScore(
        symbol=symbol,
        group=group,
        rule_type=rule_type,
        direction=direction,
        label=label_for(key),
        rule_key=rule_key(key),
        full=full,
        train=train_stats,
        test=test_stats,
        positive_years=positive_years,
        total_years=total_years,
        survival_score=score,
        confidence_grade=grade,
        business_read=read,
    )


def candidate_keys(observations: list[Observation], min_n: int) -> list[tuple[str, str] | tuple[tuple[str, str], ...]]:
    counts: dict[tuple[str, str] | tuple[tuple[str, str], ...], int] = defaultdict(int)
    for obs in observations:
        minute = obs.features["minute"]
        dow = obs.features["dow"]
        counts[("minute", minute)] += 1
        counts[((("dow", dow), ("minute", minute)))] += 1
    return [key for key, count in counts.items() if count >= min_n]


def best_patterns(
    symbol: str,
    group: str,
    observations: list[Observation],
    min_n: int,
) -> list[PatternScore]:
    train, test = split_train_test(observations)
    scored: list[PatternScore] = []
    for key in candidate_keys(observations, min_n):
        full = calc_stats(values_for(observations, key))
        if full.n < min_n:
            continue
        if full.mean_bps > 0:
            scored.append(score_pattern(symbol, group, "best_window", "long", key, observations, train, test))
        if full.mean_bps < 0:
            scored.append(score_pattern(symbol, group, "best_window", "short", key, observations, train, test))
    long_candidates = [row for row in scored if row.direction == "long"]
    short_candidates = [row for row in scored if row.direction == "short"]
    long_candidates.sort(key=lambda row: (row.survival_score, abs(row.full.mean_bps), abs(row.test.t_stat)), reverse=True)
    short_candidates.sort(key=lambda row: (row.survival_score, abs(row.full.mean_bps), abs(row.test.t_stat)), reverse=True)
    return long_candidates[:3] + short_candidates[:3]


def group_for(symbol: str, row: dict[str, str]) -> str:
    if symbol in MAG7 or row.get("is_mag7") == "yes":
        return "MAG7"
    if "vti" in row.get("sources", "") and "voo" not in row.get("sources", ""):
        return "VTI broad market"
    return "Top 100 / S&P 500 style"


def write_summary_csv(path: Path, rows: list[PatternScore]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "symbol", "group", "rule_type", "direction", "label", "rule_key", "full_n",
        "full_mean_bps", "full_hit_rate", "train_mean_bps", "test_mean_bps",
        "test_t_stat", "positive_years", "total_years", "survival_score",
        "confidence_grade", "business_read",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "symbol": row.symbol,
                    "group": row.group,
                    "rule_type": row.rule_type,
                    "direction": row.direction,
                    "label": row.label,
                    "rule_key": row.rule_key,
                    "full_n": row.full.n,
                    "full_mean_bps": f"{row.full.mean_bps:.6f}",
                    "full_hit_rate": f"{row.full.hit_rate:.4f}",
                    "train_mean_bps": f"{row.train.mean_bps:.6f}",
                    "test_mean_bps": f"{row.test.mean_bps:.6f}",
                    "test_t_stat": f"{row.test.t_stat:.4f}",
                    "positive_years": row.positive_years,
                    "total_years": row.total_years,
                    "survival_score": f"{row.survival_score:.1f}",
                    "confidence_grade": row.confidence_grade,
                    "business_read": row.business_read,
                }
            )


def table_rows(rows: list[PatternScore], limit: int) -> list[str]:
    lines = [
        "| Rank | Symbol | Pattern | Side | Avg Move | Win Rate | Test Avg | Years | Survival | Read |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for rank, row in enumerate(rows[:limit], start=1):
        lines.append(
            f"| {rank} | {row.symbol} | {row.label} | {row.direction} | {bps(row.full.mean_bps)} | "
            f"{pct(row.full.hit_rate)} | {bps(row.test.mean_bps)} | {row.positive_years}/{row.total_years} | "
            f"{row.survival_score:.1f} {row.confidence_grade} | {row.business_read} |"
        )
    return lines


def write_markdown_reports(reports_dir: Path, rows: list[PatternScore], symbols_loaded: list[str], top_n: int) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    target_rows = [row for row in rows if row.rule_type == "tuesday_1340"]
    best_rows = [row for row in rows if row.rule_type == "best_window"]
    longs = sorted([row for row in best_rows if row.direction == "long"], key=lambda row: row.survival_score, reverse=True)
    shorts = sorted([row for row in best_rows if row.direction == "short"], key=lambda row: row.survival_score, reverse=True)
    target_longs = sorted([row for row in target_rows if row.direction == "long"], key=lambda row: row.survival_score, reverse=True)
    mag7 = [row for row in rows if row.group == "MAG7"]
    broad = [row for row in rows if row.group != "MAG7"]

    overview = [
        "# Market-Wide Pattern Atlas",
        "",
        f"Symbols analyzed: {len(symbols_loaded):,}. Main discovery layer: 10-minute regular-session windows.",
        "",
        "Business question: is Tuesday 13:30-13:40 a broader market rhythm, or just a SPY quirk?",
        "",
        "## Current Read",
        "",
        business_read_for_target(target_longs, len(symbols_loaded)),
        "",
        "## Pattern Survival Score",
        "",
        "The survival score is a plain-English ranking aid. It rewards patterns that work across years, work in both train and test periods, and have enough observations. It penalizes tiny samples and one-regime stories.",
        "",
        "![Market rhythm map](charts/atlas_market_rhythm_map.svg)",
        "",
        "## Strongest Long Windows",
        "",
    ]
    overview.extend(table_rows(longs, min(top_n, 12)))
    overview.extend(["", "## Tuesday 13:30-13:40 Across Symbols", ""])
    overview.extend(table_rows(target_longs, min(top_n, 15)))
    overview.extend(["", "## Paper Tracking Plan", ""])
    overview.extend(paper_tracking_lines((longs + target_longs)[:3]))
    (reports_dir / "pattern_atlas_overview.md").write_text("\n".join(overview))

    leaderboard = [
        "# Pattern Leaderboard",
        "",
        "These are research leads, not trade recommendations. The score favors repeatability over raw excitement.",
        "",
        "![Pattern survival leaderboard](charts/atlas_survival_leaderboard.svg)",
        "",
        "## Most Consistent Long Windows",
        "",
    ]
    leaderboard.extend(table_rows(longs, top_n))
    leaderboard.extend(["", "## Most Consistent Short Windows", ""])
    leaderboard.extend(table_rows(shorts, top_n))
    leaderboard.extend(["", "## Patterns That Work Across Many Symbols", ""])
    leaderboard.extend(cross_symbol_lines(rows))
    (reports_dir / "pattern_atlas_leaderboard.md").write_text("\n".join(leaderboard))

    mag7_lines = [
        "# MAG7 Patterns",
        "",
        "This section isolates the largest technology-led names because they can dominate index behavior.",
        "",
        "![MAG7 rhythm map](charts/atlas_mag7_rhythm_map.svg)",
        "",
    ]
    mag7_lines.extend(table_rows(sorted(mag7, key=lambda row: row.survival_score, reverse=True), top_n))
    (reports_dir / "pattern_atlas_mag7.md").write_text("\n".join(mag7_lines))

    top100_lines = [
        "# Top 100 and Broad-Market Patterns",
        "",
        "This section removes the MAG7-only lens and looks for broader market rhythm.",
        "",
    ]
    top100_lines.extend(table_rows(sorted(broad, key=lambda row: row.survival_score, reverse=True), top_n))
    (reports_dir / "pattern_atlas_top100.md").write_text("\n".join(top100_lines))


def business_read_for_target(rows: list[PatternScore], symbol_count: int) -> str:
    worth = [row for row in rows if row.business_read == "Worth studying"]
    if symbol_count < 10:
        return "The three-symbol validation run is promising, but it is still a sample check. Treat this as evidence that the question is worth expanding, not as a market-wide conclusion yet."
    if len(worth) >= max(3, len(rows) * 0.25):
        return "The Tuesday 13:30-13:40 window is showing up in enough places to deserve forward paper tracking."
    return "So far, Tuesday 13:30-13:40 looks more like a symbol-specific lead than a confirmed market-wide behavior."


def paper_tracking_lines(rows: list[PatternScore]) -> list[str]:
    lines = [
        "Track the top three patterns forward for 30-60 trading days. Keep the table simple: date, symbol, planned window, gross result, estimated spread/slippage, and notes about market-moving news.",
        "",
        "| Slot | Symbol | Pattern | Side | Historical Avg | Forward Status |",
        "|---:|---|---|---|---:|---|",
    ]
    for index, row in enumerate(rows[:3], start=1):
        lines.append(f"| {index} | {row.symbol} | {row.label} | {row.direction} | {bps(row.full.mean_bps)} | Not started |")
    if not rows:
        lines.append("| 1 | n/a | n/a | n/a | n/a | Need more data |")
    return lines


def cross_symbol_lines(rows: list[PatternScore]) -> list[str]:
    grouped: dict[str, list[PatternScore]] = defaultdict(list)
    for row in rows:
        if row.rule_type == "best_window":
            grouped[f"{row.label} {row.direction}"].append(row)
    summary = []
    for label, members in grouped.items():
        useful = [row for row in members if row.business_read == "Worth studying"]
        if len(members) >= 2:
            avg_score = sum(row.survival_score for row in members) / len(members)
            summary.append((len(useful), len(members), avg_score, label))
    summary.sort(reverse=True)
    lines = ["| Pattern | Worth Studying | Symbols Seen | Avg Survival |", "|---|---:|---:|---:|"]
    for worth, count, avg_score, label in summary[:15]:
        lines.append(f"| {label} | {worth} | {count} | {avg_score:.1f} |")
    if len(lines) == 2:
        lines.append("| n/a | 0 | 0 | 0.0 |")
    return lines


def color_for(value: float, max_abs: float) -> str:
    if max_abs <= 0:
        return "#f2f5f9"
    intensity = min(1.0, abs(value) / max_abs)
    if value >= 0:
        g = int(245 - 112 * intensity)
        b = int(249 - 157 * intensity)
        return f"#1f{g:02x}{b:02x}"
    r = int(250 - 84 * intensity)
    g = int(238 - 171 * intensity)
    b = int(238 - 182 * intensity)
    return f"#{r:02x}{g:02x}{b:02x}"


def rhythm_grid(symbol_observations: dict[str, list[Observation]], symbols: set[str] | None = None) -> dict[tuple[str, str], Stats]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for symbol, observations in symbol_observations.items():
        if symbols is not None and symbol not in symbols:
            continue
        for obs in observations:
            grouped[(obs.features["dow"], obs.features["minute"])].append(obs.ret_bps)
    return {key: calc_stats(values) for key, values in grouped.items()}


def write_heatmap(path: Path, title: str, grid: dict[tuple[str, str], Stats]) -> None:
    dows = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    minutes = sorted({minute for _, minute in grid})
    cell_w, cell_h = 27, 34
    left, top = 58, 78
    width = left + cell_w * len(minutes) + 28
    height = top + cell_h * len(dows) + 42
    max_abs = max([abs(stats.mean_bps) for stats in grid.values()] + [0.01])
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="24" y="34" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#172033">{title}</text>',
        '<text x="24" y="56" font-family="Arial, sans-serif" font-size="13" fill="#667085">Average gross bps by weekday and 10-minute ending time. Green is up, red is down.</text>',
    ]
    for i, minute in enumerate(minutes):
        x = left + i * cell_w + cell_w / 2
        if i % 3 == 0:
            lines.append(f'<text x="{x:.1f}" y="{top - 14}" font-family="Arial, sans-serif" font-size="10" text-anchor="middle" fill="#667085" transform="rotate(-45 {x:.1f},{top - 14})">{minute}</text>')
    for r, dow in enumerate(dows):
        y = top + r * cell_h
        lines.append(f'<text x="18" y="{y + 22}" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#172033">{dow}</text>')
        for c, minute in enumerate(minutes):
            stats = grid.get((dow, minute), Stats(0, 0, 0, 0, 0, 0))
            x = left + c * cell_w
            color = color_for(stats.mean_bps, max_abs)
            lines.append(f'<rect x="{x}" y="{y}" width="{cell_w - 1}" height="{cell_h - 1}" fill="{color}"/>')
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def write_bar_leaderboard(path: Path, rows: list[PatternScore], title: str) -> None:
    rows = rows[:12]
    width, height = 1080, 460
    left, top, bottom = 230, 78, 46
    plot_w = width - left - 42
    row_h = 28
    max_score = max([row.survival_score for row in rows] + [1])
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="1080" height="460" fill="#ffffff"/>',
        f'<text x="24" y="36" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#172033">{title}</text>',
        '<text x="24" y="58" font-family="Arial, sans-serif" font-size="13" fill="#667085">Higher scores favor repeatability, train/test agreement, and adequate sample size.</text>',
    ]
    for index, row in enumerate(rows):
        y = top + index * row_h
        label = f"{row.symbol} {row.label}"
        bar_w = plot_w * (row.survival_score / max_score)
        color = "#1d4ed8" if row.direction == "long" else "#b42318"
        lines.append(f'<text x="24" y="{y + 18}" font-family="Arial, sans-serif" font-size="12" fill="#172033">{label}</text>')
        lines.append(f'<rect x="{left}" y="{y + 4}" width="{bar_w:.1f}" height="18" fill="{color}" opacity="0.84"/>')
        lines.append(f'<text x="{left + bar_w + 8:.1f}" y="{y + 18}" font-family="Arial, sans-serif" font-size="12" fill="#667085">{row.survival_score:.1f} {row.confidence_grade}</text>')
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def write_tuesday_symbol_chart(path: Path, rows: list[PatternScore]) -> None:
    rows = sorted([row for row in rows if row.direction == "long"], key=lambda row: row.full.mean_bps, reverse=True)[:20]
    width, height = 1080, 430
    left, top, bottom = 58, 78, 82
    plot_w = width - left - 30
    plot_h = height - top - bottom
    max_abs = max([abs(row.full.mean_bps) for row in rows] + [0.01])
    zero_y = top + plot_h / 2
    step = plot_w / max(1, len(rows))
    bar_w = max(8, step * 0.65)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="1080" height="430" fill="#ffffff"/>',
        '<text x="24" y="36" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#172033">Tuesday 13:30-13:40 by Symbol</text>',
        '<text x="24" y="58" font-family="Arial, sans-serif" font-size="13" fill="#667085">Average gross bps for the target window.</text>',
        f'<line x1="{left}" y1="{zero_y:.1f}" x2="{width - 30}" y2="{zero_y:.1f}" stroke="#9ca3af"/>',
    ]
    for index, row in enumerate(rows):
        x = left + index * step + (step - bar_w) / 2
        h = abs(row.full.mean_bps) / max_abs * (plot_h / 2)
        y = zero_y - h if row.full.mean_bps >= 0 else zero_y
        color = "#117a52" if row.full.mean_bps >= 0 else "#b42318"
        lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{max(1, h):.1f}" fill="{color}" opacity="0.86"/>')
        label_x = x + bar_w / 2
        lines.append(f'<text x="{label_x:.1f}" y="{height - 28}" font-family="Arial, sans-serif" font-size="10" text-anchor="middle" fill="#667085" transform="rotate(-40 {label_x:.1f},{height - 28})">{row.symbol}</text>')
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()
    reports_dir = Path(args.reports_dir)
    universe_path = Path(args.universe) if args.universe else newest_universe()
    universe = read_universe(universe_path)
    symbols = wanted_symbols(args, universe)
    data_dir = Path(args.data_dir)

    all_scores: list[PatternScore] = []
    loaded_symbols: list[str] = []
    observations_by_symbol: dict[str, list[Observation]] = {}
    missing: list[str] = []

    for symbol in symbols:
        csv_path = find_symbol_csv(symbol, data_dir)
        if not csv_path:
            missing.append(symbol)
            continue
        bars = read_bars(csv_path)
        observations = make_observations(bars, args.bar_minutes)
        if len(observations) < args.min_n:
            missing.append(symbol)
            continue
        row = universe.get(symbol, {"symbol": symbol, "sources": "", "is_mag7": "yes" if symbol in MAG7 else "no"})
        group = group_for(symbol, row)
        train, test = split_train_test(observations)
        loaded_symbols.append(symbol)
        observations_by_symbol[symbol] = observations
        all_scores.append(score_pattern(symbol, group, "tuesday_1340", "long", TARGET_RULE, observations, train, test))
        all_scores.extend(best_patterns(symbol, group, observations, args.min_n))

    if not loaded_symbols:
        raise RuntimeError("No symbols had usable local data. Fetch sample data first.")

    all_scores.sort(key=lambda row: row.survival_score, reverse=True)
    write_summary_csv(reports_dir / "pattern_atlas_summary.csv", all_scores)
    write_markdown_reports(reports_dir, all_scores, loaded_symbols, args.top)

    mag7_symbols = {symbol for symbol in loaded_symbols if symbol in MAG7}
    broad_symbols = {symbol for symbol in loaded_symbols if symbol not in MAG7}
    write_heatmap(CHART_DIR / "atlas_market_rhythm_map.svg", "Market Rhythm Map", rhythm_grid(observations_by_symbol))
    write_heatmap(CHART_DIR / "atlas_mag7_rhythm_map.svg", "MAG7 Rhythm Map", rhythm_grid(observations_by_symbol, mag7_symbols or None))
    if broad_symbols:
        write_heatmap(CHART_DIR / "atlas_broad_rhythm_map.svg", "Broad-Market Rhythm Map", rhythm_grid(observations_by_symbol, broad_symbols))
    write_bar_leaderboard(CHART_DIR / "atlas_survival_leaderboard.svg", all_scores, "Pattern Survival Leaderboard")
    write_tuesday_symbol_chart(CHART_DIR / "atlas_tuesday_1340_by_symbol.svg", [row for row in all_scores if row.rule_type == "tuesday_1340"])

    (reports_dir / "pattern_atlas_run_notes.md").write_text(
        "\n".join(
            [
                "# Pattern Atlas Run Notes",
                "",
                f"Universe file: {universe_path if universe_path else 'none'}",
                f"Symbols requested: {len(symbols):,}",
                f"Symbols analyzed: {len(loaded_symbols):,}",
                f"Symbols missing local data: {len(missing):,}",
                "",
                "Missing symbols are expected during sample validation or before the full Alpaca fetch completes.",
                "",
                ", ".join(missing[:80]) if missing else "No missing symbols.",
            ]
        )
    )

    print(f"Analyzed {len(loaded_symbols):,} symbols.")
    print(f"Wrote {reports_dir / 'pattern_atlas_overview.md'}")
    if missing:
        print(f"Missing or skipped symbols: {len(missing):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
