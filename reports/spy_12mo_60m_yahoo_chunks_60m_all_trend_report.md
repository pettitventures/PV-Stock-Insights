# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 1,744
- Return observations: 1,488
- Trading dates: 251
- Start: 2025-06-03T09:30:00-04:00
- End: 2026-06-03T14:11:34-04:00

## Baseline

- Return bar size: 60 minute(s)
- Feature mode: all
- Full sample: n=1,488, mean=0.1549 bps/bar, hit=52.5%, t=0.28, total=230.5 bps
- Train period: n=966, mean=-0.4595 bps/bar, hit=52.6%, t=-0.70, total=-443.9 bps
- Test period: n=522, mean=1.2918 bps/bar, hit=52.3%, t=1.28, total=674.3 bps

## Best Out-of-Sample Candidate Rules

No candidate rule met the minimum sample-size and train/test stability filters.

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
