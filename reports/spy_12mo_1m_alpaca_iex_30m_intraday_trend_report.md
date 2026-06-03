# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 101,069
- Return observations: 3,124
- Trading dates: 252
- Start: 2025-06-03T08:06:00-04:00
- End: 2026-06-03T16:23:00-04:00

## Baseline

- Return bar size: 30 minute(s)
- Feature mode: intraday
- Full sample: n=3,124, mean=0.2328 bps/bar, hit=52.6%, t=0.76, total=727.3 bps
- Train period: n=2,022, mean=0.0727 bps/bar, hit=52.9%, t=0.20, total=147.0 bps
- Test period: n=1,102, mean=0.5265 bps/bar, hit=52.0%, t=0.93, total=580.3 bps

## Best Out-of-Sample Candidate Rules

No candidate rule met the minimum sample-size and train/test stability filters.

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
