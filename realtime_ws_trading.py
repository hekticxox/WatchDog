import asyncio
import json
import websockets
import pandas as pd
from datetime import datetime
from indicators.macd import compute_macd
from indicators.rsi import compute_rsi
from indicators.bollinger import compute_bollinger
from indicators.atr import compute_atr
from strategies.multi_factor import multi_factor_signal
from data.kucoin_orders import place_order
from data.risk import calculate_position_size
from data.kucoin_data import fetch_account_equity, fetch_active_symbols
from bot_main import load_bad_symbols
import time

endpoint = "wss://ws-api-futures.kucoin.com/"
token = "2neAiuYvAU61ZDXANAGAsiL4-iAExhsBXZxftpOeh_55i3Ysy2q2LEsEWU64mdzUOPusi34M_wGoSf7iNyEWJ9Ydq3-ytBNUpIxNZ-GlZJtpNI-2di4Pt9iYB9J6i9GjsxUuhPw3Blq6rhZlGykT3Vp1phUafnulOOpts-MEmEE2LOdtdhZM5tGV5iL_SfjbJBvJHl5Vs9Y=.hEYnaEYp5J29cYFLxrXovw=="  # Replace with your token

# 1. Fetch all active USDT-margined futures symbols
bad_symbols = load_bad_symbols()
symbols = [s for s in fetch_active_symbols() if s.endswith("USDTM") and s not in bad_symbols]

# 2. Prepare data structures for each symbol
klines = {symbol: [] for symbol in symbols}
orderbooks = {symbol: {"bids": [], "asks": []} for symbol in symbols}

async def subscribe(ws, topic, token):
    sub_msg = {
        "id": str(datetime.now().timestamp()),
        "type": "subscribe",
        "topic": topic,
        "privateChannel": False,
        "response": True,
        "token": token
    }
    await ws.send(json.dumps(sub_msg))

def update_orderbook(orderbook, change):
    price, side, size = change.split(",")
    price = float(price)
    size = float(size)
    levels = orderbook["bids" if side == "buy" else "asks"]
    for i, (p, s) in enumerate(levels):
        if p == price:
            if size == 0:
                levels.pop(i)
            else:
                levels[i] = (price, size)
            break
    else:
        if size > 0:
            levels.append((price, size))
    if side == "buy":
        orderbook["bids"] = sorted(orderbook["bids"], key=lambda x: -x[0])
    else:
        orderbook["asks"] = sorted(orderbook["asks"], key=lambda x: x[0])

MAX_WORKERS = 5
BATCH_SIZE = max(1, len(symbols) // MAX_WORKERS)

async def ws_worker(batch):
    ws_url = f"{endpoint}?token={token}"
    while True:
        try:
            async with websockets.connect(ws_url, max_queue=None) as ws:
                for symbol in batch:
                    await subscribe(ws, f"/contractMarket/klineV2:1min:{symbol}", token)
                    await asyncio.sleep(0.1)  # Add a short delay
                    await subscribe(ws, f"/contractMarket/level2:{symbol}", token)
                    await asyncio.sleep(1)  # Between subscriptions
                print(f"Subscribed to {len(batch)} symbols in this worker.")

                async for msg in ws:
                    data = json.loads(msg)
                    topic = data.get("topic", "")
                    # --- KLINE HANDLING ---
                    if topic.startswith("/contractMarket/klineV2:1min:") and "data" in data:
                        symbol = topic.split(":")[-1]
                        kline = data["data"]
                        klines[symbol].append([
                            kline["time"], float(kline["open"]), float(kline["high"]),
                            float(kline["low"]), float(kline["close"]), float(kline["vol"])
                        ])
                        if len(klines[symbol]) > 100:
                            klines[symbol].pop(0)
                        if kline["isClosed"]:
                            df = pd.DataFrame(klines[symbol], columns=["timestamp","open","high","low","close","volume"])
                            rsi = compute_rsi(df["close"])
                            macd, macd_signal, _ = compute_macd(df["close"])
                            bb_upper, bb_lower = compute_bollinger(df["close"])
                            atr = compute_atr(df)
                            last_rsi = rsi.iloc[-1]
                            last_macd = macd.iloc[-1]
                            last_macd_signal = macd_signal.iloc[-1]
                            last_bb_upper = bb_upper.iloc[-1]
                            last_bb_lower = bb_lower.iloc[-1]
                            last_atr = atr.iloc[-1]
                            close = df["close"].iloc[-1]
                            # --- ORDERBOOK ANALYTICS ---
                            ob = orderbooks[symbol]
                            if ob["bids"] and ob["asks"]:
                                best_bid = ob["bids"][0][0]
                                best_ask = ob["asks"][0][0]
                                spread = best_ask - best_bid
                                signal = multi_factor_signal(
                                    last_rsi, last_macd, last_macd_signal, close,
                                    last_bb_upper, last_bb_lower, last_atr
                                )
                                print(f"{symbol} Kline closed: Signal={signal}, RSI={last_rsi:.2f}, MACD={last_macd:.4f}, Spread={spread:.2f}")
                                if signal in ("buy", "sell"):
                                    account_equity = fetch_account_equity()
                                    size = calculate_position_size(account_equity, 0.01, 0.02)
                                    response = place_order(symbol, signal, int(size))
                                    print(f"Placed {signal} order for {symbol}: {response}")
                    # --- ORDERBOOK HANDLING ---
                    elif topic.startswith("/contractMarket/level2:") and "data" in data:
                        symbol = topic.split(":")[-1]
                        change = data["data"]["change"]
                        update_orderbook(orderbooks[symbol], change)
        except Exception as e:
            print(f"Websocket error in batch {batch[0]}-{batch[-1]}: {e}, reconnecting in 5 seconds...")
            await asyncio.sleep(5)

async def main():
    tasks = []
    for i in range(0, len(symbols), BATCH_SIZE):
        batch = symbols[i:i+BATCH_SIZE]
        if len(tasks) >= MAX_WORKERS:
            break
        tasks.append(asyncio.create_task(ws_worker(batch)))
        await asyncio.sleep(10)  # Longer delay between workers
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())