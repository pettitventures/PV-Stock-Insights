# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 4,658
- Return observations: 2,269
- Trading dates: 60
- Start: 2026-03-10T09:30:00-04:00
- End: 2026-06-03T14:01:31-04:00

## Baseline

- Return bar size: 10 minute(s)
- Full sample: n=2,269, mean=0.1671 bps/bar, hit=52.9%, t=0.80, total=379.2 bps
- Train period: n=1,482, mean=-0.0062 bps/bar, hit=51.8%, t=-0.02, total=-9.3 bps
- Test period: n=787, mean=0.4935 bps/bar, hit=55.1%, t=1.73, total=388.4 bps

## Best Out-of-Sample Candidate Rules

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `quarter=Q2 + week_of_month=2` | 1.2506 | 2.28 | 190 | 0.9461 | 61.1% | 2.04 | 0.4525 |
| 2 | `hour=10:00 + quarter=Q2` | 1.9189 | 2.22 | 126 | 0.9452 | 61.1% | 1.06 | 0.4517 |
| 3 | `dow=Thu + quarter=Q2` | 1.5358 | 1.91 | 152 | 0.7439 | 54.6% | 1.01 | 0.2503 |
| 4 | `hour=15:00 + quarter=Q2` | 1.6121 | 2.23 | 120 | 0.5955 | 54.2% | 0.84 | 0.1020 |
| 5 | `dow=Fri` | -1.0111 | -1.72 | 152 | -0.0224 | 54.6% | -0.04 | -0.5159 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
