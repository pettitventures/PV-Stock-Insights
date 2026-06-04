# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 1,123,109
- Return observations: 52,993
- Trading dates: 1,360
- Start: 2021-01-04T04:00:00-05:00
- End: 2026-06-04T08:54:00-04:00

## Baseline

- Return bar size: 10 minute(s)
- Feature mode: all
- Full sample: n=52,993, mean=0.0534 bps/bar, hit=51.3%, t=0.95, total=2827.6 bps
- Train period: n=34,450, mean=0.0504 bps/bar, hit=51.2%, t=0.71, total=1736.8 bps
- Test period: n=18,543, mean=0.0588 bps/bar, hit=51.3%, t=0.63, total=1090.8 bps

## Best Out-of-Sample Candidate Rules

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `hour=14:00 + month=03` | 1.0512 | 1.81 | 258 | 2.1649 | 57.8% | 2.68 | 2.1060 |
| 2 | `bucket_5m=13:40 + dow=Tue` | 1.5254 | 1.84 | 99 | 3.0301 | 60.6% | 2.39 | 2.9713 |
| 3 | `day_of_month=03 + hour=15:00` | -1.8543 | -2.14 | 95 | -2.6631 | 43.2% | -2.31 | -2.7219 |
| 4 | `bucket_5m=14:20 + week_of_month=3` | -1.4209 | -1.64 | 109 | -1.8130 | 41.3% | -2.29 | -1.8718 |
| 5 | `bucket_15m=13:30` | 0.4085 | 1.53 | 952 | 0.8382 | 52.9% | 2.27 | 0.7794 |
| 6 | `day_of_month=18 + dow=Wed` | -4.1592 | -3.69 | 195 | -1.9752 | 42.1% | -1.82 | -2.0340 |
| 7 | `day_of_month=24` | 1.1969 | 2.68 | 651 | 0.6229 | 51.9% | 1.80 | 0.5641 |
| 8 | `day_of_month=18` | -0.7001 | -1.93 | 624 | -0.8762 | 48.1% | -1.79 | -0.9350 |
| 9 | `day_of_month=24 + midday=True` | 1.0917 | 1.93 | 306 | 0.7716 | 53.9% | 1.70 | 0.7128 |
| 10 | `bucket_5m=13:40 + turn_of_month=True` | 1.4146 | 2.31 | 138 | 1.2192 | 55.1% | 1.68 | 1.1604 |
| 11 | `bucket_5m=16:00 + week_of_month=2` | 2.2865 | 2.31 | 111 | 2.1408 | 53.2% | 1.64 | 2.0820 |
| 12 | `bucket_5m=16:00 + first_trading_day_week=True` | 2.5436 | 2.22 | 99 | 2.6407 | 56.6% | 1.64 | 2.5819 |
| 13 | `bucket_30m=14:30 + month=03` | 1.7886 | 2.04 | 129 | 1.7462 | 55.8% | 1.63 | 1.6873 |
| 14 | `bucket_30m=13:30 + quarter=Q4` | 0.7009 | 1.50 | 384 | 0.6923 | 55.5% | 1.62 | 0.6334 |
| 15 | `quarter=Q1 + weekday_instance=2_Thu` | -1.3405 | -2.08 | 195 | -1.3681 | 49.7% | -1.54 | -1.4269 |
| 16 | `bucket_30m=15:30 + week_of_month=2` | -0.8149 | -1.56 | 333 | -1.0424 | 46.8% | -1.51 | -1.1012 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
