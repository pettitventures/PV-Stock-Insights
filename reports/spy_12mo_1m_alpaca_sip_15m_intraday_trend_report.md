# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 221,441
- Return observations: 6,550
- Trading dates: 252
- Start: 2025-06-03T04:00:00-04:00
- End: 2026-06-03T16:32:00-04:00

## Baseline

- Return bar size: 15 minute(s)
- Feature mode: intraday
- Full sample: n=6,550, mean=0.1207 bps/bar, hit=51.2%, t=0.80, total=790.4 bps
- Train period: n=4,236, mean=0.0405 bps/bar, hit=51.3%, t=0.23, total=171.6 bps
- Test period: n=2,314, mean=0.2674 bps/bar, hit=51.1%, t=0.94, total=618.8 bps

## Best Out-of-Sample Candidate Rules

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `dow=Fri + hour=15:00` | -1.2275 | -1.97 | 68 | -1.6913 | 45.6% | -1.37 | -1.9587 |
| 2 | `dow=Mon` | 0.4793 | 1.56 | 416 | 0.8736 | 50.7% | 1.24 | 0.6062 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
