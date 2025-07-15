import time
import uuid
import requests
import statistics
from datetime import datetime
import pandas as pd
from data.kucoin_data import fetch_active_symbols
from indicators.atr import compute_atr
from data.kucoin_orders import grid_place_order
from utils import fetch_klines_with_fallback, fetch_open_positions_full, close_position, BASE_URL

def ai_volatility_grid_bot():
    print("Scanning for top grid trade candidates...")
    symbols = [s for s in fetch_active_symbols() if s.endswith("USDTM")]
    candidates = []
    for symbol in symbols:
        end = int(datetime.now().timestamp() * 1000)
        start = end - 60 * 60 * 1000
        data = fetch_klines_with_fallback(symbol, start, end)
        if not data or len(data) < 20:
            continue
        df = pd.DataFrame(data, columns=["timestamp","open","high","low","close","volume"])
        df["close"] = df["close"].astype(float)
        atr = compute_atr(df["high"], df["low"], df["close"]).iloc[-1]
        last_close = df["close"].iloc[-1]
        volatility = atr / last_close
        candidates.append((symbol, volatility, last_close))
    candidates.sort(key=lambda x: -x[1])
    print("\nTop grid candidates by volatility:")
    for i, (symbol, vol, price) in enumerate(candidates[:10], 1):
        print(f"{i}. {symbol} | Volatility: {vol:.4f} | Price: {price:.6f}")

    idx = input("Enter the number of the coin to grid trade (or 'q' to cancel): ").strip()
    if idx.lower() == "q":
        print("Cancelled grid bot.")
        return
    try:
        idx = int(idx) - 1
        symbol, volatility, last_price = candidates[idx]
    except Exception:
        print("Invalid selection.")
        return

    while True:
        try:
            usdt_amount = float(input("Enter the USDT amount to use for grid trading: ").strip())
            if usdt_amount > 0:
                break
            else:
                print("Please enter a positive number.")
        except Exception:
            print("Invalid input. Please enter a number.")

    grid_levels = 10
    leverage = 5
    trailing_stop_percent = 0.5
    check_interval = 10

    print(f"\n[AI GRID BOT] Starting grid on {symbol} with {usdt_amount} USDT, {grid_levels} levels, leverage {leverage}x.")

    price_history = []
    def fetch_market_price():
        r = requests.get(f"{BASE_URL}/api/v1/mark-price/{symbol}/current")
        price = float(r.json()['data']['value'])
        price_history.append(price)
        if len(price_history) > 10:
            price_history.pop(0)
        return price

    def estimate_volatility():
        if len(price_history) < 2:
            return 0.005
        stddev = statistics.stdev(price_history)
        avg_price = statistics.mean(price_history)
        return stddev / avg_price

    def place_trailing_stop(side, entry_price, size):
        offset = trailing_stop_percent / 100 * entry_price
        trigger_price = entry_price + offset if side == "buy" else entry_price - offset
        stop_side = "sell" if side == "buy" else "buy"
        print(f"[TRAILING STOP] {side} entry, placing {stop_side} SL at {trigger_price:.6f} for {size:.4f} {symbol}")

    MIN_NOTIONAL = 5
    base_order_margin = usdt_amount / (2 * grid_levels)
    base_order_size = (base_order_margin * leverage) / last_price
    min_size = MIN_NOTIONAL / last_price
    if base_order_size < min_size:
        base_order_size = min_size
        print(f"[WARN] Order size increased to meet minimum notional: {base_order_size:.4f} {symbol}")

    print(f"[INFO] Each grid order size: {base_order_size:.4f} {symbol}, margin per order: {base_order_margin:.4f} USDT, notional: {base_order_size * last_price:.4f} USDT")

    while True:
        try:
            price = fetch_market_price()
            spacing = estimate_volatility() * price
            print(f"[INFO] Current Price: {price:.6f} | Volatility-adjusted spacing: {spacing:.6f}")

            for i in range(1, grid_levels + 1):
                buy_price = round(price - (i * spacing), 6)
                sell_price = round(price + (i * spacing), 6)
                size_buy = base_order_size
                size_sell = base_order_size
                grid_place_order(symbol, "buy", buy_price, size_buy, leverage)
                grid_place_order(symbol, "sell", sell_price, size_sell, leverage)
                place_trailing_stop("buy", buy_price, size_buy)
                place_trailing_stop("sell", sell_price, size_sell)

            print("[GRID] Sleeping before next grid placement...")
            time.sleep(check_interval)
        except Exception as e:
            print(f"[ERROR] Exception in grid bot loop: {e}")
            time.sleep(check_interval)