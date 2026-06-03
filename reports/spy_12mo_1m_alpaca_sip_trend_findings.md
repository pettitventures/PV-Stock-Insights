# SPY 12-Month SIP Trend Findings

Data source: Alpaca SIP 1-minute bars, 2025-06-03 through 2026-06-03.
This is exploratory research only and is not investment advice.

## Strongest Intraday Long

- Rule: `minute=13:30`
- Horizon: 10 minute(s)
- Window: The 13:20-13:30 close-to-close window.
- Full sample: n=252, mean=1.4411 bps/bar, hit=59.1%, t=2.84, total=363.2 bps
- Train: n=163, mean=1.1018 bps/bar, hit=58.9%, t=1.76, total=179.6 bps
- Test: n=89, mean=2.0625 bps/bar, hit=59.6%, t=2.38, total=183.6 bps
- Monthly direction: 12 positive, 1 negative

| Month | n | Mean bps | Hit Rate |
|---|---:|---:|---:|
| 2025-06 | 19 | -0.1327 | 47.4% |
| 2025-07 | 22 | 0.1034 | 59.1% |
| 2025-08 | 21 | 2.9028 | 76.2% |
| 2025-09 | 21 | 0.0684 | 52.4% |
| 2025-10 | 23 | 1.8546 | 56.5% |
| 2025-11 | 19 | 1.8557 | 52.6% |
| 2025-12 | 22 | 0.5832 | 63.6% |
| 2026-01 | 20 | 2.0642 | 60.0% |
| 2026-02 | 19 | 1.6137 | 57.9% |
| 2026-03 | 22 | 0.9919 | 54.5% |
| 2026-04 | 21 | 2.0740 | 57.1% |
| 2026-05 | 20 | 3.3368 | 75.0% |
| 2026-06 | 3 | 2.0675 | 33.3% |

## Tuesday Midday Long

- Rule: `dow=Tue + midday=True`
- Horizon: 10 minute(s)
- Window: Any 10-minute bar from 11:00 through 13:59 on Tuesdays.
- Full sample: n=954, mean=0.7312 bps/bar, hit=53.4%, t=2.56, total=697.5 bps
- Train: n=612, mean=0.4980 bps/bar, hit=53.6%, t=1.55, total=304.8 bps
- Test: n=342, mean=1.1485 bps/bar, hit=52.9%, t=2.09, total=392.8 bps
- Monthly direction: 8 positive, 5 negative

| Month | n | Mean bps | Hit Rate |
|---|---:|---:|---:|
| 2025-06 | 72 | 0.3582 | 61.1% |
| 2025-07 | 90 | -0.0661 | 45.6% |
| 2025-08 | 72 | 0.7809 | 56.9% |
| 2025-09 | 90 | 0.0945 | 46.7% |
| 2025-10 | 72 | 1.0937 | 55.6% |
| 2025-11 | 72 | 2.7805 | 63.9% |
| 2025-12 | 90 | -0.0614 | 53.3% |
| 2026-01 | 72 | -0.7292 | 47.2% |
| 2026-02 | 72 | -0.2789 | 40.3% |
| 2026-03 | 90 | 3.2444 | 63.3% |
| 2026-04 | 72 | 0.9163 | 55.6% |
| 2026-05 | 72 | 0.7631 | 52.8% |
| 2026-06 | 18 | -0.0439 | 50.0% |

## Day 14 Long

- Rule: `day_of_month=14`
- Horizon: 10 minute(s)
- Window: All 10-minute bars on the 14th calendar day when it is a trading day.
- Full sample: n=273, mean=1.4016 bps/bar, hit=57.9%, t=2.33, total=382.6 bps
- Train: n=195, mean=1.2295 bps/bar, hit=56.4%, t=1.57, total=239.8 bps
- Test: n=78, mean=1.8318 bps/bar, hit=61.5%, t=2.38, total=142.9 bps
- Monthly direction: 6 positive, 1 negative

| Month | n | Mean bps | Hit Rate |
|---|---:|---:|---:|
| 2025-07 | 39 | 0.6675 | 53.8% |
| 2025-08 | 39 | 0.8357 | 64.1% |
| 2025-10 | 39 | 2.2669 | 53.8% |
| 2025-11 | 39 | 2.5932 | 51.3% |
| 2026-01 | 39 | -0.2158 | 59.0% |
| 2026-04 | 39 | 2.2873 | 69.2% |
| 2026-05 | 39 | 1.3763 | 53.8% |

## First Trading Day Midday Long

- Rule: `first_trading_day_month=True + midday=True`
- Horizon: 10 minute(s)
- Window: Midday 10-minute bars on the first trading day of each month.
- Full sample: n=234, mean=1.0987 bps/bar, hit=57.7%, t=2.27, total=257.1 bps
- Train: n=144, mean=0.9491 bps/bar, hit=59.7%, t=1.55, total=136.7 bps
- Test: n=90, mean=1.3381 bps/bar, hit=54.4%, t=1.69, total=120.4 bps
- Monthly direction: 11 positive, 2 negative

| Month | n | Mean bps | Hit Rate |
|---|---:|---:|---:|
| 2025-06 | 18 | 2.2098 | 72.2% |
| 2025-07 | 18 | 1.6968 | 66.7% |
| 2025-08 | 18 | -0.7749 | 44.4% |
| 2025-09 | 18 | 1.2906 | 50.0% |
| 2025-10 | 18 | 1.9781 | 61.1% |
| 2025-11 | 18 | 1.5708 | 66.7% |
| 2025-12 | 18 | 2.0984 | 72.2% |
| 2026-01 | 18 | -2.4766 | 44.4% |
| 2026-02 | 18 | 1.2973 | 66.7% |
| 2026-03 | 18 | 1.2197 | 38.9% |
| 2026-04 | 18 | 1.2687 | 55.6% |
| 2026-05 | 18 | 0.0231 | 44.4% |
| 2026-06 | 18 | 2.8817 | 66.7% |

## Late-Day Short Bias

- Rule: `minute=15:30`
- Horizon: 10 minute(s)
- Window: The 15:20-15:30 close-to-close window.
- Full sample: n=252, mean=-1.0906 bps/bar, hit=41.3%, t=-2.52, total=-274.8 bps
- Train: n=163, mean=-1.0886 bps/bar, hit=41.7%, t=-2.22, total=-177.4 bps
- Test: n=89, mean=-1.0944 bps/bar, hit=40.4%, t=-1.30, total=-97.4 bps
- Monthly direction: 3 positive, 10 negative

| Month | n | Mean bps | Hit Rate |
|---|---:|---:|---:|
| 2025-06 | 19 | 0.7173 | 57.9% |
| 2025-07 | 22 | -1.8327 | 27.3% |
| 2025-08 | 21 | -0.4541 | 42.9% |
| 2025-09 | 21 | 0.5380 | 57.1% |
| 2025-10 | 23 | -0.7569 | 47.8% |
| 2025-11 | 19 | -3.3154 | 31.6% |
| 2025-12 | 22 | -1.3291 | 27.3% |
| 2026-01 | 20 | -2.2265 | 40.0% |
| 2026-02 | 19 | -1.5000 | 31.6% |
| 2026-03 | 22 | -3.0491 | 31.8% |
| 2026-04 | 21 | 0.5319 | 52.4% |
| 2026-05 | 20 | -0.4566 | 45.0% |
| 2026-06 | 3 | -0.7337 | 66.7% |

## 5-Minute Late-Day Short Bias

- Rule: `minute=15:25`
- Horizon: 5 minute(s)
- Window: The 15:20-15:25 close-to-close window.
- Full sample: n=252, mean=-0.7769 bps/bar, hit=43.3%, t=-2.38, total=-195.8 bps
- Train: n=163, mean=-0.5155 bps/bar, hit=44.8%, t=-1.52, total=-84.0 bps
- Test: n=89, mean=-1.2556 bps/bar, hit=40.4%, t=-1.83, total=-111.7 bps
- Monthly direction: 4 positive, 9 negative

| Month | n | Mean bps | Hit Rate |
|---|---:|---:|---:|
| 2025-06 | 19 | 1.4769 | 57.9% |
| 2025-07 | 22 | -1.7092 | 27.3% |
| 2025-08 | 21 | -0.2354 | 42.9% |
| 2025-09 | 21 | 0.7337 | 52.4% |
| 2025-10 | 23 | 1.0637 | 60.9% |
| 2025-11 | 19 | -3.0671 | 42.1% |
| 2025-12 | 22 | -1.0921 | 31.8% |
| 2026-01 | 20 | -1.0776 | 45.0% |
| 2026-02 | 19 | -0.9062 | 36.8% |
| 2026-03 | 22 | -4.2419 | 22.7% |
| 2026-04 | 21 | 1.0322 | 52.4% |
| 2026-05 | 20 | -1.2820 | 45.0% |
| 2026-06 | 3 | -0.9343 | 66.7% |

## 5-Minute Morning Short Bias

- Rule: `minute=10:50`
- Horizon: 5 minute(s)
- Window: The 10:45-10:50 close-to-close window.
- Full sample: n=252, mean=-1.5284 bps/bar, hit=41.3%, t=-3.29, total=-385.2 bps
- Train: n=163, mean=-1.6352 bps/bar, hit=42.9%, t=-3.04, total=-266.5 bps
- Test: n=89, mean=-1.3328 bps/bar, hit=38.2%, t=-1.53, total=-118.6 bps
- Monthly direction: 2 positive, 11 negative

| Month | n | Mean bps | Hit Rate |
|---|---:|---:|---:|
| 2025-06 | 19 | -1.4437 | 47.4% |
| 2025-07 | 22 | 0.1272 | 45.5% |
| 2025-08 | 21 | -2.1233 | 42.9% |
| 2025-09 | 21 | -1.0735 | 47.6% |
| 2025-10 | 23 | -0.3221 | 47.8% |
| 2025-11 | 19 | -4.2250 | 31.6% |
| 2025-12 | 22 | -2.7751 | 36.4% |
| 2026-01 | 20 | -2.2762 | 35.0% |
| 2026-02 | 19 | -2.5480 | 26.3% |
| 2026-03 | 22 | 0.9046 | 54.5% |
| 2026-04 | 21 | -1.8302 | 47.6% |
| 2026-05 | 20 | -1.5356 | 30.0% |
| 2026-06 | 3 | -0.4925 | 33.3% |
