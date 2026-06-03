# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 2,595
- Return observations: 2,588
- Trading dates: 7
- Start: 2026-05-26T09:30:00-04:00
- End: 2026-06-03T13:44:41-04:00

## Baseline

- Return bar size: 1 minute(s)
- Full sample: n=2,588, mean=0.0410 bps/bar, hit=50.2%, t=0.96, total=106.2 bps
- Train period: n=1,556, mean=0.0444 bps/bar, hit=50.7%, t=0.77, total=69.1 bps
- Test period: n=1,032, mean=0.0359 bps/bar, hit=49.3%, t=0.59, total=37.0 bps

## Best Out-of-Sample Candidate Rules

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `bucket_5m=13:55` | -0.5635 | -1.83 | 10 | -0.8032 | 10.0% | -3.06 | -0.8391 |
| 2 | `bucket_5m=15:20` | 0.3341 | 1.55 | 10 | 0.4736 | 70.0% | 2.43 | 0.4377 |
| 3 | `bucket_10m=13:00` | -0.5566 | -1.73 | 30 | -0.5062 | 33.3% | -2.03 | -0.5421 |
| 4 | `bucket_10m=15:00` | 0.4512 | 2.14 | 20 | 0.2930 | 65.0% | 1.55 | 0.2572 |
| 5 | `bucket_10m=14:00` | 0.3784 | 1.84 | 20 | 0.2404 | 55.0% | 1.45 | 0.2046 |
| 6 | `bucket_10m=11:40` | -0.6435 | -2.26 | 30 | -0.3083 | 36.7% | -1.35 | -0.3441 |
| 7 | `bucket_5m=11:40` | -1.0141 | -2.25 | 15 | -0.3039 | 46.7% | -1.22 | -0.3397 |
| 8 | `bucket_30m=15:00` | 0.2263 | 2.05 | 60 | 0.0988 | 53.3% | 0.99 | 0.0629 |
| 9 | `bucket_10m=15:20` | 0.2990 | 1.77 | 20 | 0.1514 | 55.0% | 0.97 | 0.1155 |
| 10 | `dow=Tue + hour=15:00` | 0.3045 | 1.66 | 60 | 0.0944 | 55.0% | 0.94 | 0.0585 |
| 11 | `bucket_15m=14:15` | 0.3325 | 2.17 | 30 | 0.1434 | 53.3% | 0.93 | 0.1076 |
| 12 | `bucket_5m=14:15` | 0.5769 | 1.96 | 10 | 0.3158 | 60.0% | 0.82 | 0.2800 |
| 13 | `bucket_30m=14:00` | 0.2986 | 2.63 | 60 | 0.0772 | 48.3% | 0.73 | 0.0414 |
| 14 | `bucket_5m=13:45` | 0.5123 | 1.82 | 10 | 0.3687 | 40.0% | 0.67 | 0.3328 |
| 15 | `bucket_5m=14:20` | 0.4310 | 1.72 | 10 | 0.1185 | 60.0% | 0.63 | 0.0826 |
| 16 | `bucket_5m=13:05` | -0.9230 | -1.92 | 15 | -0.2280 | 40.0% | -0.57 | -0.2639 |
| 17 | `bucket_15m=14:00` | 0.2647 | 1.57 | 30 | 0.0110 | 43.3% | 0.08 | -0.0248 |
| 18 | `dow=Tue + hour=11:00` | -0.5488 | -1.85 | 60 | -0.0066 | 50.0% | -0.04 | -0.0424 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
