# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 221,441
- Return observations: 3,275
- Trading dates: 252
- Start: 2025-06-03T04:00:00-04:00
- End: 2026-06-03T16:32:00-04:00

## Baseline

- Return bar size: 30 minute(s)
- Feature mode: intraday
- Full sample: n=3,275, mean=0.2403 bps/bar, hit=52.7%, t=0.81, total=787.0 bps
- Train period: n=2,118, mean=0.0794 bps/bar, hit=52.7%, t=0.23, total=168.2 bps
- Test period: n=1,157, mean=0.5348 bps/bar, hit=52.6%, t=0.97, total=618.8 bps

## Best Out-of-Sample Candidate Rules

No candidate rule met the minimum sample-size and train/test stability filters.

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
