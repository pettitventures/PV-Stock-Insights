# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 221,441
- Return observations: 9,819
- Trading dates: 252
- Start: 2025-06-03T04:00:00-04:00
- End: 2026-06-03T16:32:00-04:00

## Baseline

- Return bar size: 10 minute(s)
- Feature mode: all
- Full sample: n=9,819, mean=0.0804 bps/bar, hit=51.0%, t=0.82, total=789.5 bps
- Train period: n=6,348, mean=0.0269 bps/bar, hit=51.1%, t=0.24, total=170.6 bps
- Test period: n=3,471, mean=0.1783 bps/bar, hit=50.7%, t=0.95, total=618.8 bps

## Best Out-of-Sample Candidate Rules

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `minute=13:30` | 1.1018 | 1.76 | 89 | 2.0625 | 59.6% | 2.38 | 1.8842 |
| 2 | `day_of_month=14` | 1.2295 | 1.57 | 78 | 1.8318 | 61.5% | 2.38 | 1.6535 |
| 3 | `dow=Tue + midday=True` | 0.4980 | 1.55 | 342 | 1.1485 | 52.9% | 2.09 | 0.9702 |
| 4 | `first_trading_day_month=True + midday=True` | 0.9491 | 1.55 | 90 | 1.3381 | 54.4% | 1.69 | 1.1598 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
