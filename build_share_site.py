#!/usr/bin/env python3
"""Build a colleague-friendly static HTML share site from the visual report."""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path


REPORT = Path("reports/spy_12mo_1m_alpaca_sip_visual_report.md")
DEEP_DIVE = Path("reports/spy_1320_1330_deep_dive.md")
CHARTS = Path("reports/charts")
OUT = Path("share")


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
    html_lines = ["<div class=\"table-wrap\"><table>", "<thead><tr>"]
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
                f"<figure><img src=\"{html.escape(src)}\" alt=\"{html.escape(alt)}\" loading=\"lazy\"></figure>"
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


def page_shell(body: str, title: str = "SPY 12-Month Pattern Report") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="Plain-English SPY intraday pattern research report with charts.">
  <style>
    :root {{
      --bg: #f7f8fa;
      --paper: #ffffff;
      --ink: #172033;
      --muted: #667085;
      --line: #d9dee7;
      --accent: #14532d;
      --accent-soft: #e9f7ef;
      --warning: #8a4b00;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 18px 64px;
    }}
    article {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: clamp(22px, 4vw, 46px);
      box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
    }}
    h1 {{
      margin: 0 0 18px;
      font-size: clamp(32px, 5vw, 52px);
      line-height: 1.02;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 42px 0 14px;
      font-size: clamp(22px, 3vw, 31px);
      line-height: 1.16;
      letter-spacing: 0;
    }}
    h3 {{
      margin: 34px 0 10px;
      font-size: 20px;
      line-height: 1.25;
      letter-spacing: 0;
    }}
    p, li {{ font-size: 17px; }}
    p {{ margin: 12px 0; }}
    ul, ol {{ padding-left: 24px; }}
    strong {{ color: var(--accent); }}
    code {{
      background: #eef2f7;
      border: 1px solid #d8e0ea;
      border-radius: 4px;
      padding: 1px 5px;
      font-size: 0.92em;
    }}
    .table-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      margin: 18px 0 22px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 720px;
      font-size: 15px;
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #f2f5f9;
      font-weight: 700;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    figure {{
      margin: 18px 0 34px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcfe;
    }}
    img {{
      display: block;
      width: 100%;
      height: auto;
    }}
    .top-note {{
      margin: 0 0 22px;
      padding: 14px 16px;
      border: 1px solid #b7e2c5;
      border-radius: 8px;
      background: var(--accent-soft);
      color: #174d2b;
      font-size: 16px;
    }}
    .nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 0 0 18px;
    }}
    .nav a {{
      display: inline-flex;
      align-items: center;
      min-height: 36px;
      padding: 7px 11px;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--ink);
      text-decoration: none;
      font-size: 14px;
      font-weight: 650;
      background: #fff;
    }}
    .nav a:hover {{ border-color: #8bbf9a; color: var(--accent); }}
    article p a {{
      color: var(--accent);
      font-weight: 650;
    }}
    .footer-note {{
      margin-top: 42px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 14px;
    }}
    @media (max-width: 760px) {{
      article {{ padding: 22px 16px; }}
      p, li {{ font-size: 16px; }}
      table {{ min-width: 640px; }}
    }}
  </style>
</head>
<body>
  <main>
    <article>
      <nav class="nav" aria-label="Report navigation">
        <a href="index.html">Main report</a>
        <a href="1320-1330.html">13:20-13:30 deep dive</a>
      </nav>
      <div class="top-note">Prepared as a plain-English research summary. This is not investment advice.</div>
      {body}
      <div class="footer-note">Generated from local Alpaca SIP data and static SVG charts. Raw API keys and raw CSV data are not included in this share package.</div>
    </article>
  </main>
</body>
</html>
"""


def main() -> int:
    if not REPORT.exists():
        raise FileNotFoundError(REPORT)
    OUT.mkdir(parents=True, exist_ok=True)
    charts_out = OUT / "charts"
    charts_out.mkdir(parents=True, exist_ok=True)

    for chart in CHARTS.glob("*.svg"):
        shutil.copy2(chart, charts_out / chart.name)

    body = markdown_to_html(REPORT.read_text())
    (OUT / "index.html").write_text(page_shell(body))
    if DEEP_DIVE.exists():
        deep_dive_body = markdown_to_html(DEEP_DIVE.read_text())
        (OUT / "1320-1330.html").write_text(
            page_shell(deep_dive_body, "SPY 13:20-13:30 Deep Dive")
        )
    (OUT / "README.md").write_text(
        "# Share Site\n\n"
        "Static report package for Cloudflare Pages, Netlify, or any static host.\n\n"
        "Publish this folder as the site root. No API keys or raw CSV data are included.\n"
    )
    print(f"Wrote {OUT / 'index.html'}")
    print(f"Copied charts to {charts_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
