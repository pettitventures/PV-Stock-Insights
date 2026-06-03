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
- Feature mode: intraday
- Full sample: n=9,819, mean=0.0804 bps/bar, hit=51.0%, t=0.82, total=789.5 bps
- Train period: n=6,348, mean=0.0269 bps/bar, hit=51.1%, t=0.24, total=170.6 bps
- Test period: n=3,471, mean=0.1783 bps/bar, hit=50.7%, t=0.95, total=618.8 bps

## Best Out-of-Sample Candidate Rules

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `minute=13:30` | 1.1018 | 1.76 | 89 | 2.0625 | 59.6% | 2.38 | 1.8842 |
| 2 | `dow=Tue + midday=True` | 0.4980 | 1.55 | 342 | 1.1485 | 52.9% | 2.09 | 0.9702 |
| 3 | `dow=Mon` | 0.3195 | 1.58 | 624 | 0.5824 | 51.0% | 1.32 | 0.4041 |
| 4 | `minute=15:30` | -1.0886 | -2.22 | 89 | -1.0944 | 40.4% | -1.30 | -1.2727 |
| 5 | `dow=Tue + hour=12:00` | 0.9415 | 1.67 | 114 | 1.1234 | 52.6% | 1.19 | 0.9451 |
| 6 | `bucket_30m=10:00` | 0.9238 | 1.85 | 267 | 0.9937 | 54.7% | 1.03 | 0.8155 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
