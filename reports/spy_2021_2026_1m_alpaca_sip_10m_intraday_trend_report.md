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
- Feature mode: intraday
- Full sample: n=52,993, mean=0.0534 bps/bar, hit=51.3%, t=0.95, total=2827.6 bps
- Train period: n=34,450, mean=0.0504 bps/bar, hit=51.2%, t=0.71, total=1736.8 bps
- Test period: n=18,543, mean=0.0588 bps/bar, hit=51.3%, t=0.63, total=1090.8 bps

## Best Out-of-Sample Candidate Rules

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `bucket_5m=13:40 + dow=Tue` | 1.5254 | 1.84 | 99 | 3.0301 | 60.6% | 2.39 | 2.9713 |
| 2 | `bucket_15m=13:30` | 0.4085 | 1.53 | 952 | 0.8382 | 52.9% | 2.27 | 0.7794 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
