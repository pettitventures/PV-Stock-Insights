# S&P 500 Intraday Trend Research

This workspace contains a small research pipeline for finding recurring minute-level calendar/time patterns in S&P 500 or SPY intraday bars.

Important: a full 12 months of 1-minute S&P 500 data usually requires a market-data vendor or an existing export. Free Yahoo-style sources generally expose only a short recent 1-minute window. Use this tool with a vendor CSV for the full research question.

## Input CSV

The analyzer accepts CSV files with at least:

- `timestamp` or `datetime`
- `close`

Optional columns: `open`, `high`, `low`, `volume`.

Timestamps should include timezone if possible. If they are timezone-naive, they are assumed to be America/New_York market time.

## Run

```bash
python3 sp500_intraday_trend_ai.py --csv path/to/minute-bars.csv --symbol SPY
```

Recommended first pass for pattern discovery:

```bash
python3 sp500_intraday_trend_ai.py --csv path/to/minute-bars.csv --symbol SPY --bar-minutes 10
```

For a quick recent-data smoke test using Yahoo's chart endpoint:

```bash
python3 fetch_yahoo_recent.py --symbol SPY --range 7d --interval 1m --out data/spy_recent_1m.csv
python3 sp500_intraday_trend_ai.py --csv data/spy_recent_1m.csv --symbol SPY --bar-minutes 10
```

For a 12-month Yahoo chunk attempt:

```bash
python3 fetch_yahoo_recent.py --symbol SPY --start 2025-06-03 --end 2026-06-03 --interval 5m --chunk-days 59 --out data/spy_12mo_5m_yahoo_chunks.csv
```

Yahoo rejected older sub-hour chunks in testing. The available free fallback was 12 months of 60-minute bars:

```bash
python3 fetch_yahoo_recent.py --symbol SPY --start 2025-06-03 --end 2026-06-03 --interval 60m --chunk-days 59 --out data/spy_12mo_60m_yahoo_chunks.csv
python3 sp500_intraday_trend_ai.py --csv data/spy_12mo_60m_yahoo_chunks.csv --symbol SPY --bar-minutes 60 --feature-mode all
```

## Alpaca

Alpaca is the preferred API path for the full 12-month 1-minute or 10-minute study.

Set credentials in your shell or in an ignored `.env.local` file, then fetch and analyze:

```bash
export ALPACA_API_KEY_ID="..."
export ALPACA_API_SECRET_KEY="..."
```

`.env.local` format:

```bash
ALPACA_API_KEY_ID=...
ALPACA_API_SECRET_KEY=...
```

Fetch and analyze:

```bash

python3 fetch_alpaca_bars.py \
  --symbol SPY \
  --start 2025-06-03 \
  --end 2026-06-03 \
  --timeframe 1Min \
  --feed sip \
  --adjustment all \
  --out data/spy_12mo_1m_alpaca.csv

python3 sp500_intraday_trend_ai.py \
  --csv data/spy_12mo_1m_alpaca.csv \
  --symbol SPY \
  --bar-minutes 10 \
  --feature-mode all \
  --top 50

python3 sp500_intraday_trend_ai.py \
  --csv data/spy_12mo_1m_alpaca.csv \
  --symbol SPY \
  --bar-minutes 10 \
  --feature-mode intraday \
  --top 50
```

Use `--feed iex` if your Alpaca plan does not include SIP historical data.

## Shareable Static Site

Build a colleague-friendly static HTML package:

```bash
python3 build_share_site.py
python3 verify_static_site.py
```

The publishable folder is `share/`. It includes the HTML report and chart SVGs only; it does not include `.env` files or raw CSV data.

Generated pages:

- `share/index.html`: overview / starting point
- `share/report.html`: expanded 2021-2026 pattern report
- `share/tuesday-1340.html`: focused deep dive on the Tuesday 13:30-13:40 pattern
- `share/charts.html`: chart library
- `share/methodology.html`: data and method notes

Cloudflare Pages setup:

- Connect the GitHub repository to Cloudflare Pages.
- Build command: `python3 build_share_site.py`
- Output directory: `share`.

This is intentionally a static-only project for now. See `STATIC_ONLY.md` for the data and deployment policy.

Outputs are written to `reports/`:

- Markdown research report
- Candidate pattern CSV
- Minute-of-day profile CSV

## What It Looks For

- Minute-of-day and 5/10/15/30/60-minute bucket behavior
- Day-of-week and calendar-day effects
- First/last trading day of week/month
- First Tuesday of the month and other nth-weekday effects
- Month, quarter, and turn-of-month effects
- Conjunctions such as `Tuesday + 10:00-10:29` or `first Tuesday + open hour`

The search uses a train/test split and reports out-of-sample results. That is intentional: intraday data has many possible calendar patterns, and naive scans produce false discoveries very easily.

This is for research only and is not investment advice.
