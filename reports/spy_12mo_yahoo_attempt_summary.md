# SPY 12-Month Yahoo Intraday Attempt

Research date: 2026-06-03

## Requested

- Symbol: SPY
- Target period: 2025-06-03 through 2026-06-03
- Preferred research horizon: 10-minute returns
- Chunking attempted: yes

## Data Availability Result

Yahoo accepted 12 months of 60-minute intraday chunks, but rejected older sub-hour chunks.

| Source interval | Output file | Result |
|---|---|---|
| 5m | `data/spy_12mo_5m_yahoo_chunks.csv` | Older chunks rejected; only 526 recent bars written |
| 30m | `data/spy_12mo_30m_yahoo_chunks.csv` | Older chunks rejected; only 89 recent bars written |
| 60m | `data/spy_12mo_60m_yahoo_chunks.csv` | Success; 1,744 bars written |

Because the 5m/30m requests were rejected outside the recent slice, this free Yahoo path cannot produce a true 12-month 10-minute SPY study. A vendor/exported CSV is required for that exact horizon.

## Completed 12-Month Fallback

The analyzer was run on the 12-month 60-minute dataset.

- Bars loaded: 1,744
- Return observations: 1,488
- Trading dates: 251
- Start: 2025-06-03 09:30 America/New_York
- End: 2026-06-03 14:11 America/New_York

Reports:

- `reports/spy_12mo_60m_yahoo_chunks_60m_all_trend_report.md`
- `reports/spy_12mo_60m_yahoo_chunks_60m_intraday_trend_report.md`

Result: no stable out-of-sample hourly calendar or intraday rule passed the current filters.

## Completed Recent 10-Minute Study

The best available sub-hour Yahoo dataset remains the recent 60-trading-date sample:

- Source file: `data/spy_recent_60d_5m.csv`
- Report: `reports/spy_recent_60d_5m_10m_all_trend_report.md`
- Intraday-only report: `reports/spy_recent_60d_5m_10m_intraday_trend_report.md`

Result: the broad scan found a Q2/week-of-month hypothesis, but the stricter intraday-only 10-minute scan found no stable recurring hour/day pattern.
