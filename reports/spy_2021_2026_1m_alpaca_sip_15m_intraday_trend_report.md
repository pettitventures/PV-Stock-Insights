# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 1,123,109
- Return observations: 35,329
- Trading dates: 1,360
- Start: 2021-01-04T04:00:00-05:00
- End: 2026-06-04T08:54:00-04:00

## Baseline

- Return bar size: 15 minute(s)
- Feature mode: intraday
- Full sample: n=35,329, mean=0.0799 bps/bar, hit=51.4%, t=0.92, total=2824.3 bps
- Train period: n=22,964, mean=0.0755 bps/bar, hit=51.7%, t=0.71, total=1734.2 bps
- Test period: n=12,365, mean=0.0882 bps/bar, hit=50.7%, t=0.59, total=1090.1 bps

## Best Out-of-Sample Candidate Rules

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `bucket_5m=16:00 + dow=Mon` | 3.1483 | 2.01 | 91 | 3.5372 | 58.2% | 1.83 | 3.4490 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
