# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 1,123,109
- Return observations: 105,992
- Trading dates: 1,360
- Start: 2021-01-04T04:00:00-05:00
- End: 2026-06-04T08:54:00-04:00

## Baseline

- Return bar size: 5 minute(s)
- Feature mode: intraday
- Full sample: n=105,992, mean=0.0266 bps/bar, hit=50.7%, t=0.93, total=2822.6 bps
- Train period: n=68,898, mean=0.0252 bps/bar, hit=50.7%, t=0.70, total=1736.8 bps
- Test period: n=37,094, mean=0.0293 bps/bar, hit=50.8%, t=0.61, total=1085.8 bps

## Best Out-of-Sample Candidate Rules

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `bucket_5m=10:10 + dow=Thu` | -1.2273 | -1.56 | 93 | -2.6269 | 43.0% | -2.70 | -2.6562 |
| 2 | `bucket_10m=10:50 + dow=Wed` | -0.8621 | -1.99 | 194 | -1.3023 | 49.0% | -2.15 | -1.3316 |
| 3 | `bucket_5m=13:40 + dow=Tue` | 0.9853 | 1.74 | 99 | 1.6811 | 48.5% | 2.05 | 1.6518 |
| 4 | `bucket_5m=11:00 + dow=Wed` | 1.5598 | 2.97 | 97 | 1.3340 | 56.7% | 1.80 | 1.3047 |
| 5 | `bucket_5m=15:55 + dow=Thu` | -2.1502 | -2.41 | 93 | -1.7299 | 49.5% | -1.74 | -1.7591 |
| 6 | `bucket_5m=10:15 + dow=Thu` | 3.3454 | 3.89 | 93 | 1.8557 | 60.2% | 1.71 | 1.8264 |
| 7 | `bucket_5m=10:20 + dow=Wed` | 1.7501 | 2.29 | 97 | 1.3105 | 53.6% | 1.65 | 1.2813 |
| 8 | `bucket_10m=10:20 + dow=Wed` | 1.0717 | 1.92 | 194 | 0.9503 | 52.1% | 1.65 | 0.9210 |
| 9 | `bucket_5m=13:10 + dow=Mon` | 1.3405 | 2.10 | 91 | 0.9450 | 52.7% | 1.63 | 0.9157 |
| 10 | `bucket_10m=14:30 + dow=Mon` | 0.6045 | 1.59 | 182 | 0.6657 | 55.5% | 1.55 | 0.6364 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
