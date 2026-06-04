#!/usr/bin/env python3
"""Build a colleague-friendly static website from the SPY research reports."""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path


REPORT = Path("reports/spy_2021_2026_expanded_pattern_report.md")
DEEP_DIVE = Path("reports/spy_2021_2026_1340_tuesday_deep_dive.md")
CHARTS = Path("reports/charts")
OUT = Path("share")

NAV_LINKS = [
    ("index.html", "Overview"),
    ("report.html", "Expanded Report"),
    ("tuesday-1340.html", "Tuesday Deep Dive"),
    ("charts.html", "Charts"),
    ("methodology.html", "Methodology"),
]

CHART_LIBRARY = [
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
      --bg: #f6f7f9;
      --paper: #ffffff;
      --ink: #172033;
      --muted: #667085;
      --line: #d9dee7;
      --accent: #14532d;
      --accent-2: #1d4ed8;
      --accent-soft: #e9f7ef;
      --danger: #9f2d20;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }
    a { color: var(--accent); font-weight: 650; }
    .site-header {
      background: var(--paper);
      border-bottom: 1px solid var(--line);
      position: sticky;
      top: 0;
      z-index: 2;
    }
    .header-inner {
      max-width: 1180px;
      margin: 0 auto;
      padding: 14px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
    }
    .brand {
      text-decoration: none;
      color: var(--ink);
      font-size: 17px;
      font-weight: 800;
      letter-spacing: 0;
      white-space: nowrap;
    }
    .nav {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }
    .nav a {
      display: inline-flex;
      align-items: center;
      min-height: 34px;
      padding: 6px 10px;
      border: 1px solid transparent;
      border-radius: 8px;
      color: var(--ink);
      text-decoration: none;
      font-size: 14px;
      font-weight: 700;
    }
    .nav a:hover, .nav a.active {
      border-color: #b9d8c2;
      color: var(--accent);
      background: var(--accent-soft);
    }
    main {
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 18px 64px;
    }
    .page {
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: clamp(22px, 4vw, 46px);
      box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
    }
    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(300px, 0.85fr);
      gap: 24px;
      align-items: start;
      margin-bottom: 26px;
    }
    .kicker {
      margin: 0 0 10px;
      color: var(--accent);
      font-size: 14px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    h1 {
      margin: 0 0 18px;
      font-size: clamp(32px, 5vw, 52px);
      line-height: 1.02;
      letter-spacing: 0;
    }
    h2 {
      margin: 42px 0 14px;
      font-size: clamp(22px, 3vw, 31px);
      line-height: 1.16;
      letter-spacing: 0;
    }
    h3 {
      margin: 34px 0 10px;
      font-size: 20px;
      line-height: 1.25;
      letter-spacing: 0;
    }
    p, li { font-size: 17px; }
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
    .note {
      margin: 0 0 22px;
      padding: 14px 16px;
      border: 1px solid #b7e2c5;
      border-radius: 8px;
      background: var(--accent-soft);
      color: #174d2b;
      font-size: 16px;
    }
    .metric-grid, .link-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 20px 0 26px;
    }
    .metric, .link-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfe;
      padding: 16px;
    }
    .metric .label {
      color: var(--muted);
      font-size: 13px;
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
    .link-card {
      display: block;
      color: var(--ink);
      text-decoration: none;
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
    .link-card:hover { border-color: #9ac9a8; }
    .table-wrap {
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      margin: 18px 0 22px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 720px;
      font-size: 15px;
    }
    th, td {
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }
    th {
      background: #f2f5f9;
      font-weight: 700;
    }
    tr:last-child td { border-bottom: 0; }
    figure {
      margin: 18px 0 34px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfe;
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
      gap: 22px;
    }
    .chart-item {
      border-top: 1px solid var(--line);
      padding-top: 22px;
    }
    .footer-note {
      margin-top: 42px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 14px;
    }
    @media (max-width: 920px) {
      .hero, .metric-grid, .link-grid { grid-template-columns: 1fr 1fr; }
      .header-inner { align-items: flex-start; flex-direction: column; }
      .nav { justify-content: flex-start; }
    }
    @media (max-width: 640px) {
      main { padding: 18px 12px 42px; }
      .page { padding: 20px 14px; }
      .hero, .metric-grid, .link-grid { grid-template-columns: 1fr; }
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


def page_shell(body: str, title: str, active: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="Plain-English SPY intraday pattern research report with charts.">
  <style>{css()}</style>
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="index.html">PV Stock Insights</a>
      <nav class="nav" aria-label="Site navigation">
        {nav_html(active)}
      </nav>
    </div>
  </header>
  <main>
    <section class="page">
      <div class="note">Prepared as a plain-English research summary. This is not investment advice.</div>
      {body}
      <div class="footer-note">Generated from local Alpaca SIP data and static SVG charts. Raw API keys and raw CSV data are not included in this share package.</div>
    </section>
  </main>
</body>
</html>
"""


def home_page() -> str:
    return """
<div class="hero">
  <div>
    <p class="kicker">SPY expanded timing research</p>
    <h1>A plain-English map of the strongest intraday pattern since 2021.</h1>
    <p>The research now reviews consolidated SPY minute data from 2021 through 2026. The broader 13:30 area still matters, but the strongest simple lead became Tuesday 13:30-13:40.</p>
  </div>
  <figure>
    <img src="charts/spy_2021_2026_tue_1340_yearly.svg" alt="Tuesday 13:30 to 13:40 yearly chart">
  </figure>
</div>

<div class="metric-grid">
  <div class="metric">
    <div class="label">Best window</div>
    <div class="value">Tue 13:30-13:40</div>
    <div class="detail">New York time</div>
  </div>
  <div class="metric">
    <div class="label">Win rate</div>
    <div class="value">60.6%</div>
    <div class="detail">282 Tuesdays tested</div>
  </div>
  <div class="metric">
    <div class="label">Average move</div>
    <div class="value">+2.05 bps</div>
    <div class="detail">Before spread and slippage</div>
  </div>
  <div class="metric">
    <div class="label">Yearly read</div>
    <div class="value">6 / 6</div>
    <div class="detail">Positive years represented</div>
  </div>
</div>

<h2>Start Here</h2>
<div class="link-grid">
  <a class="link-card" href="tuesday-1340.html">
    <strong>Tuesday Deep Dive</strong>
    <span>The focused business case for the refined Tuesday 13:30-13:40 pattern.</span>
  </a>
  <a class="link-card" href="report.html">
    <strong>Expanded Report</strong>
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

<h2>Bottom Line</h2>
<p>If we were going to study one time-based SPY pattern further after expanding the history, it should be the <strong>Tuesday 13:30-13:40 long window</strong>.</p>
<p>The old 13:20-13:30 daily idea is not dead; it became a weaker part of a broader 13:30-area pattern. The refined Tuesday version is the cleaner multi-year lead.</p>
"""


def charts_page() -> str:
    items = []
    for title, src, description in CHART_LIBRARY:
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

<h2>What We Studied</h2>
<p>The expanded analysis used SPY 1-minute bars from Alpaca SIP, covering 2021-01-04 through 2026-06-03 for regular-session observations. SIP is the consolidated feed, so it is the better source compared with the earlier IEX-only test pass.</p>

<h2>How The Pattern Search Worked</h2>
<p>The scripts converted 1-minute bars into clean 5-minute, 10-minute, 15-minute, and 30-minute windows. The main report focuses on 10-minute windows because they are less noisy than individual minutes but still specific enough to reveal time-of-day behavior.</p>

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
<p>Paper-track two rules side by side: the original daily 13:20-13:30 window and the refined Tuesday 13:30-13:40 window. Record gross result, estimated spread/slippage, and whether the day had a major market event.</p>
"""


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
    OUT.mkdir(parents=True, exist_ok=True)
    copy_charts()

    write_page("index.html", "PV Stock Insights", home_page())
    write_page(
        "report.html",
        "SPY 12-Month Pattern Report",
        markdown_to_html(REPORT.read_text()),
    )
    if DEEP_DIVE.exists():
        write_page(
            "tuesday-1340.html",
            "SPY Tuesday 13:30-13:40 Deep Dive",
            markdown_to_html(DEEP_DIVE.read_text()),
        )
    write_page("charts.html", "SPY Pattern Chart Library", charts_page())
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
