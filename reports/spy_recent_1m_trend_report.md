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

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `minute=15:10` | 6.2097 | 3.13 | 2 | 2.8971 | 100.0% | 21.97 | 2.5575 |
| 2 | `minute=14:10` | 4.8222 | 2.49 | 2 | 2.3711 | 100.0% | 3.59 | 2.0315 |
| 3 | `minute=13:10` | -5.6470 | -1.71 | 3 | -4.4457 | 0.0% | -2.21 | -4.7853 |
| 4 | `minute=14:00` | -4.1430 | -1.99 | 2 | -3.0955 | 0.0% | -2.04 | -3.4351 |
| 5 | `dow=Tue + hour=10:00` | 3.3838 | 1.72 | 6 | 3.7246 | 66.7% | 1.49 | 3.3850 |
| 6 | `dow=Tue + hour=15:00` | 2.9116 | 1.88 | 6 | 0.8342 | 66.7% | 1.46 | 0.4946 |
| 7 | `minute=14:40` | -2.7597 | -1.86 | 2 | -2.3056 | 0.0% | -1.21 | -2.6452 |
| 8 | `bucket_30m=11:30 + dow=Tue` | -4.6025 | -3.19 | 3 | -2.3465 | 33.3% | -1.16 | -2.6861 |
| 9 | `bucket_30m=10:00 + dow=Tue` | 6.0803 | 3.66 | 3 | 3.0564 | 66.7% | 1.15 | 2.7168 |
| 10 | `bucket_30m=10:00` | 4.7982 | 1.56 | 9 | 1.8423 | 66.7% | 0.70 | 1.5026 |
| 11 | `bucket_30m=13:00 + last_trading_day_week=True` | -2.0262 | -6.99 | 3 | -2.0323 | 33.3% | -0.67 | -2.3719 |
| 12 | `minute=14:30` | 4.2993 | 2.79 | 2 | 0.8571 | 50.0% | 0.62 | 0.5175 |
| 13 | `bucket_30m=10:30 + last_trading_day_week=True` | -7.6714 | -2.72 | 3 | -2.9097 | 33.3% | -0.59 | -3.2493 |
| 14 | `minute=11:50` | -5.3460 | -2.53 | 3 | -0.6573 | 33.3% | -0.29 | -0.9969 |
| 15 | `bucket_30m=15:30 + dow=Tue` | 4.5334 | 4.94 | 3 | 0.1538 | 66.7% | 0.28 | -0.1858 |
| 16 | `dow=Tue + midday=True` | -2.0134 | -1.63 | 18 | -0.0439 | 50.0% | -0.05 | -0.3835 |
| 17 | `bucket_30m=12:30 + dow=Wed` | 4.9778 | 1.98 | 3 | 0.1321 | 33.3% | 0.03 | -0.2075 |
| 18 | `minute=10:50` | -4.7843 | -2.03 | 3 | -0.0127 | 66.7% | -0.00 | -0.3523 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
