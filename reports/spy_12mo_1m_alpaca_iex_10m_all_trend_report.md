# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 101,069
- Return observations: 9,622
- Trading dates: 252
- Start: 2025-06-03T08:06:00-04:00
- End: 2026-06-03T16:23:00-04:00

## Baseline

- Return bar size: 10 minute(s)
- Feature mode: all
- Full sample: n=9,622, mean=0.0902 bps/bar, hit=50.9%, t=0.91, total=868.1 bps
- Train period: n=6,210, mean=0.0401 bps/bar, hit=51.2%, t=0.35, total=249.2 bps
- Test period: n=3,412, mean=0.1814 bps/bar, hit=50.3%, t=0.96, total=618.9 bps

## Best Out-of-Sample Candidate Rules

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `minute=13:30` | 1.1405 | 1.76 | 89 | 2.0825 | 57.3% | 2.41 | 1.9011 |
| 2 | `dow=Tue + midday=True` | 0.4964 | 1.54 | 342 | 1.1265 | 52.0% | 2.03 | 0.9451 |
| 3 | `first_trading_day_month=True + midday=True` | 0.9330 | 1.51 | 90 | 1.3431 | 54.4% | 1.68 | 1.1617 |
| 4 | `first_trading_day_week=True` | 0.3155 | 1.59 | 691 | 0.6022 | 49.6% | 1.42 | 0.4208 |
| 5 | `midday=True + weekday_instance=2_Mon` | 0.8249 | 1.62 | 72 | 1.1194 | 51.4% | 1.39 | 0.9380 |
| 6 | `dow=Mon` | 0.3225 | 1.59 | 615 | 0.6138 | 50.1% | 1.39 | 0.4324 |
| 7 | `minute=15:30` | -1.1355 | -2.28 | 89 | -1.1730 | 40.4% | -1.38 | -1.3544 |
| 8 | `first_trading_day_week=True + quarter=Q2` | 0.9996 | 1.85 | 348 | 0.6063 | 52.3% | 1.33 | 0.4249 |
| 9 | `dow=Mon + quarter=Q2` | 0.9516 | 1.53 | 310 | 0.6565 | 52.9% | 1.31 | 0.4751 |
| 10 | `dow=Tue + hour=12:00` | 0.9401 | 1.65 | 114 | 1.0879 | 50.9% | 1.13 | 0.9065 |
| 11 | `weekday_instance=4_Tue` | 0.6848 | 1.57 | 193 | 0.7565 | 50.3% | 1.08 | 0.5751 |
| 12 | `bucket_30m=10:00` | 0.9313 | 1.86 | 267 | 1.0134 | 54.7% | 1.05 | 0.8320 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
