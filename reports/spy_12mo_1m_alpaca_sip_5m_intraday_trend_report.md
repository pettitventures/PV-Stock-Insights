# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 221,441
- Return observations: 19,644
- Trading dates: 252
- Start: 2025-06-03T04:00:00-04:00
- End: 2026-06-03T16:32:00-04:00

## Baseline

- Return bar size: 5 minute(s)
- Feature mode: intraday
- Full sample: n=19,644, mean=0.0401 bps/bar, hit=50.5%, t=0.80, total=787.7 bps
- Train period: n=12,702, mean=0.0133 bps/bar, hit=50.8%, t=0.23, total=168.9 bps
- Test period: n=6,942, mean=0.0891 bps/bar, hit=49.8%, t=0.93, total=618.8 bps

## Best Out-of-Sample Candidate Rules

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `minute=15:25` | -0.5155 | -1.52 | 89 | -1.2556 | 40.4% | -1.83 | -1.3447 |
| 2 | `minute=13:30` | 0.6681 | 1.64 | 89 | 0.8834 | 60.7% | 1.71 | 0.7942 |
| 3 | `minute=10:50` | -1.6352 | -3.04 | 89 | -1.3328 | 38.2% | -1.53 | -1.4220 |
| 4 | `dow=Mon` | 0.1598 | 1.55 | 1,248 | 0.2912 | 49.9% | 1.32 | 0.2021 |
| 5 | `bucket_30m=12:00 + dow=Tue` | 0.5837 | 1.60 | 114 | 0.7930 | 54.4% | 1.30 | 0.7038 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
