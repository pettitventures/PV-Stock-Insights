# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 2,595
- Return observations: 253
- Trading dates: 7
- Start: 2026-05-26T09:30:00-04:00
- End: 2026-06-03T13:44:41-04:00

## Baseline

- Return bar size: 10 minute(s)
- Full sample: n=253, mean=0.4469 bps/bar, hit=50.2%, t=1.08, total=113.1 bps
- Train period: n=152, mean=0.5182 bps/bar, hit=49.3%, t=0.96, total=78.8 bps
- Test period: n=101, mean=0.3396 bps/bar, hit=51.5%, t=0.53, total=34.3 bps

## Best Out-of-Sample Candidate Rules

No candidate rule met the minimum sample-size and train/test stability filters.

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
