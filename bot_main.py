import pandas as pd
from datetime import datetime, timedelta
from data.kucoin_data import (
    fetch_klines_rest, fetch_funding_rate, fetch_open_interest, fetch_account_equity,
    fetch_active_symbols
)
from data.orderbook import (
    fetch_orderbook, orderbook_imbalance, volume_profile,
    orderbook_spread, largest_wall, cumulative_depth, orderbook_slope
)
from indicators.macd import compute_macd
from indicators.rsi import compute_rsi
from indicators.bollinger import compute_bollinger
from indicators.atr import compute_atr
from indicators.stochastic import compute_stochastic
from indicators.vwap import compute_vwap
from indicators.moving_average import compute_ema, compute_sma
from strategies.multi_factor import multi_factor_signal
from data.kucoin_orders import place_order, close_position
from data.risk import calculate_position_size
import csv
import os
import time
import uuid
import requests
import hmac
import base64
from dotenv import load_dotenv
from telegram_notify import send_telegram_message
import signal
import json

load_dotenv()
API_KEY = os.getenv("KUCOIN_API_KEY")
API_SECRET = os.getenv("KUCOIN_API_SECRET")
API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")
BASE_URL = os.getenv("BASE_URL", "https://api-futures.kucoin.com")

CSV_FILE = "signal_log.csv"

def log_signal_to_csv(row):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "timestamp", "symbol", "RSI", "MACD", "MACD_signal", "BB_upper", "BB_lower", "ATR",
                "ST_K", "ST_D", "VWAP", "EMA21", "SMA50", "FundingRate", "OpenInterest", "SIGNAL"
            ])
        writer.writerow(row)

def _get_headers(endpoint, method, body=""):
    now = str(int(time.time() * 1000))
    if body and isinstance(body, dict):
        body = json.dumps(body)
    str_to_sign = f"{now}{method}{endpoint}{body}"
    signature = base64.b64encode(
        hmac.new(API_SECRET.encode(), str_to_sign.encode(), digestmod="sha256").digest()
    ).decode()
    passphrase = base64.b64encode(
        hmac.new(API_SECRET.encode(), API_PASSPHRASE.encode(), digestmod="sha256").digest()
    ).decode()
    return {
        "KC-API-TIMESTAMP": now,
        "KC-API-KEY": API_KEY,
        "KC-API-SIGN": signature,
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json",
    }

def save_bad_symbols(bad_symbols, filename="bad_symbols.txt"):
    with open(filename, "w") as f:
        for symbol in bad_symbols:
            f.write(symbol + "\n")

def load_bad_symbols(filename="bad_symbols.txt"):
    if not os.path.isfile(filename):
        return set()
    with open(filename, "r") as f:
        return set(line.strip() for line in f if line.strip())

def fetch_open_positions():
    endpoint = "/api/v1/positions"
    url = BASE_URL + endpoint
    headers = _get_headers(endpoint, "GET")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        result = {}
        if data.get("code") == "200000":
            for pos in data["data"]:
                symbol = pos["symbol"]
                qty = float(pos["currentQty"])
                if qty == 0:
                    continue
                side = "buy" if qty > 0 else "sell"
                size = abs(qty)
                result[symbol] = {
                    "side": side,
                    "size": size,
                }
        return result
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return {}

def fetch_open_positions_full():
    """
    Fetch open positions with full info for dashboard/trailing stop.
    """
    endpoint = "/api/v1/positions"
    url = BASE_URL + endpoint
    headers = _get_headers(endpoint, "GET")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        result = {}
        if data.get("code") == "200000":
            for pos in data["data"]:
                symbol = pos["symbol"]
                qty = float(pos["currentQty"])
                if qty == 0:
                    continue
                side = "buy" if qty > 0 else "sell"
                size = abs(qty)
                entry_price = float(pos.get("avgEntryPrice", 0))
                liq_price = float(pos.get("liquidationPrice", 0))
                margin = float(pos.get("margin", 0))
                unrealized_pnl = float(pos.get("unrealisedPnl", 0))
                roi = float(pos.get("unrealisedPnlRatio", 0)) * 100  # ratio to %
                result[symbol] = {
                    "side": side,
                    "size": size,
                    "entryPrice": entry_price,
                    "liquidationPrice": liq_price,
                    "margin": margin,
                    "unrealizedPNL": unrealized_pnl,
                    "roi": f"{roi:.2f}",
                }
        return result
    except Exception as e:
        print(f"Error fetching full positions: {e}")
        return {}

def get_user_mode():
    print("Select mode:")
    print("1. Trade & Monitor (scan, then confirm trades)")
    print("2. Monitor Only (no new trades, just monitor/close)")
    print("3. Set Dynamic Trailing Stop loss with open position")
    mode = input("Enter 1, 2 or 3: ").strip()
    return mode

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

def input_with_timeout(prompt, timeout=30):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    try:
        value = input(prompt)
        signal.alarm(0)
        return value
    except TimeoutException:
        print("\nNo input received, proceeding with no trades.")
        signal.alarm(0)
        return None

def fetch_klines_with_fallback(symbol, start, end):
    """
    Try KuCoin first, then fall back to Binance if not enough data.
    """
    data = fetch_klines_rest(symbol, start, end)
    if data and len(data) >= 20:
        return data
    # Fallback: try Binance (convert symbol if needed)
    binance_symbol = symbol.replace("USDTM", "USDT")
    try:
        from fetch_binance_klines import fetch_binance_klines
        data = fetch_binance_klines(binance_symbol, start, end)
        if data and len(data) >= 20:
            print(f"Fetched {len(data)} klines for {symbol} from Binance as fallback.")
            return data
    except Exception as e:
        print(f"Binance fallback failed for {symbol}: {e}")
    print(f"Could not get enough price data for {symbol} from any source.")
    return None

def main(trade_mode=True):
    bad_symbols = load_bad_symbols()
    open_positions = fetch_open_positions()

    if trade_mode:
        symbols = [s for s in fetch_active_symbols() if s.endswith("USDTM") and s not in bad_symbols]
        print("Scanning symbols:", symbols)
    else:
        symbols = list(open_positions.keys())
        print("Monitor Only mode: Monitoring open positions:", symbols)

    stop_loss_pct = 0.02  # Set your stop loss percent (e.g., 2%)
    trade_candidates = []

    for symbol in symbols:
        if symbol in bad_symbols:
            continue
        end = int(datetime.now().timestamp() * 1000)
        # Fetch more data for indicators
        start = int((datetime.now() - timedelta(minutes=300)).timestamp() * 1000)
        data = fetch_klines_rest(symbol, start, end)
        if not data or len(data) < 60:
            print(f"Not enough data for {symbol}")
            continue
        df = pd.DataFrame(data, columns=["timestamp","open","high","low","close","volume"])
        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        rsi = compute_rsi(df["close"])
        last_rsi = rsi.iloc[-1]
        macd, macd_signal, macd_diff = compute_macd(df["close"])
        last_macd = macd.iloc[-1]
        last_macd_signal = macd_signal.iloc[-1]
        bb_upper, bb_lower, bb_middle = compute_bollinger(df["close"])
        last_bb_upper = bb_upper.iloc[-1]
        last_bb_lower = bb_lower.iloc[-1]
        last_bb_middle = bb_middle.iloc[-1]
        atr = compute_atr(df["high"], df["low"], df["close"])
        last_atr = atr.iloc[-1]
        # Stochastic Oscillator
        stoch_k, stoch_d = compute_stochastic(df["high"], df["low"], df["close"])
        last_stoch_k = stoch_k.iloc[-1]
        last_stoch_d = stoch_d.iloc[-1]

        # VWAP
        vwap = compute_vwap(df)
        last_vwap = vwap.iloc[-1]

        # EMA and SMA
        ema21 = compute_ema(df["close"], span=21)
        last_ema21 = ema21.iloc[-1]
        sma50 = compute_sma(df["close"], window=50)
        last_sma50 = sma50.iloc[-1]


        funding_rate = fetch_funding_rate(symbol)
        open_interest = fetch_open_interest(symbol)

        signal = multi_factor_signal(
            last_rsi, last_macd, last_macd_signal, df["close"].iloc[-1],
            last_bb_upper, last_bb_lower, last_atr,
            last_stoch_k, last_stoch_d, last_vwap
        )

        # --- Calculate signal points (reuse your dashboard2 logic or define here) ---
        def calculate_signal_points_for_main():
            points = 0
            # Example: match your dashboard2.py logic
            if last_rsi < 35:
                points += 1
            if last_macd > 0:
                points += 1
            if df["close"].iloc[-1] < last_bb_lower:
                points += 1
            if last_stoch_k < 20 and last_stoch_d < 20:
                points += 1
            # Add more confluence checks as needed
            return points

        points = calculate_signal_points_for_main()

        # Require at least 3 points for a "buy" or "sell" to be considered
        if signal in ["buy", "sell"] and points < 3:
            signal = "hold"

        print(
            f"{symbol}: RSI={last_rsi:.2f}, MACD={last_macd:.4f}, MACD_signal={last_macd_signal:.4f}, "
            f"BB_upper={last_bb_upper:.2f}, BB_lower={last_bb_lower:.2f}, ATR={last_atr:.2f}, "
            f"ST_K={last_stoch_k:.2f}, ST_D={last_stoch_d:.2f}, VWAP={last_vwap:.2f}, "
            f"EMA21={last_ema21:.2f}, SMA50={last_sma50:.2f}, "
            f"FundingRate={funding_rate}, OpenInterest={open_interest}, SIGNAL={signal}"
        )
        log_signal_to_csv([
            datetime.now().isoformat(), symbol, last_rsi, last_macd, last_macd_signal,
            last_bb_upper, last_bb_lower, last_atr, last_stoch_k, last_stoch_d,
            last_vwap, last_ema21, last_sma50, funding_rate, open_interest, signal
        ])

        orderbook = fetch_orderbook(symbol)
        if orderbook:
            imbalance = orderbook_imbalance(orderbook)
            spread = orderbook_spread(orderbook)
            bid_wall_price, bid_wall_size = largest_wall(orderbook, "bids")
            ask_wall_price, ask_wall_size = largest_wall(orderbook, "asks")
            bid_liq, ask_liq = cumulative_depth(orderbook, pct=0.1)
            bid_slope = orderbook_slope(orderbook, "bids")
            ask_slope = orderbook_slope(orderbook, "asks")
            print(
                f"{symbol}: Imb={imbalance:.2f}, Spread={spread:.2f}, "
                f"BidWall={bid_wall_price:.2f}@{bid_wall_size:.0f}, "
                f"AskWall={ask_wall_price:.2f}@{ask_wall_size:.0f}, "
                f"BidLiq={bid_liq:.0f}, AskLiq={ask_liq:.0f}, "
                f"BidSlope={bid_slope:.2f}, AskSlope={ask_slope:.2f}"
            )
        else:
            imbalance = None

        # Trading logic (example)
        # Account parameters (replace with real values)
        pos = open_positions.get(symbol)
        # Always check for close logic if position exists
        if pos:
            if (pos["side"] == "buy" and signal == "sell") or (pos["side"] == "sell" and signal == "buy"):
                if trade_mode:
                    print(f"\nSignal to close {pos['side']} position for {symbol}, size={pos['size']}.")
                    confirm = input(f"Do you want to close this position? (y/n): ").strip().lower()
                    if confirm == "y":
                        client_oid = str(uuid.uuid4())
                        response = close_position(symbol, pos["side"], pos["size"], client_oid=client_oid)
                        print(f"Closed {pos['side']} position for {symbol}, size={pos['size']}. Response: {response}")
                    else:
                        print(f"Skipped closing {pos['side']} position for {symbol}.")
                else:
                    # Monitor mode: close automatically
                    print(f"\n[Monitor Mode] Auto-closing {pos['side']} position for {symbol}, size={pos['size']}.")
                    client_oid = str(uuid.uuid4())
                    response = close_position(symbol, pos["side"], pos["size"], client_oid=client_oid)
                    print(f"Closed {pos['side']} position for {symbol}, size={pos['size']}. Response: {response}")
            continue  # Do not consider new entries for open positions

        # Only add new trades if in trade_mode
        if trade_mode and signal in ["buy", "sell"] and not pos:
            trade_candidates.append({
                "symbol": symbol,
                "signal": signal,
                "rsi": last_rsi,
                "size": None,  # Will calculate after sorting
                "stop_loss_pct": stop_loss_pct
            })

    # --- Sort trade candidates: buys (lowest RSI first), sells (highest RSI first) ---
    buys = [t for t in trade_candidates if t["signal"] == "buy"]
    sells = [t for t in trade_candidates if t["signal"] == "sell"]
    buys.sort(key=lambda x: x["rsi"])
    sells.sort(key=lambda x: -x["rsi"])
    sorted_trades = buys + sells

    if trade_mode and sorted_trades:
        print("\nTop trade candidates:")
        for i, t in enumerate(sorted_trades, 1):
            print(f"{i}. {t['signal'].upper()} {t['symbol']} (RSI={t['rsi']:.2f})")
        top_5_buys = buys[:5]
        if top_5_buys:
            message = "Top 5 Buy Candidates:\n"
            for t in top_5_buys:
                message += f"{t['symbol']} (RSI={t['rsi']:.2f})\n"
            send_telegram_message(message)

            # <-- Add the file writing code here
            with open("top_candidates.txt", "w") as f:
                for t in top_5_buys:
                    f.write(f"{t['symbol']}\n")

        to_trade = input_with_timeout("Enter numbers of trades to execute (comma separated, or 'all'): ", timeout=30)
        if not to_trade:
            print("No trades selected. Will rerun in 1 minute.")
            return  # Skip to next loop
        if to_trade.lower() == "all":
            selected = sorted_trades
        else:
            idxs = [int(x.strip())-1 for x in to_trade.split(",") if x.strip().isdigit()]
            selected = [sorted_trades[i] for i in idxs if 0 <= i < len(sorted_trades)]

        # --- Ask user for $ amount per trade ---
        while True:
            try:
                usd_amount = float(input("Enter the USDT amount you want to use for each trade: ").strip())
                if usd_amount > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except Exception:
                print("Invalid input. Please enter a number.")

        # Now execute only selected trades
        for t in selected:
            account_equity = fetch_account_equity()  # Fetch fresh balance for each trade
            if account_equity is None or account_equity <= 5:
                print(f"Account equity too low for {t['symbol']}, skipping.")
                continue
            leverage = 5
            # Fetch latest price for the symbol
            end = int(datetime.now().timestamp() * 1000)
            start = end - 60 * 60 * 1000
            data = fetch_klines_rest(t["symbol"], start, end)
            if not data or len(data) < 1:
                print(f"Could not get price for {t['symbol']}, skipping.")
                continue
            df = pd.DataFrame(data, columns=["timestamp","open","high","low","close","volume"])
            df["close"] = df["close"].astype(float)
            price = float(df["close"].iloc[-1])
            size = int((usd_amount * leverage) / price)
            notional = size * price
            required_margin = notional / leverage

            if required_margin > account_equity:
                print(f"Required margin {required_margin:.2f} exceeds account equity {account_equity:.2f} for {t['symbol']}, reducing size.")
                min_size = 1
                while size > min_size:
                    size -= 1
                    notional = size * price
                    required_margin = notional / leverage
                    if required_margin <= account_equity:
                        break
                if size <= min_size:
                    print(f"Could not find suitable size for {t['symbol']}, skipping order.")
                    continue

            if size > 0:
                client_oid = str(uuid.uuid4())
                response = place_order(
                    t["symbol"], t["signal"], size,
                    client_oid=client_oid,
                    leverage=leverage,
                    order_type="market"
                )
                print(f"Placed {t['signal']} order for {t['symbol']}, size={size}, leverage={leverage}. Response: {response}")
            else:
                print(f"Calculated size is 0 for {t['symbol']}, skipping order.")
    else:
        print("Monitor only mode: No new trades will be placed.")

    save_bad_symbols(bad_symbols)

def set_trailing_stop(symbol, side, trailing_stop, api_key, api_secret, api_passphrase):
    """
    Place a stop order (KuCoin Futures) as a trailing stop.
    """
    endpoint = "/api/v1/stopOrders"
    url = BASE_URL + endpoint
    # KuCoin expects the body as a JSON string for signing
    payload = {
        "symbol": symbol,
        "side": "sell" if side == "buy" else "buy",  # Stop is always opposite side
        "leverage": 5,  # Adjust as needed
        "stop": "down" if side == "buy" else "up",  # "down" for long, "up" for short
        "stopPriceType": "TP",  # "TP" (take profit) or "MP" (mark price); adjust as needed
        "stopPrice": str(trailing_stop),
        "orderType": "market",
        "size": 1  # You must set the correct size!
    }
    body = json.dumps(payload)
    headers = _get_headers(endpoint, "POST", body)
    try:
        resp = requests.post(url, headers=headers, data=body, timeout=10)
        print(f"Set trailing stop for {symbol} ({side}) at {trailing_stop:.4f}: {resp.text}")
        return resp.json()
    except Exception as e:
        print(f"Error setting trailing stop for {symbol}: {e}")
        return None

def set_dynamic_trailing_stop_for_open_positions():
    print("Dynamic Trailing Stop Mode: Monitoring trailing stops for open positions...")
    open_positions = fetch_open_positions_full()
    selected_symbols = select_positions(open_positions)
    if not selected_symbols:
        print("No positions selected. Exiting trailing stop mode.")
        return
    # Only keep selected positions
    open_positions = {s: open_positions[s] for s in selected_symbols}
    trailing_stops = {}
    atr_multipler = 2  # You can tune this value

    # Initialize trailing stop values and entry prices for each position
    for symbol, pos in open_positions.items():
        end = int(datetime.now().timestamp() * 1000)
        start = end - 60 * 60 * 1000
        data = fetch_klines_with_fallback(symbol, start, end)
        if not data or len(data) < 20:
            print(f"Could not get enough price data for {symbol}, skipping.")
            continue
        df = pd.DataFrame(data, columns=["timestamp","open","high","low","close","volume"])
        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        price = float(df["close"].iloc[-1])
        atr = compute_atr(df["high"], df["low"], df["close"]).iloc[-1]
        entry_price = pos.get("entryPrice", price)
        if pos["side"] == "buy":
            trailing_stops[symbol] = price - atr_multipler * atr
        else:
            trailing_stops[symbol] = price + atr_multipler * atr

    print("Trailing stops initialized (ATR-based). Monitoring live prices...")

    while True:
        open_positions = fetch_open_positions_full()
        table_lines = [
            "\nSymbol | Side | Amount | Entry Price | Mark Price | Liq. Price | Margin | Unrealized PNL (ROI%) | Trailing Stop | Locked-in Profit %"
        ]
        for symbol, pos in open_positions.items():
            end = int(datetime.now().timestamp() * 1000)
            start = end - 30 * 60 * 1000
            data = fetch_klines_with_fallback(symbol, start, end)
            if not data or len(data) < 15:
                continue
            df = pd.DataFrame(data, columns=["timestamp","open","high","low","close","volume"])
            df["close"] = df["close"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            price = float(df["close"].iloc[-1])
            atr = compute_atr(df["high"], df["low"], df["close"]).iloc[-1]
            entry = pos.get("entryPrice", price)
            trailing = trailing_stops[symbol]
            amount = pos.get("size", "-")
            liq_price = pos.get("liquidationPrice", "-")
            margin = pos.get("margin", "-")
            unrealized_pnl = pos.get("unrealizedPNL", "-")
            roi = pos.get("roi", "-")

            # Update trailing stop if price moves favorably
            if pos["side"] == "buy":
                new_trailing = price - atr_multipler * atr
                if new_trailing > trailing_stops[symbol]:
                    trailing_stops[symbol] = new_trailing
                profit = (price - entry) / entry * 100
                locked_profit_pct = (trailing_stops[symbol] - entry) / entry * 100
                locked_profit_usdt = (trailing_stops[symbol] - entry) * float(amount)
                table_lines.append(
                    f"{symbol} | BUY  | {amount} | {entry:.8f} | {price:.8f} | {liq_price} | {margin} | {unrealized_pnl} ({roi}%) | {trailing_stops[symbol]:.8f} | {locked_profit_pct:+.2f}% | {locked_profit_usdt:+.8f} USDT"
                )
                if price <= trailing_stops[symbol]:
                    print(f"Trailing stop hit for {symbol} (buy) at {price:.8f}. Closing position...")
                    client_oid = str(uuid.uuid4())
                    response = close_position(symbol, pos["side"], amount, client_oid=client_oid)
                    print(f"Closed {pos['side']} position for {symbol}, size={amount}. Response: {response}")
                    del trailing_stops[symbol]
            else:
                new_trailing = price + atr_multipler * atr
                if new_trailing < trailing_stops[symbol]:
                    trailing_stops[symbol] = new_trailing
                profit = (entry - price) / entry * 100
                locked_profit_pct = (entry - trailing_stops[symbol]) / entry * 100
                locked_profit_usdt = (entry - trailing_stops[symbol]) * float(amount)
                table_lines.append(
                    f"{symbol} | SELL | {amount} | {entry:.8f} | {price:.8f} | {liq_price} | {margin} | {unrealized_pnl} ({roi}%) | {trailing_stops[symbol]:.8f} | {locked_profit_pct:+.2f}% | {locked_profit_usdt:+.4f} USDT"
                )
                if price >= trailing_stops[symbol]:
                    print(f"Trailing stop hit for {symbol} (sell) at {price:.8f}. Closing position...")
                    client_oid = str(uuid.uuid4())
                    response = close_position(symbol, pos["side"], amount, client_oid=client_oid)
                    print(f"Closed {pos['side']} position for {symbol}, size={amount}. Response: {response}")
                    del trailing_stops[symbol]

        if table_lines:
            print("\n".join(table_lines))

        if not trailing_stops:
            print("All trailing stops triggered or positions closed.")
            break

        time.sleep(10)  # Check every 10 seconds

# You need to implement fetch_open_positions_full() to return all the extra info for each position.
# You can adapt your fetch_open_positions() to include entryPrice, liquidationPrice, margin, unrealizedPNL, roi, etc.
def main_loop():
    mode = get_user_mode()
    trade_mode = (mode == "1")
    trailing_stop_mode = (mode == "3")
    while True:
        if trailing_stop_mode:
            set_dynamic_trailing_stop_for_open_positions()
            print("Sleeping for 1 minute before next trailing stop update...")
            time.sleep(60)
        else:
            main(trade_mode=trade_mode)
            print("Sleeping for 1 minute before next run...")
            time.sleep(60)

def select_positions(open_positions):
    if not open_positions:
        print("No open positions found.")
        return []
    print("\nOpen Positions:")
    symbols = list(open_positions.keys())
    for i, symbol in enumerate(symbols, 1):
        pos = open_positions[symbol]
        print(f"{i}. {symbol} | {pos['side'].upper()} | Size: {pos['size']} | Entry: {pos.get('entryPrice', '-')}")
    selection = input("Enter numbers of positions to apply trailing stop (comma separated, or 'all'): ").strip()
    if selection.lower() == "all":
        return symbols
    idxs = [int(x.strip())-1 for x in selection.split(",") if x.strip().isdigit()]
    return [symbols[i] for i in idxs if 0 <= i < len(symbols)]

if __name__ == "__main__":
    main_loop()