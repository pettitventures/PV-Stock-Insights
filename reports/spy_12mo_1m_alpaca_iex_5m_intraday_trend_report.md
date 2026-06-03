# SPY Intraday Trend Research

This report is exploratory research only and is not investment advice.

## Data Coverage

- Bars loaded: 101,069
- Return observations: 19,382
- Trading dates: 252
- Start: 2025-06-03T08:06:00-04:00
- End: 2026-06-03T16:23:00-04:00

## Baseline

- Return bar size: 5 minute(s)
- Feature mode: intraday
- Full sample: n=19,382, mean=0.0393 bps/bar, hit=50.6%, t=0.78, total=761.8 bps
- Train period: n=12,502, mean=0.0075 bps/bar, hit=50.8%, t=0.13, total=93.6 bps
- Test period: n=6,880, mean=0.0971 bps/bar, hit=50.1%, t=1.02, total=668.2 bps

## Best Out-of-Sample Candidate Rules

| Rank | Rule | Train mean | Train t | Test n | Test mean | Test hit | Test t | Lift vs baseline |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `minute=13:30` | 0.6743 | 1.58 | 89 | 0.8363 | 60.7% | 1.59 | 0.7392 |
| 2 | `dow=Mon` | 0.1681 | 1.63 | 1,239 | 0.3038 | 50.6% | 1.38 | 0.2067 |
| 3 | `minute=10:50` | -1.6906 | -3.14 | 89 | -1.1341 | 44.9% | -1.31 | -1.2312 |
| 4 | `bucket_30m=12:00 + dow=Tue` | 0.6125 | 1.70 | 114 | 0.7934 | 53.5% | 1.27 | 0.6963 |
| 5 | `minute=12:10` | -0.6628 | -1.58 | 89 | -0.8611 | 50.6% | -1.07 | -0.9582 |
| 6 | `bucket_30m=09:30 + dow=Mon` | 1.4398 | 2.16 | 80 | 1.4872 | 51.2% | 1.07 | 1.3901 |

## Interpretation Notes

- Treat positive findings as hypotheses until tested on a separate period or instrument.
- Minute-level scans create many chances for false positives; the train/test split is a guardrail, not proof.
- Reported returns are non-overlapping close-to-close log returns in basis points and exclude fees, spread, slippage, and execution constraints.
- For index symbols such as `^GSPC`, tradability differs from ETF/futures instruments such as SPY or ES.
