import time
import pandas as pd
from datetime import datetime
from indicators.atr import compute_atr
from utils import fetch_klines_with_fallback, fetch_open_positions_full, close_position

TRAILING_STOP_MULTIPLIER = 2
TRAILING_STOP_INTERVAL = 60

def set_dynamic_trailing_stop_for_open_positions():
    print("Dynamic Trailing Stop Mode: Monitoring trailing stops for open positions...")
    while True:
        open_positions = fetch_open_positions_full()
        if not open_positions:
            print("No open positions found.")
            time.sleep(TRAILING_STOP_INTERVAL)
            continue

        for symbol, pos in open_positions.items():
            side = pos['side']
            entry_price = float(pos.get('entryPrice', 0))
            size = float(pos.get('size', 0))
            if entry_price == 0 or size == 0:
                continue

            end = int(datetime.now().timestamp() * 1000)
            start = end - 60 * 60 * 1000
            klines = fetch_klines_with_fallback(symbol, start, end)
            if not klines or len(klines) < 20:
                print(f"Not enough data for {symbol}")
                continue

            df = pd.DataFrame(klines, columns=["timestamp","open","high","low","close","volume"])
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            df["close"] = df["close"].astype(float)
            atr = compute_atr(df["high"], df["low"], df["close"]).iloc[-1]

            if side == "buy":
                trailing_stop = max(df["close"].iloc[-1] - TRAILING_STOP_MULTIPLIER * atr, entry_price * 0.95)
            else:
                trailing_stop = min(df["close"].iloc[-1] + TRAILING_STOP_MULTIPLIER * atr, entry_price * 1.05)

            print(f"{symbol} | {side.upper()} | Entry: {entry_price:.4f} | Size: {size} | ATR: {atr:.4f} | Trailing Stop: {trailing_stop:.4f}")

            last_price = df["close"].iloc[-1]
            if (side == "buy" and last_price <= trailing_stop) or (side == "sell" and last_price >= trailing_stop):
                print(f"Closing {side} position on {symbol} at {last_price:.4f} (trailing stop hit)")
                close_position(symbol, side)
            else:
                print(f"Position on {symbol} is safe. Monitoring...")

        time.sleep(TRAILING_STOP_INTERVAL)