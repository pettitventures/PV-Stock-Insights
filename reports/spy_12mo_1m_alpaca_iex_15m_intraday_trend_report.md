# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 101,069
- Return observations: 6,378
- Trading dates: 252
- Start: 2025-06-03T08:06:00-04:00
- End: 2026-06-03T16:23:00-04:00

## Baseline

- Return bar size: 15 minute(s)
- Feature mode: intraday
- Full sample: n=6,378, mean=0.1293 bps/bar, hit=51.0%, t=0.84, total=825.0 bps
- Train period: n=4,119, mean=0.0514 bps/bar, hit=51.1%, t=0.29, total=211.8 bps
- Test period: n=2,259, mean=0.2714 bps/bar, hit=50.9%, t=0.95, total=613.2 bps

## Best Out-of-Sample Candidate Rules

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `dow=Fri + hour=15:00` | -1.2247 | -1.90 | 68 | -1.6940 | 44.1% | -1.38 | -1.9654 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
