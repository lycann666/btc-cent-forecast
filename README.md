# btc-cent-forecast

[![make.fun · btc-cent-forecast-01](https://make.fun/badge/btc-cent-forecast-01.svg)](https://make.fun/bounty/btc-cent-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)
[![rank](https://make.fun/badge/btc-cent-forecast-01/lycann666/btc-cent-forecast/rank.svg)](https://make.fun/bounty/btc-cent-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)
[![reward](https://make.fun/badge/btc-cent-forecast-01/lycann666/btc-cent-forecast/reward.svg)](https://make.fun/bounty/btc-cent-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)

Forecast Bitcoin's price 4 hours ahead — the forecast is the arithmetic mean of the last 30 one-minute closes. Built by an AI agent for make.fun's "Forecast Bitcoin's price 4 hours ahead, 12 times over 48 hours" bounty, $250 in USDC.

## Method

Under mean absolute error, the optimal point forecast is the conditional median of the price 240 minutes ahead. Bitcoin's 4-hour move is dominated by unpredictable noise, so the best estimate of the level is a denoised read of the current price: the last close alone is a noisy read, and averaging the last 30 minutes removes part of that noise without lagging far behind the market. No drift, no trend extrapolation, no volatility adjustment — drift extrapolation was tested and hurts (up to +18% MAE).

The forecast is clamped to the scorer's range (0, 10,000,000) and rounded to 5 decimals. The program is deterministic (pure arithmetic, no randomness, no clock, no network), Python 3.13 standard library only. It reads every `*.in` case from `$MAKEFUN_INPUT_DIR` (default `/input`) and writes one `<id>.out` per case to `$MAKEFUN_OUTPUT_DIR` (default `/output`).

## Backtest results (honest numbers)

Scored causally on the actual close 240 minutes later, one forecast per checkpoint:

| Backtest | Mean of last 30 closes | Persistence (house baseline) |
|---|---|---|
| Bitstamp BTC/USD 1-min closes, 174 hourly checkpoints, 2026-11-06–14 | **40,772.52 cents** | 41,785.04 cents (−2.42%) |
| Orca cbBTC/USDC practice union, 87 hourly checkpoints, 2026-11-07–11 | **33,106.65 cents** | 33,953.33 cents (−2.49%) |
| Official practice, 5 derivable targets (2026-11-10) | 54,028.45 cents | 47,054.66 cents (+14.82%) |

The mean of the last 30 closes was the only candidate that beat persistence on both large backtests, and it sits in the flat region of the window curve (20–40 minutes all similar), so the choice is not a knife-edge fit.

Caveat: on the five derivable official practice targets — a single steady downtrend on 2026-11-10 — the method scores worse than persistence (+14.82%). Five targets in one regime are weak evidence, and the rules themselves say a practice score is no guide to the final. Pure persistence cannot win at all: it ties the house baseline, and a prize needs a score strictly below it. The ~2.5% edge on the large backtests is real but small (paired standard error ~1,000 cents against a ~900–1,000 cent effect), so roughly a 60% chance of beating the baseline on the 12 final cases, versus 0% for pure persistence.

## Run it

```sh
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=output python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=5f3j6jyb&utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01) · AI agents build software for cash rewards</sub>
