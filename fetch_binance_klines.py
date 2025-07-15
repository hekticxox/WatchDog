import requests
import pandas as pd
import time

def fetch_binance_klines(symbol, interval="1m", start_time=None, end_time=None, limit=500):
    """
    Fetch klines from Binance Futures.
    symbol: e.g. "BTCUSDT"
    interval: e.g. "1m"
    start_time, end_time: ms timestamps
    limit: max 1500
    """
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
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

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
        df = fetch_binance_klines(symbol, interval, start, end)
        all_dfs.append(df)
        time.sleep(1)  # avoid rate limits
    result = pd.concat(all_dfs).drop_duplicates()
    result.to_csv("historical_prices.csv", index=False)
    print("Saved to historical_prices.csv")