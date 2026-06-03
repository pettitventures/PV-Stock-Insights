#!/usr/bin/env python3
"""Search S&P 500 intraday minute data for recurring calendar/time patterns.

This is an exploratory research tool, not a trading system. It deliberately
keeps the math transparent: candidate rules are discovered on an early training
period, then scored on a later test period.
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable
from zoneinfo import ZoneInfo

import numpy as np


NY = ZoneInfo("America/New_York")
MARKET_OPEN_MINUTE = 9 * 60 + 30
MARKET_CLOSE_MINUTE = 16 * 60


@dataclass(frozen=True)
class Bar:
    timestamp: datetime
    close: float


@dataclass(frozen=True)
class Observation:
    timestamp: datetime
    ret_bps: float
    features: dict[str, str]


@dataclass(frozen=True)
class Stats:
    n: int
    mean_bps: float
    hit_rate: float
    stdev_bps: float
    t_stat: float
    total_bps: float


@dataclass(frozen=True)
class Candidate:
    rule: tuple[tuple[str, str], ...]
    train: Stats
    test: Stats
    baseline_test: Stats
    lift_bps: float
    stability: float
    score: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Minute-bar CSV path")
    parser.add_argument("--symbol", default="SPY", help="Report label")
    parser.add_argument("--timestamp-col", default="", help="Override timestamp column")
    parser.add_argument("--close-col", default="", help="Override close column")
    parser.add_argument("--out-dir", default="reports", help="Output directory")
    parser.add_argument(
        "--bar-minutes",
        type=int,
        default=1,
        help="Non-overlapping return bar size built from input closes, e.g. 1 or 10",
    )
    parser.add_argument(
        "--feature-mode",
        choices=["all", "intraday"],
        default="all",
        help="Use all calendar features or only recurring intraday/day-of-week features",
    )
    parser.add_argument("--min-train-n", type=int, default=120, help="Minimum matching train observations")
    parser.add_argument("--min-test-n", type=int, default=60, help="Minimum matching test observations")
    parser.add_argument(
        "--min-test-t",
        type=float,
        default=1.0,
        help="Minimum absolute out-of-sample t-stat for a candidate rule",
    )
    parser.add_argument("--top", type=int, default=25, help="Top candidates to report")
    return parser.parse_args()


def parse_timestamp(raw: str) -> datetime:
    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=NY)
    return dt.astimezone(NY)


def normalized_header(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def first_present(headers: Iterable[str], names: Iterable[str]) -> str | None:
    normalized = {normalized_header(h): h for h in headers}
    for name in names:
        if name in normalized:
            return normalized[name]
    return None


def read_bars(path: Path, timestamp_col: str = "", close_col: str = "") -> list[Bar]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row")
        ts_col = timestamp_col or first_present(
            reader.fieldnames, ["timestamp", "datetime", "date", "time"]
        )
        px_col = close_col or first_present(reader.fieldnames, ["close", "adj_close", "price"])
        if not ts_col or not px_col:
            raise ValueError(
                "Could not infer timestamp/close columns. Use --timestamp-col and --close-col."
            )

        bars: list[Bar] = []
        for row in reader:
            raw_ts = (row.get(ts_col) or "").strip()
            raw_close = (row.get(px_col) or "").strip()
            if not raw_ts or not raw_close or raw_close.lower() in {"nan", "none", "null"}:
                continue
            try:
                close = float(raw_close)
                if close > 0:
                    bars.append(Bar(parse_timestamp(raw_ts), close))
            except ValueError:
                continue

    bars.sort(key=lambda bar: bar.timestamp)
    deduped: list[Bar] = []
    seen: set[datetime] = set()
    for bar in bars:
        if bar.timestamp in seen:
            continue
        seen.add(bar.timestamp)
        deduped.append(bar)
    return deduped


def nth_weekday_of_month(dt: datetime) -> int:
    return ((dt.day - 1) // 7) + 1


def trading_day_maps(dates: list[datetime.date]) -> tuple[dict[datetime.date, int], dict[datetime.date, int]]:
    by_month: dict[tuple[int, int], list] = defaultdict(list)
    by_week: dict[tuple[int, int], list] = defaultdict(list)
    for date in sorted(set(dates)):
        by_month[(date.year, date.month)].append(date)
        iso = date.isocalendar()
        by_week[(iso.year, iso.week)].append(date)

    day_of_month_index = {}
    day_of_week_index = {}
    for month_dates in by_month.values():
        last = len(month_dates)
        for i, date in enumerate(month_dates, start=1):
            day_of_month_index[date] = i if i <= 3 else -(last - i + 1) if i > last - 3 else 0
    for week_dates in by_week.values():
        last = len(week_dates)
        for i, date in enumerate(week_dates, start=1):
            day_of_week_index[date] = i if i == 1 else -1 if i == last else 0
    return day_of_month_index, day_of_week_index


def build_features(dt: datetime, month_idx: int, week_idx: int) -> dict[str, str]:
    minute = dt.hour * 60 + dt.minute
    minutes_after_open = minute - MARKET_OPEN_MINUTE
    date = dt.date()
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    week_n = nth_weekday_of_month(dt)
    features = {
        "minute": f"{dt.hour:02d}:{dt.minute:02d}",
        "bucket_5m": f"{dt.hour:02d}:{(dt.minute // 5) * 5:02d}",
        "bucket_10m": f"{dt.hour:02d}:{(dt.minute // 10) * 10:02d}",
        "bucket_15m": f"{dt.hour:02d}:{(dt.minute // 15) * 15:02d}",
        "bucket_30m": f"{dt.hour:02d}:{(dt.minute // 30) * 30:02d}",
        "hour": f"{dt.hour:02d}:00",
        "dow": weekday_names[dt.weekday()],
        "month": f"{dt.month:02d}",
        "quarter": f"Q{((dt.month - 1) // 3) + 1}",
        "day_of_month": f"{dt.day:02d}",
        "week_of_month": str(week_n),
        "weekday_instance": f"{week_n}_{weekday_names[dt.weekday()]}",
        "open_30m": str(0 <= minutes_after_open < 30),
        "close_30m": str(MARKET_CLOSE_MINUTE - 30 <= minute < MARKET_CLOSE_MINUTE),
        "midday": str(11 * 60 <= minute < 14 * 60),
        "first_tuesday": str(dt.weekday() == 1 and week_n == 1),
        "third_friday": str(dt.weekday() == 4 and 15 <= dt.day <= 21),
        "turn_of_month": str(month_idx in {1, 2, 3, -1, -2, -3}),
        "first_trading_day_month": str(month_idx == 1),
        "last_trading_day_month": str(month_idx == -1),
        "first_trading_day_week": str(week_idx == 1),
        "last_trading_day_week": str(week_idx == -1),
        "date": date.isoformat(),
    }
    return features


def make_observations(bars: list[Bar], bar_minutes: int = 1) -> list[Observation]:
    if len(bars) < 2:
        return []
    if bar_minutes < 1:
        raise ValueError("--bar-minutes must be at least 1")
    dates = [bar.timestamp.date() for bar in bars]
    month_idx, week_idx = trading_day_maps(dates)
    observations: list[Observation] = []

    bars_by_date: dict[object, list[Bar]] = defaultdict(list)
    for bar in bars:
        bars_by_date[bar.timestamp.date()].append(bar)

    for date, day_bars in bars_by_date.items():
        selected: list[Bar] = []
        for bar in day_bars:
            minute = bar.timestamp.hour * 60 + bar.timestamp.minute
            offset = minute - MARKET_OPEN_MINUTE
            if 0 <= offset <= MARKET_CLOSE_MINUTE - MARKET_OPEN_MINUTE and offset % bar_minutes == 0:
                selected.append(bar)
        for prev, curr in zip(selected, selected[1:]):
            if prev.timestamp.date() != curr.timestamp.date():
                continue
            minute = curr.timestamp.hour * 60 + curr.timestamp.minute
            if not (MARKET_OPEN_MINUTE < minute <= MARKET_CLOSE_MINUTE):
                continue
            ret_bps = math.log(curr.close / prev.close) * 10_000
            features = build_features(
                curr.timestamp, month_idx[curr.timestamp.date()], week_idx[curr.timestamp.date()]
            )
            features["bar_minutes"] = str(bar_minutes)
            features["return_window"] = f"{prev.timestamp.strftime('%H:%M')}-{curr.timestamp.strftime('%H:%M')}"
            observations.append(Observation(curr.timestamp, ret_bps, features))
    return observations


def calc_stats(values: list[float] | np.ndarray) -> Stats:
    arr = np.asarray(values, dtype=float)
    n = int(arr.size)
    if n == 0:
        return Stats(0, 0.0, 0.0, 0.0, 0.0, 0.0)
    mean = float(arr.mean())
    hit_rate = float((arr > 0).mean())
    stdev = float(arr.std(ddof=1)) if n > 1 else 0.0
    t_stat = mean / (stdev / math.sqrt(n)) if stdev > 0 and n > 1 else 0.0
    total = float(arr.sum())
    return Stats(n, mean, hit_rate, stdev, t_stat, total)


def split_train_test(observations: list[Observation]) -> tuple[list[Observation], list[Observation]]:
    ordered = sorted(observations, key=lambda obs: obs.timestamp)
    unique_dates = sorted({obs.timestamp.date() for obs in ordered})
    if len(unique_dates) < 4:
        midpoint = len(ordered) // 2
        return ordered[:midpoint], ordered[midpoint:]
    split_date = unique_dates[int(len(unique_dates) * 0.65)]
    train = [obs for obs in ordered if obs.timestamp.date() < split_date]
    test = [obs for obs in ordered if obs.timestamp.date() >= split_date]
    return train, test


def group_values(observations: list[Observation], rule: tuple[tuple[str, str], ...]) -> list[float]:
    values = []
    for obs in observations:
        if all(obs.features.get(key) == value for key, value in rule):
            values.append(obs.ret_bps)
    return values


def rule_label(rule: tuple[tuple[str, str], ...]) -> str:
    return " + ".join(f"{key}={value}" for key, value in rule)


def discover_rules(
    train: list[Observation],
    test: list[Observation],
    min_train_n: int,
    min_test_n: int,
    min_test_t: float,
    feature_mode: str = "all",
) -> list[Candidate]:
    intraday_feature_keys = [
        "minute",
        "bucket_5m",
        "bucket_10m",
        "bucket_15m",
        "bucket_30m",
        "hour",
        "dow",
        "open_30m",
        "close_30m",
        "midday",
    ]
    calendar_feature_keys = [
        "month",
        "quarter",
        "day_of_month",
        "week_of_month",
        "weekday_instance",
        "open_30m",
        "close_30m",
        "midday",
        "first_tuesday",
        "third_friday",
        "turn_of_month",
        "first_trading_day_month",
        "last_trading_day_month",
        "first_trading_day_week",
        "last_trading_day_week",
    ]
    feature_keys = (
        intraday_feature_keys
        if feature_mode == "intraday"
        else intraday_feature_keys + calendar_feature_keys
    )
    feature_counts: dict[tuple[str, str], int] = Counter()
    for obs in train:
        for key in feature_keys:
            feature_counts[(key, obs.features[key])] += 1

    single_rules = [
        ((key, value),)
        for (key, value), count in feature_counts.items()
        if count >= min_train_n and value not in {"False"}
    ]

    pairs: list[tuple[tuple[str, str], ...]] = []
    coarser = [rule for rule in single_rules if rule[0][0] != "minute"]
    for i, left in enumerate(coarser):
        for right in coarser[i + 1 :]:
            keys = {left[0][0], right[0][0]}
            if len(keys) < 2:
                continue
            pairs.append(tuple(sorted([left[0], right[0]])))

    # Keep the search broad enough to catch calendar-time conjunctions while
    # avoiding an unreadable combinatorial explosion.
    rules = list(dict.fromkeys(single_rules + pairs))
    baseline_test = calc_stats([obs.ret_bps for obs in test])
    candidates: list[Candidate] = []
    seen = set()
    for rule in rules:
        if rule in seen:
            continue
        seen.add(rule)
        train_values = group_values(train, rule)
        if len(train_values) < min_train_n:
            continue
        train_stats = calc_stats(train_values)
        if abs(train_stats.t_stat) < 1.5:
            continue
        test_values = group_values(test, rule)
        if len(test_values) < min_test_n:
            continue
        test_stats = calc_stats(test_values)
        if abs(test_stats.t_stat) < min_test_t:
            continue
        lift = test_stats.mean_bps - baseline_test.mean_bps
        same_direction = (
            train_stats.mean_bps == 0
            or test_stats.mean_bps == 0
            or math.copysign(1, train_stats.mean_bps) == math.copysign(1, test_stats.mean_bps)
        )
        stability = 1.0 if same_direction else -1.0
        score = stability * abs(test_stats.t_stat) * math.sqrt(max(1, test_stats.n)) / 10
        if same_direction and abs(lift) > 0:
            candidates.append(
                Candidate(rule, train_stats, test_stats, baseline_test, lift, stability, score)
            )

    candidates.sort(
        key=lambda c: (
            abs(c.test.t_stat),
            abs(c.lift_bps),
            c.test.n,
        ),
        reverse=True,
    )
    return dedupe_candidates(candidates)


def dedupe_candidates(candidates: list[Candidate]) -> list[Candidate]:
    deduped: list[Candidate] = []
    fingerprints: set[tuple[int, int, int, int]] = set()
    for candidate in candidates:
        fingerprint = (
            candidate.train.n,
            candidate.test.n,
            round(candidate.train.mean_bps, 6),
            round(candidate.test.mean_bps, 6),
        )
        if fingerprint in fingerprints:
            continue
        fingerprints.add(fingerprint)
        deduped.append(candidate)
    return deduped


def minute_profile(observations: list[Observation]) -> list[tuple[str, Stats]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for obs in observations:
        grouped[obs.features["minute"]].append(obs.ret_bps)
    return sorted((minute, calc_stats(values)) for minute, values in grouped.items())


def write_candidates(path: Path, candidates: list[Candidate]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "rule",
                "train_n",
                "train_mean_bps",
                "train_hit_rate",
                "train_t",
                "test_n",
                "test_mean_bps",
                "test_hit_rate",
                "test_t",
                "test_lift_vs_baseline_bps",
                "test_total_bps",
            ]
        )
        for c in candidates:
            writer.writerow(
                [
                    rule_label(c.rule),
                    c.train.n,
                    f"{c.train.mean_bps:.6f}",
                    f"{c.train.hit_rate:.4f}",
                    f"{c.train.t_stat:.4f}",
                    c.test.n,
                    f"{c.test.mean_bps:.6f}",
                    f"{c.test.hit_rate:.4f}",
                    f"{c.test.t_stat:.4f}",
                    f"{c.lift_bps:.6f}",
                    f"{c.test.total_bps:.4f}",
                ]
            )


def write_minute_profile(path: Path, rows: list[tuple[str, Stats]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["minute", "n", "mean_bps", "hit_rate", "t_stat", "total_bps"])
        for minute, stats in rows:
            writer.writerow(
                [
                    minute,
                    stats.n,
                    f"{stats.mean_bps:.6f}",
                    f"{stats.hit_rate:.4f}",
                    f"{stats.t_stat:.4f}",
                    f"{stats.total_bps:.4f}",
                ]
            )


def stats_line(stats: Stats) -> str:
    return (
        f"n={stats.n:,}, mean={stats.mean_bps:.4f} bps/bar, "
        f"hit={stats.hit_rate:.1%}, t={stats.t_stat:.2f}, total={stats.total_bps:.1f} bps"
    )


def write_report(
    path: Path,
    symbol: str,
    bars: list[Bar],
    observations: list[Observation],
    train: list[Observation],
    test: list[Observation],
    candidates: list[Candidate],
    top_n: int,
    feature_mode: str,
) -> None:
    all_stats = calc_stats([obs.ret_bps for obs in observations])
    train_stats = calc_stats([obs.ret_bps for obs in train])
    test_stats = calc_stats([obs.ret_bps for obs in test])
    start = bars[0].timestamp if bars else None
    end = bars[-1].timestamp if bars else None
    dates = sorted({obs.timestamp.date() for obs in observations})

    lines = [
        f"# {symbol} Intraday Trend Research",
        "",
        "This report is exploratory research only and is not investment advice.",
        "",
        "## Data Coverage",
        "",
        f"- Bars loaded: {len(bars):,}",
        f"- Return observations: {len(observations):,}",
        f"- Trading dates: {len(dates):,}",
        f"- Start: {start.isoformat() if start else 'n/a'}",
        f"- End: {end.isoformat() if end else 'n/a'}",
        "",
        "## Baseline",
        "",
        f"- Return bar size: {observations[0].features.get('bar_minutes', '1')} minute(s)",
        f"- Feature mode: {feature_mode}",
        f"- Full sample: {stats_line(all_stats)}",
        f"- Train period: {stats_line(train_stats)}",
        f"- Test period: {stats_line(test_stats)}",
        "",
        "## Best Out-of-Sample Candidate Rules",
        "",
    ]

    if not candidates:
        lines.extend(
            [
                "No candidate rule met the minimum sample-size and train/test stability filters.",
                "",
            ]
        )
    else:
        lines.append(
            "| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |"
        )
        lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|")
        for rank, c in enumerate(candidates[:top_n], start=1):
            lines.append(
                "| "
                f"{rank} | `{rule_label(c.rule)}` | "
                f"{c.train.mean_bps:.4f} | {c.train.t_stat:.2f} | {c.test.n:,} | "
                f"{c.test.mean_bps:.4f} | {c.test.hit_rate:.1%} | {c.test.t_stat:.2f} | "
                f"{c.lift_bps:.4f} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Interpretation Notes",
            "",
            "- Treat positive findings as hypotheses until tested on a separate period or instrument.",
            "- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.",
            "- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.",
            "- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv)
    bars = read_bars(csv_path, args.timestamp_col, args.close_col)
    if len(bars) < 100:
        raise ValueError(f"Only loaded {len(bars)} bars; need more data for pattern research.")
    observations = make_observations(bars, args.bar_minutes)
    if len(observations) < 100:
        raise ValueError(f"Only built {len(observations)} return observations.")

    train, test = split_train_test(observations)
    candidates = discover_rules(
        train,
        test,
        args.min_train_n,
        args.min_test_n,
        args.min_test_t,
        args.feature_mode,
    )
    profile = minute_profile(observations)

    out_dir = Path(args.out_dir)
    stem = f"{csv_path.stem}_{args.bar_minutes}m_{args.feature_mode}"
    report_path = out_dir / f"{stem}_trend_report.md"
    candidates_path = out_dir / f"{stem}_candidate_rules.csv"
    profile_path = out_dir / f"{stem}_minute_profile.csv"

    write_report(
        report_path,
        args.symbol,
        bars,
        observations,
        train,
        test,
        candidates,
        args.top,
        args.feature_mode,
    )
    write_candidates(candidates_path, candidates)
    write_minute_profile(profile_path, profile)

    print(f"Loaded {len(bars):,} bars and {len(observations):,} return observations.")
    print(f"Report: {report_path}")
    print(f"Candidate rules: {candidates_path}")
    print(f"Minute profile: {profile_path}")
    if candidates:
        best = candidates[0]
        print(
            "Top candidate: "
            f"{rule_label(best.rule)} | test mean {best.test.mean_bps:.4f} bps, "
            f"hit {best.test.hit_rate:.1%}, t {best.test.t_stat:.2f}, n {best.test.n:,}"
        )
    else:
        print("No stable candidate rules passed filters.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
