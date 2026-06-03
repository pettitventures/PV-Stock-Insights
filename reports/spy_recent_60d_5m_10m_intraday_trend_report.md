# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 4,658
- Return observations: 2,269
- Trading dates: 60
- Start: 2026-03-10T09:30:00-04:00
- End: 2026-06-03T14:01:31-04:00

## Baseline

- Return bar size: 10 minute(s)
- Feature mode: intraday
- Full sample: n=2,269, mean=0.1671 bps/bar, hit=52.9%, t=0.80, total=379.2 bps
- Train period: n=1,482, mean=-0.0062 bps/bar, hit=51.8%, t=-0.02, total=-9.3 bps
- Test period: n=787, mean=0.4935 bps/bar, hit=55.1%, t=1.73, total=388.4 bps

## Best Out-of-Sample Candidate Rules

No candidate rule met the minimum sample-size and train/test stability filters.

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
