# Deep Dive: Tuesday 13:30-13:40 SPY Long Window

After expanding the dataset back to 2021, this became the strongest simple intraday long candidate.

Plain-English thesis: on Tuesdays, SPY tended to rise from the 13:30 close to the 13:40 close more than normal.

This is research, not investment advice.

## Key Numbers

| Measure | Result | Plain-English Meaning |
|---|---:|---|
| Average move | +2.0536 bps | Average gross Tuesday move during this 10-minute window |
| Win rate | 60.6% | Percent of matching Tuesdays that were positive |
| Times tested | 282 | Number of Tuesday observations in the sample |
| Total gross move | +579.1 bps | Sum before spread/slippage/costs |

## Earlier vs Later Period

| Period | Days | Avg Move | Win Rate | Total Gross Move |
|---|---:|---:|---:|---:|
| Earlier period | 183 | +1.5254 bps | 60.7% | +279.1 bps |
| Later period | 99 | +3.0301 bps | 60.6% | +300.0 bps |

## Year-by-Year

![Tuesday 13:30-13:40 yearly results](charts/spy_2021_2026_tue_1340_yearly.svg)

| Year | Days | Avg Move | Win Rate | Total Gross Move |
|---|---:|---:|---:|---:|
| 2021 | 52 | +2.0517 bps | 73.1% | +106.7 bps |
| 2022 | 52 | +1.3716 bps | 51.9% | +71.3 bps |
| 2023 | 51 | +0.2826 bps | 52.9% | +14.4 bps |
| 2024 | 53 | +2.4678 bps | 66.0% | +130.8 bps |
| 2025 | 52 | +3.3515 bps | 57.7% | +174.3 bps |
| 2026 | 22 | +3.7106 bps | 63.6% | +81.6 bps |

## Month-by-Month

| Month | Days | Avg Move | Win Rate | Total Gross Move |
|---|---:|---:|---:|---:|
| 2021-01 | 4 | +6.8737 bps | 100.0% | +27.5 bps |
| 2021-02 | 4 | +2.0533 bps | 75.0% | +8.2 bps |
| 2021-03 | 5 | -3.8924 bps | 40.0% | -19.5 bps |
| 2021-04 | 4 | +5.1044 bps | 100.0% | +20.4 bps |
| 2021-05 | 4 | +2.3340 bps | 50.0% | +9.3 bps |
| 2021-06 | 5 | +1.2723 bps | 80.0% | +6.4 bps |
| 2021-07 | 4 | +1.8450 bps | 75.0% | +7.4 bps |
| 2021-08 | 5 | -1.8666 bps | 60.0% | -9.3 bps |
| 2021-09 | 4 | +5.7147 bps | 100.0% | +22.9 bps |
| 2021-10 | 4 | +6.4078 bps | 100.0% | +25.6 bps |
| 2021-11 | 5 | +1.9597 bps | 60.0% | +9.8 bps |
| 2021-12 | 4 | -0.5023 bps | 50.0% | -2.0 bps |
| 2022-01 | 4 | +9.3785 bps | 75.0% | +37.5 bps |
| 2022-02 | 4 | -0.7955 bps | 50.0% | -3.2 bps |
| 2022-03 | 5 | +3.6345 bps | 80.0% | +18.2 bps |
| 2022-04 | 4 | -0.8095 bps | 50.0% | -3.2 bps |
| 2022-05 | 5 | +25.6444 bps | 100.0% | +128.2 bps |
| 2022-06 | 4 | -15.9306 bps | 0.0% | -63.7 bps |
| 2022-07 | 4 | +5.2518 bps | 50.0% | +21.0 bps |
| 2022-08 | 5 | -5.4295 bps | 20.0% | -27.1 bps |
| 2022-09 | 4 | -5.8862 bps | 25.0% | -23.5 bps |
| 2022-10 | 4 | +4.7008 bps | 75.0% | +18.8 bps |
| 2022-11 | 5 | -5.0863 bps | 40.0% | -25.4 bps |
| 2022-12 | 4 | -1.5318 bps | 50.0% | -6.1 bps |
| 2023-01 | 5 | +7.3063 bps | 80.0% | +36.5 bps |
| 2023-02 | 4 | -0.7186 bps | 50.0% | -2.9 bps |
| 2023-03 | 4 | -3.8563 bps | 50.0% | -15.4 bps |
| 2023-04 | 4 | +0.4232 bps | 50.0% | +1.7 bps |
| 2023-05 | 5 | +3.5380 bps | 60.0% | +17.7 bps |
| 2023-06 | 4 | -1.3258 bps | 25.0% | -5.3 bps |
| 2023-07 | 3 | -0.0059 bps | 33.3% | -0.0 bps |
| 2023-08 | 5 | -0.6517 bps | 40.0% | -3.3 bps |
| 2023-09 | 4 | -3.2701 bps | 50.0% | -13.1 bps |
| 2023-10 | 5 | -2.8138 bps | 20.0% | -14.1 bps |
| 2023-11 | 4 | +3.0512 bps | 100.0% | +12.2 bps |
| 2023-12 | 4 | +0.0801 bps | 75.0% | +0.3 bps |
| 2024-01 | 5 | -0.6244 bps | 40.0% | -3.1 bps |
| 2024-02 | 4 | +3.0927 bps | 75.0% | +12.4 bps |
| 2024-03 | 4 | +0.0903 bps | 50.0% | +0.4 bps |
| 2024-04 | 5 | +11.7439 bps | 80.0% | +58.7 bps |
| 2024-05 | 4 | +1.0820 bps | 75.0% | +4.3 bps |
| 2024-06 | 4 | +1.7467 bps | 75.0% | +7.0 bps |
| 2024-07 | 5 | +3.5180 bps | 80.0% | +17.6 bps |
| 2024-08 | 4 | -1.7126 bps | 50.0% | -6.9 bps |
| 2024-09 | 4 | -4.6644 bps | 25.0% | -18.7 bps |
| 2024-10 | 5 | +7.1395 bps | 80.0% | +35.7 bps |
| 2024-11 | 4 | +2.8771 bps | 75.0% | +11.5 bps |
| 2024-12 | 5 | +2.3719 bps | 80.0% | +11.9 bps |
| 2025-01 | 4 | -2.5406 bps | 25.0% | -10.2 bps |
| 2025-02 | 4 | +10.7482 bps | 50.0% | +43.0 bps |
| 2025-03 | 4 | +13.8442 bps | 100.0% | +55.4 bps |
| 2025-04 | 5 | +24.4773 bps | 100.0% | +122.4 bps |
| 2025-05 | 4 | -4.4757 bps | 50.0% | -17.9 bps |
| 2025-06 | 4 | +3.3224 bps | 75.0% | +13.3 bps |
| 2025-07 | 5 | -3.9950 bps | 40.0% | -20.0 bps |
| 2025-08 | 4 | +1.1177 bps | 75.0% | +4.5 bps |
| 2025-09 | 5 | +0.0111 bps | 60.0% | +0.1 bps |
| 2025-10 | 4 | -2.7688 bps | 50.0% | -11.1 bps |
| 2025-11 | 4 | -0.6409 bps | 25.0% | -2.6 bps |
| 2025-12 | 5 | -0.5232 bps | 40.0% | -2.6 bps |
| 2026-01 | 4 | -0.0511 bps | 50.0% | -0.2 bps |
| 2026-02 | 4 | +9.9102 bps | 75.0% | +39.6 bps |
| 2026-03 | 5 | -0.4715 bps | 60.0% | -2.4 bps |
| 2026-04 | 4 | +11.5110 bps | 100.0% | +46.0 bps |
| 2026-05 | 4 | +0.2533 bps | 50.0% | +1.0 bps |
| 2026-06 | 1 | -2.5033 bps | 0.0% | -2.5 bps |

## Business Read

This pattern is more specific than the old daily 13:20-13:30 idea. That is both good and bad. Good, because the numbers are stronger. Bad, because a narrower rule gives us fewer examples and can be easier to overfit.

The next step is not to trade it blindly. The next step is to paper-track it exactly as written and compare it against the original daily 13:20-13:30 rule.