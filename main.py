"""Bitcoin 4-hour-ahead point forecaster for make.fun btc-cent-forecast-01.

Method: the forecast is the arithmetic mean of the last 30 one-minute
closes. Rationale, validated on two independent backtests (see README):
- Under mean absolute error the optimal point forecast is the conditional
  median of the price 240 minutes ahead. Bitcoin's 4-hour move is dominated
  by unpredictable noise, so the best estimate of the level is a denoised
  read of the current price; the last close alone is a noisy read, and
  averaging the last 30 minutes removes part of that noise without lagging
  far behind the market.
- Drift extrapolation was tested and HURTS (up to +18% MAE): the 4-hour
  drift is noise. Short-window averages (3-15 min) and long ones (45-60
  min) both score worse than 30 min on the same backtests.
- Backtests (causal, one forecast per checkpoint, scored on the actual
  close 240 minutes later): Bitstamp BTC/USD 1-minute closes, 174 hourly
  checkpoints, 2026-11-06 to 2026-11-14: mean30 MAE 40,772.52 cents vs
  persistence 41,785.04 (-2.42%). Orca cbBTC/USDC practice union, 87 hourly
  checkpoints, 2026-11-07 to 2026-11-11: mean30 MAE 33,106.65 cents vs
  persistence 33,953.33 (-2.49%). The mean of the last 30 closes was the
  only candidate that beat persistence on BOTH backtests.
- Honest caveat: on the five derivable official practice targets (a single
  steady downtrend, 2026-11-10) mean30 scores 54,028.45 cents vs
  persistence 47,054.66 (+14.82%). Five targets in one regime are weak
  evidence; the rules themselves say a practice score is no guide to the
  final. Pure persistence cannot win at all: it ties the house baseline,
  and a prize needs a score strictly below it.

Deterministic: pure arithmetic, no randomness, no clock, no network.
Reads $MAKEFUN_INPUT_DIR (else /input), writes $MAKEFUN_OUTPUT_DIR
(else /output). One malformed case file no longer aborts the run: it is
skipped with a stderr warning and the run exits nonzero. Python 3.13,
standard library only.
"""

import json
import math
import os
import sys

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

# Number of recent one-minute closes averaged for the level estimate.
WINDOW = 30
# Price bounds from the kit's starter: the grid's 5 decimals, inside the
# scorer's (0, 10,000,000) range.
MIN_PRICE = 0.00001
MAX_PRICE = 9999999.99999


def price5(x):
    """Clamp to the scorer's range and round to the grid's 5 decimals.

    Note: json.dumps drops a trailing zero (e.g. 73010.11320 is written
    as 73010.1132), so an .out file may be 50 bytes instead of 51 when
    the 5th decimal is 0. The value is still a valid 5-decimal price.
    """
    return round(min(MAX_PRICE, max(MIN_PRICE, x)) * 1e5) / 1e5


def forecast(prices):
    """Mean of the last WINDOW finite closes (fewer if the series is short)."""
    finite = [p for p in prices if isinstance(p, (int, float)) and math.isfinite(p)]
    if not finite:
        raise ValueError("market has no finite prices")
    window = finite[-WINDOW:]
    return price5(sum(window) / len(window))


def process_case(fname):
    """Forecast one case file. Returns True on success, False if malformed.

    A malformed case must not abort the whole run: with 12 final cases,
    one bad input would otherwise cost all 12 forecasts. Bad cases are
    reported on stderr and counted so the run still exits nonzero.
    """
    case_id = fname[: -len(".in")]
    try:
        with open(os.path.join(INPUT_DIR, fname), "r", encoding="utf-8") as f:
            case = json.load(f)
        market = case["markets"][0]
        guess = forecast(market["prices"])
    except (OSError, ValueError, KeyError, IndexError, TypeError) as e:
        print(f"warning: skipping malformed case {case_id}: {e}", file=sys.stderr)
        return False
    out_path = os.path.join(OUTPUT_DIR, case_id + ".out")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"forecasts": [{"case": case_id, "price": guess}]},
                          separators=(",", ":")) + "\n")
    return True


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    inputs = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".in"))
    failed = [fname for fname in inputs if not process_case(fname)]
    if failed:
        raise SystemExit(f"{len(failed)} case(s) failed: {', '.join(sorted(failed))}")


if __name__ == "__main__":
    main()
