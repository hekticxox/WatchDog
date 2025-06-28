import requests
import pandas as pd
import time

def fetch_binance_klines(symbol, interval="1m", limit=1000, start_time=None, end_time=None):
    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    if start_time:
        params["startTime"] = int(start_time)
    if end_time:
        params["endTime"] = int(end_time)
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    # Columns: open_time, open, high, low, close, volume, close_time, ...
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])
    df["symbol"] = symbol
    df["close"] = df["close"].astype(float)
    return df[["timestamp", "symbol", "close"]]

if __name__ == "__main__":
    # Example: Download 1-minute klines for BTCUSDT for the last 2 days
    symbol = "BTCUSDT"
    interval = "1m"
    now = int(time.time() * 1000)
    one_day_ms = 24 * 60 * 60 * 1000
    all_dfs = []
    for i in range(2):  # 2 days
        start = now - (i + 1) * one_day_ms
        end = now - i * one_day_ms
        df = fetch_binance_klines(symbol, interval, 1000, start, end)
        all_dfs.append(df)
        time.sleep(1)  # avoid rate limits
    result = pd.concat(all_dfs).drop_duplicates()
    result.to_csv("historical_prices.csv", index=False)
    print("Saved to historical_prices.csv")