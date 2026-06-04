#!/usr/bin/env python3
"""Build a colleague-friendly static website from the research reports."""

from __future__ import annotations

import html
import csv
import re
import shutil
from pathlib import Path


REPORT = Path("reports/spy_2021_2026_expanded_pattern_report.md")
DEEP_DIVE = Path("reports/spy_2021_2026_1340_tuesday_deep_dive.md")
ATLAS_OVERVIEW = Path("reports/pattern_atlas_overview.md")
ATLAS_LEADERBOARD = Path("reports/pattern_atlas_leaderboard.md")
ATLAS_MAG7 = Path("reports/pattern_atlas_mag7.md")
ATLAS_TOP100 = Path("reports/pattern_atlas_top100.md")
ATLAS_SUMMARY = Path("reports/pattern_atlas_summary.csv")
CHARTS = Path("reports/charts")
OUT = Path("share")

NAV_LINKS = [
    ("index.html", "Overview"),
    ("atlas.html", "Market-Wide Atlas"),
    ("leaderboard.html", "Leaderboard"),
    ("mag7.html", "MAG7"),
    ("top100.html", "Top 100"),
    ("report.html", "SPY Deep Dive"),
    ("tuesday-1340.html", "Tuesday 13:30"),
    ("charts.html", "Charts"),
    ("methodology.html", "Methodology"),
]

CHART_LIBRARY = [
    (
        "Market Rhythm Map",
        "charts/atlas_market_rhythm_map.svg",
        "Market-wide view of average 10-minute behavior by weekday and time of day.",
    ),
    (
        "MAG7 Rhythm Map",
        "charts/atlas_mag7_rhythm_map.svg",
        "The same rhythm-map concept isolated to the MAG7 names available in the current run.",
    ),
    (
        "Pattern Survival Leaderboard",
        "charts/atlas_survival_leaderboard.svg",
        "Ranks research leads by repeatability, train/test agreement, and sample size.",
    ),
    (
        "Tuesday 13:30-13:40 by Symbol",
        "charts/atlas_tuesday_1340_by_symbol.svg",
        "Shows whether the SPY Tuesday window appears in other symbols from the atlas run.",
    ),
    (
        "Tuesday 13:30-13:40 Yearly Results",
        "charts/spy_2021_2026_tue_1340_yearly.svg",
        "Shows the refined Tuesday pattern year by year from 2021 through 2026.",
    ),
    (
        "Expanded-History Candidate Paths",
        "charts/spy_2021_2026_candidate_paths.svg",
        "Compares the refined Tuesday pattern, the original daily 13:20-13:30 idea, and the strongest short-bias lead.",
    ),
    (
        "12-Month Reference: 10-Minute Intraday Profile",
        "charts/spy_sip_10m_profile.svg",
        "Reference chart from the earlier 12-month pass. Useful for seeing why the 13:30 area originally stood out.",
    ),
    (
        "12-Month Reference: 13:30 Monthly Consistency",
        "charts/spy_sip_1330_monthly.svg",
        "Reference chart from the earlier 12-month pass for the original 13:20-13:30 window.",
    ),
    (
        "12-Month Reference: 5-Minute Intraday Profile",
        "charts/spy_sip_5m_profile.svg",
        "Reference chart from the earlier 12-month pass for narrower windows.",
    ),
    (
        "12-Month Reference: Candidate Train/Test Means",
        "charts/spy_sip_candidate_train_test.svg",
        "Reference chart from the earlier 12-month pass.",
    ),
    (
        "12-Month Reference: Candidate Cumulative Paths",
        "charts/spy_sip_candidate_cumulative.svg",
        "Reference chart from the earlier 12-month pass.",
    ),
    (
        "12-Month Reference: Weekday/Time Heatmap",
        "charts/spy_sip_dow_time_heatmap.svg",
        "Reference chart from the earlier 12-month pass.",
    ),
    (
        "12-Month Reference: 13:20-13:30 Daily Outcomes",
        "charts/spy_1320_1330_daily_outcomes.svg",
        "Reference chart from the earlier 12-month deep dive.",
    ),
]


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: f'<a href="{html.escape(match.group(2), quote=True)}">{match.group(1)}</a>',
        escaped,
    )
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def markdown_table(lines: list[str]) -> str:
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    body_lines = lines[2:]
    html_lines = ['<div class="table-wrap"><table>', "<thead><tr>"]
    for header in headers:
        html_lines.append(f"<th>{inline_markdown(header)}</th>")
    html_lines.append("</tr></thead><tbody>")
    for line in body_lines:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        html_lines.append("<tr>")
        for cell in cells:
            html_lines.append(f"<td>{inline_markdown(cell)}</td>")
        html_lines.append("</tr>")
    html_lines.append("</tbody></table></div>")
    return "\n".join(html_lines)


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    i = 0
    in_ol = False
    in_ul = False
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if in_ul:
                out.append("</ul>")
                in_ul = False
            i += 1
            continue

        if line.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|---"):
            table_lines = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            out.append(markdown_table(table_lines))
            continue

        image = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line)
        if image:
            alt, src = image.groups()
            out.append(
                f'<figure><img src="{html.escape(src)}" alt="{html.escape(alt)}" loading="lazy"></figure>'
            )
            i += 1
            continue

        if line.startswith("# "):
            out.append(f"<h1>{inline_markdown(line[2:])}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2>{inline_markdown(line[3:])}</h2>")
        elif line.startswith("### "):
            out.append(f"<h3>{inline_markdown(line[4:])}</h3>")
        elif re.match(r"\d+\. ", line):
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline_markdown(re.sub(r'^\d+\. ', '', line))}</li>")
        elif line.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_markdown(line[2:])}</li>")
        else:
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<p>{inline_markdown(line)}</p>")
        i += 1

    if in_ol:
        out.append("</ol>")
    if in_ul:
        out.append("</ul>")
    return "\n".join(out)


def css() -> str:
    return """
    :root {
      --bg: #f4f6f8;
      --paper: #ffffff;
      --ink: #101828;
      --muted: #667085;
      --muted-2: #8a94a6;
      --line: #d8dee8;
      --line-soft: #edf1f6;
      --accent: #0f766e;
      --accent-dark: #115e59;
      --accent-soft: #e6f6f3;
      --blue: #1d4ed8;
      --blue-soft: #e9f0ff;
      --red: #b42318;
      --red-soft: #fff0ee;
      --shadow: 0 12px 30px rgba(16, 24, 40, 0.07);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }
    a { color: var(--accent-dark); font-weight: 700; }
    .site-header {
      background: var(--paper);
      border-bottom: 1px solid var(--line);
      position: sticky;
      top: 0;
      z-index: 10;
      box-shadow: 0 1px 0 rgba(16, 24, 40, 0.02);
    }
    .header-inner {
      max-width: 1320px;
      margin: 0 auto;
      padding: 12px 22px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
    }
    .brand-wrap { min-width: 190px; }
    .brand {
      display: block;
      text-decoration: none;
      color: var(--ink);
      font-size: 17px;
      font-weight: 800;
      letter-spacing: 0;
      white-space: nowrap;
    }
    .brand-sub {
      display: block;
      margin-top: 2px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 650;
    }
    .nav {
      display: flex;
      gap: 4px;
      justify-content: flex-end;
      overflow-x: auto;
      scrollbar-width: none;
    }
    .nav::-webkit-scrollbar { display: none; }
    .nav a {
      display: inline-flex;
      align-items: center;
      min-height: 36px;
      padding: 7px 11px;
      border-radius: 7px;
      color: var(--ink);
      text-decoration: none;
      font-size: 13px;
      font-weight: 750;
      white-space: nowrap;
    }
    .nav a:hover, .nav a.active {
      color: var(--accent-dark);
      background: var(--accent-soft);
    }
    main {
      max-width: 1320px;
      margin: 0 auto;
      padding: 26px 22px 72px;
    }
    .page {
      display: grid;
      gap: 22px;
    }
    .hero {
      display: grid;
      grid-template-columns: minmax(0, 0.92fr) minmax(420px, 1.08fr);
      gap: 18px;
      align-items: stretch;
    }
    .panel {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }
    .hero-copy {
      padding: clamp(24px, 4vw, 42px);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      min-height: 430px;
    }
    .hero-visual {
      padding: 14px;
      min-height: 430px;
    }
    .hero-visual figure {
      height: 100%;
      margin: 0;
      padding: 0;
      border: 0;
      background: transparent;
    }
    .hero-visual img {
      height: 100%;
      object-fit: contain;
    }
    .kicker, .eyebrow {
      margin: 0 0 10px;
      color: var(--accent);
      font-size: 12px;
      font-weight: 850;
      text-transform: uppercase;
      letter-spacing: 0.09em;
    }
    h1 {
      margin: 0 0 18px;
      font-size: clamp(34px, 5vw, 58px);
      line-height: 1.01;
      letter-spacing: 0;
    }
    h2 {
      margin: 34px 0 12px;
      font-size: clamp(22px, 3vw, 30px);
      line-height: 1.16;
      letter-spacing: 0;
    }
    h3 {
      margin: 26px 0 9px;
      font-size: 20px;
      line-height: 1.25;
      letter-spacing: 0;
    }
    p, li { font-size: 16px; }
    p { margin: 12px 0; }
    ul, ol { padding-left: 24px; }
    strong { color: var(--accent); }
    code {
      background: #eef2f7;
      border: 1px solid #d8e0ea;
      border-radius: 4px;
      padding: 1px 5px;
      font-size: 0.92em;
    }
    .muted { color: var(--muted); }
    .badge-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 18px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 30px;
      padding: 5px 9px;
      border-radius: 8px;
      background: var(--blue-soft);
      color: #1e3a8a;
      font-size: 12px;
      font-weight: 800;
    }
    .badge.good {
      background: var(--accent-soft);
      color: var(--accent-dark);
    }
    .badge.warn {
      background: #fff7e6;
      color: #8a4b00;
    }
    .metric-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }
    .metric {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      padding: 16px;
      box-shadow: 0 8px 20px rgba(16, 24, 40, 0.04);
    }
    .metric .label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }
    .metric .value {
      margin-top: 6px;
      font-size: 27px;
      line-height: 1.1;
      font-weight: 850;
      letter-spacing: 0;
    }
    .metric .detail {
      margin-top: 5px;
      color: var(--muted);
      font-size: 13px;
    }
    .section-head {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 18px;
      margin-top: 10px;
    }
    .section-head h2 { margin-top: 0; }
    .link-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }
    .link-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      padding: 16px;
      display: block;
      color: var(--ink);
      text-decoration: none;
      min-height: 138px;
      box-shadow: 0 8px 20px rgba(16, 24, 40, 0.04);
    }
    .link-card strong {
      display: block;
      margin-bottom: 6px;
      color: var(--ink);
      font-size: 18px;
    }
    .link-card span {
      color: var(--muted);
      font-size: 14px;
      font-weight: 500;
    }
    .link-card:hover {
      border-color: #99d1c9;
      transform: translateY(-1px);
    }
    .report-shell {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 260px;
      gap: 22px;
      align-items: start;
    }
    .report-body {
      min-width: 0;
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: clamp(22px, 4vw, 42px);
      box-shadow: var(--shadow);
    }
    .report-body h1 {
      font-size: clamp(28px, 4vw, 42px);
      line-height: 1.08;
      max-width: 880px;
    }
    .report-body > p:first-of-type {
      color: var(--muted);
      font-size: 17px;
      max-width: 900px;
    }
    .report-aside {
      position: sticky;
      top: 82px;
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 8px 20px rgba(16, 24, 40, 0.04);
    }
    .report-aside h2 {
      margin: 0 0 10px;
      font-size: 15px;
    }
    .aside-list {
      display: grid;
      gap: 8px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .aside-list a {
      display: block;
      padding: 8px 9px;
      border-radius: 7px;
      color: var(--ink);
      text-decoration: none;
      font-size: 13px;
      font-weight: 700;
    }
    .aside-list a:hover, .aside-list a.active { background: var(--accent-soft); color: var(--accent-dark); }
    .table-wrap {
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      margin: 16px 0 24px;
      background: var(--paper);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 720px;
      font-size: 14px;
    }
    th, td {
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }
    th {
      background: #f7f9fc;
      color: #344054;
      font-weight: 800;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    tbody tr:nth-child(even) td { background: #fbfcfe; }
    tr:last-child td { border-bottom: 0; }
    figure {
      margin: 16px 0 28px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
    }
    figure figcaption {
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
    }
    img {
      display: block;
      width: 100%;
      height: auto;
    }
    .chart-list {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    .chart-item {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 8px 20px rgba(16, 24, 40, 0.04);
    }
    .chart-item h2 {
      margin-top: 0;
      font-size: 19px;
    }
    .chart-item p {
      color: var(--muted);
      font-size: 14px;
    }
    .chart-item figure {
      margin-bottom: 0;
      padding: 0;
      border: 0;
    }
    .footer-note {
      max-width: 1320px;
      margin: 28px auto 0;
      padding-top: 18px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 14px;
    }
    .decision-band {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(280px, 0.55fr);
      gap: 14px;
      align-items: stretch;
    }
    .decision-card {
      background: var(--paper);
      border: 1px solid var(--line);
      border-left: 5px solid var(--accent);
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 8px 20px rgba(16, 24, 40, 0.04);
    }
    .decision-card h2 { margin-top: 0; }
    .rank-list {
      margin: 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 10px;
    }
    .rank-list li {
      display: grid;
      grid-template-columns: 34px minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      padding: 10px;
      border: 1px solid var(--line-soft);
      border-radius: 8px;
      background: #fbfcfe;
      font-size: 14px;
    }
    .rank {
      width: 28px;
      height: 28px;
      display: inline-grid;
      place-items: center;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent-dark);
      font-weight: 850;
      font-size: 13px;
    }
    .score {
      color: var(--muted);
      font-size: 13px;
      font-weight: 800;
      white-space: nowrap;
    }
    @media (max-width: 920px) {
      .hero, .decision-band, .report-shell { grid-template-columns: 1fr; }
      .metric-grid, .link-grid, .chart-list { grid-template-columns: 1fr 1fr; }
      .header-inner { align-items: flex-start; flex-direction: column; }
      .nav { justify-content: flex-start; }
      .report-aside { position: static; }
    }
    @media (max-width: 640px) {
      main { padding: 16px 12px 44px; }
      .hero, .metric-grid, .link-grid, .chart-list { grid-template-columns: 1fr; }
      .hero-copy, .hero-visual { min-height: 0; }
      .hero-visual img { height: auto; }
      p, li { font-size: 16px; }
      table { min-width: 640px; }
    }
    """


def nav_html(active: str) -> str:
    links = []
    for href, label in NAV_LINKS:
        class_name = ' class="active"' if href == active else ""
        links.append(f'<a href="{href}"{class_name}>{label}</a>')
    return "\n".join(links)


def sidebar_html(active: str) -> str:
    primary = [
        ("atlas.html", "Market-wide read"),
        ("leaderboard.html", "Pattern leaderboard"),
        ("mag7.html", "MAG7 patterns"),
        ("top100.html", "Top 100 patterns"),
        ("tuesday-1340.html", "Tuesday SPY case"),
        ("charts.html", "Chart library"),
        ("methodology.html", "Method notes"),
    ]
    items = []
    for href, label in primary:
        class_name = ' class="active"' if href == active else ""
        items.append(f'<li><a href="{href}"{class_name}>{label}</a></li>')
    return (
        '<aside class="report-aside">'
        "<h2>Research Sections</h2>"
        f'<ul class="aside-list">{"".join(items)}</ul>'
        "</aside>"
    )


def page_shell(body: str, title: str, active: str) -> str:
    if active == "index.html":
        content = f'<section class="page">{body}</section>'
    else:
        content = (
            '<section class="report-shell">'
            f'<article class="report-body">{body}</article>'
            f"{sidebar_html(active)}"
            "</section>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="Plain-English market pattern atlas with intraday research reports and charts.">
  <style>{css()}</style>
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <div class="brand-wrap">
        <a class="brand" href="index.html">PV Stock Insights</a>
        <span class="brand-sub">Pattern Atlas Research</span>
      </div>
      <nav class="nav" aria-label="Site navigation">
        {nav_html(active)}
      </nav>
    </div>
  </header>
  <main>
    {content}
    <div class="footer-note">Research only. Not investment advice. Generated from local Alpaca SIP data and static SVG charts; raw API keys and raw CSV data are not included in this share package.</div>
  </main>
</body>
</html>
"""


def load_atlas_summary() -> list[dict[str, str]]:
    if not ATLAS_SUMMARY.exists():
        return []
    with ATLAS_SUMMARY.open(newline="") as handle:
        return list(csv.DictReader(handle))


def top_atlas_patterns(limit: int = 3) -> list[dict[str, str]]:
    rows = [
        row for row in load_atlas_summary()
        if row.get("rule_type") in {"best_window", "tuesday_1340"}
    ]
    rows.sort(key=lambda row: float(row.get("survival_score") or 0), reverse=True)
    seen: set[tuple[str, str, str]] = set()
    output = []
    for row in rows:
        key = (row.get("symbol", ""), row.get("label", ""), row.get("direction", ""))
        if key in seen:
            continue
        seen.add(key)
        output.append(row)
        if len(output) >= limit:
            break
    return output


def rank_list_html(rows: list[dict[str, str]]) -> str:
    if not rows:
        return '<p class="muted">Run the atlas analyzer to populate the pattern leaderboard.</p>'
    items = []
    for index, row in enumerate(rows, start=1):
        symbol = html.escape(row.get("symbol", "n/a"))
        label = html.escape(row.get("label", "n/a"))
        direction = html.escape(row.get("direction", ""))
        score = html.escape(row.get("survival_score", ""))
        grade = html.escape(row.get("confidence_grade", ""))
        items.append(
            f"<li><span class=\"rank\">{index}</span>"
            f"<span><strong>{symbol}</strong><br>{label} {direction}</span>"
            f"<span class=\"score\">{score} {grade}</span></li>"
        )
    return f'<ol class="rank-list">{"".join(items)}</ol>'


def home_page() -> str:
    top_rows = top_atlas_patterns()
    atlas_note = (
        "<p>The sample atlas is live. It validates the pipeline on SPY, AAPL, and NVDA, then asks whether the SPY Tuesday window is repeating outside SPY.</p>"
        if ATLAS_OVERVIEW.exists()
        else "<p>The next phase is ready to run as a Pattern Atlas once sample symbols are fetched and analyzed.</p>"
    )
    hero_chart = (
        "charts/atlas_market_rhythm_map.svg"
        if (OUT / "charts/atlas_market_rhythm_map.svg").exists()
        else "charts/spy_2021_2026_tue_1340_yearly.svg"
    )
    return f"""
<div class="hero">
  <div class="panel hero-copy">
    <div>
    <p class="kicker">Market-wide timing research</p>
    <h1>Is the SPY timing clue actually market-wide?</h1>
    {atlas_note}
    <div class="badge-row">
      <span class="badge good">Static research site</span>
      <span class="badge">10-minute windows</span>
      <span class="badge warn">Sample run: 3 symbols</span>
    </div>
    </div>
    <div class="muted">Built for business review: rankings, charts, and plain-English reads first; raw data stays local.</div>
  </div>
  <div class="panel hero-visual">
    <figure>
      <img src="{hero_chart}" alt="Market rhythm chart">
    </figure>
  </div>
</div>

<div class="metric-grid">
  <div class="metric">
    <div class="label">Atlas question</div>
    <div class="value">Market-wide?</div>
    <div class="detail">SPY clue or broader rhythm</div>
  </div>
  <div class="metric">
    <div class="label">Primary window</div>
    <div class="value">10 minutes</div>
    <div class="detail">Main discovery layer</div>
  </div>
  <div class="metric">
    <div class="label">Target pattern</div>
    <div class="value">Tue 13:30</div>
    <div class="detail">Ends 13:40 New York time</div>
  </div>
  <div class="metric">
    <div class="label">Project posture</div>
    <div class="value">Static</div>
    <div class="detail">No raw data in public site</div>
  </div>
</div>

<div class="decision-band">
  <section class="decision-card">
    <p class="eyebrow">Current Read</p>
    <h2>Promising, but not proven market-wide yet.</h2>
    <p>The first sample run says the Tuesday 13:30-13:40 idea deserves expansion. It does not yet prove the behavior exists across the full market universe.</p>
  </section>
  <section class="decision-card">
    <p class="eyebrow">Top Sample Leads</p>
    {rank_list_html(top_rows)}
  </section>
</div>

<div class="section-head">
  <div>
    <p class="eyebrow">Research Map</p>
    <h2>Where to go next</h2>
  </div>
</div>
<div class="link-grid">
  <a class="link-card" href="atlas.html">
    <strong>Market-Wide Atlas</strong>
    <span>The main overview for the broader symbol universe.</span>
  </a>
  <a class="link-card" href="leaderboard.html">
    <strong>Pattern Leaderboard</strong>
    <span>Most consistent long/short windows and cross-symbol patterns.</span>
  </a>
  <a class="link-card" href="mag7.html">
    <strong>MAG7 Patterns</strong>
    <span>A focused look at the highest-impact mega-cap names.</span>
  </a>
  <a class="link-card" href="top100.html">
    <strong>Top 100 Patterns</strong>
    <span>Broad-market names outside the MAG7 lens.</span>
  </a>
  <a class="link-card" href="tuesday-1340.html">
    <strong>Tuesday Pattern</strong>
    <span>The focused SPY case for Tuesday 13:30-13:40.</span>
  </a>
  <a class="link-card" href="report.html">
    <strong>SPY Deep Dive</strong>
    <span>The broader plain-English report covering the 2021-2026 rerun.</span>
  </a>
  <a class="link-card" href="charts.html">
    <strong>Chart Library</strong>
    <span>All supporting visuals in one place for quick review.</span>
  </a>
  <a class="link-card" href="methodology.html">
    <strong>Methodology</strong>
    <span>Data source, assumptions, limitations, and what should be tested next.</span>
  </a>
</div>
"""


def charts_page() -> str:
    items = []
    for title, src, description in CHART_LIBRARY:
        if not (OUT / src).exists():
            continue
        items.append(
            f"""
<section class="chart-item">
  <h2>{html.escape(title)}</h2>
  <p>{html.escape(description)}</p>
  <figure>
    <img src="{html.escape(src)}" alt="{html.escape(title)}" loading="lazy">
  </figure>
</section>
"""
        )
    return (
        "<h1>Chart Library</h1>\n"
        "<p>These are the visuals behind the reports. Use this page when you want to review the evidence without reading the full narrative.</p>\n"
        '<div class="chart-list">'
        + "\n".join(items)
        + "</div>"
    )


def methodology_page() -> str:
    return """
<h1>Methodology and Notes</h1>

<h2>Static-Only Project Posture</h2>
<p>This site is intentionally static. Raw 1-minute bars stay local under <code>data/</code>, API keys stay in local environment files, and Cloudflare Pages serves only the generated <code>share/</code> folder.</p>

<h2>What We Studied</h2>
<p>The SPY deep dive used 1-minute bars from Alpaca SIP, covering 2021-01-04 through 2026-06-03 for regular-session observations. The Pattern Atlas uses the same bar logic across every symbol with local data available.</p>

<h2>How The Pattern Search Worked</h2>
<p>The scripts convert 1-minute bars into clean 10-minute windows for the main discovery layer. The atlas scores daily windows and weekday/time windows, then asks whether the same idea survives across train/test periods and years.</p>

<h2>Pattern Survival Score</h2>
<p>The score rewards multi-year consistency, train/test agreement, meaningful sample size, and out-of-sample strength. It is a ranking tool, not proof that a pattern will work live.</p>

<h2>How To Read Basis Points</h2>
<p>A basis point is 0.01%. A move of +2 bps is roughly +0.02%. That is small, which is why execution costs matter.</p>

<h2>Why Train/Test Matters</h2>
<p>The year was split into an earlier period and a later period. A pattern is more interesting when it works in both sections instead of only looking good in the original search period.</p>

<h2>What Is Not Included</h2>
<ul>
  <li>Trading costs</li>
  <li>Bid/ask spread</li>
  <li>Slippage</li>
  <li>Tax impact</li>
  <li>Order timing and fill quality</li>
  <li>Out-of-sample days after 2026-06-03</li>
</ul>

<h2>Recommended Next Step</h2>
<p>Paper-track the top three atlas patterns for 30-60 trading days. Record gross result, estimated spread/slippage, and whether the day had a major market event.</p>
"""


def fallback_page(title: str, body: str) -> str:
    return f"<h1>{html.escape(title)}</h1><p>{html.escape(body)}</p>"


def copy_charts() -> None:
    charts_out = OUT / "charts"
    charts_out.mkdir(parents=True, exist_ok=True)
    for chart in CHARTS.glob("*.svg"):
        shutil.copy2(chart, charts_out / chart.name)


def write_page(filename: str, title: str, body: str) -> None:
    (OUT / filename).write_text(page_shell(body, title, filename))


def main() -> int:
    if not REPORT.exists():
        raise FileNotFoundError(REPORT)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    copy_charts()

    write_page("index.html", "PV Stock Insights", home_page())
    write_page(
        "atlas.html",
        "Market-Wide Pattern Atlas",
        markdown_to_html(ATLAS_OVERVIEW.read_text())
        if ATLAS_OVERVIEW.exists()
        else fallback_page(
            "Market-Wide Pattern Atlas",
            "Run make_pattern_atlas.py after fetching sample data to generate this page.",
        ),
    )
    write_page(
        "leaderboard.html",
        "Pattern Leaderboard",
        markdown_to_html(ATLAS_LEADERBOARD.read_text())
        if ATLAS_LEADERBOARD.exists()
        else fallback_page("Pattern Leaderboard", "No atlas leaderboard has been generated yet."),
    )
    write_page(
        "mag7.html",
        "MAG7 Patterns",
        markdown_to_html(ATLAS_MAG7.read_text())
        if ATLAS_MAG7.exists()
        else fallback_page("MAG7 Patterns", "No MAG7 atlas run has been generated yet."),
    )
    write_page(
        "top100.html",
        "Top 100 Patterns",
        markdown_to_html(ATLAS_TOP100.read_text())
        if ATLAS_TOP100.exists()
        else fallback_page("Top 100 Patterns", "No Top 100 atlas run has been generated yet."),
    )
    write_page(
        "report.html",
        "SPY Expanded Pattern Report",
        markdown_to_html(REPORT.read_text()),
    )
    if DEEP_DIVE.exists():
        write_page(
            "tuesday-1340.html",
            "SPY Tuesday 13:30-13:40 Deep Dive",
            markdown_to_html(DEEP_DIVE.read_text()),
        )
    write_page("charts.html", "Pattern Atlas Chart Library", charts_page())
    write_page("methodology.html", "Methodology and Notes", methodology_page())

    (OUT / "README.md").write_text(
        "# Share Site\n\n"
        "Static report package for Cloudflare Pages, Netlify, or any static host.\n\n"
        "Publish this folder as the site root. No API keys or raw CSV data are included.\n"
    )
    print(f"Wrote site to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
