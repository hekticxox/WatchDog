from data.kucoin_data import fetch_klines_rest

def fetch_klines_with_fallback(symbol, start, end):
    data = fetch_klines_rest(symbol, start, end)
    if data and len(data) >= 20:
        return data
    binance_symbol = symbol.replace("USDTM", "USDT")
    try:
        from fetch_binance_klines import fetch_binance_klines
        data = fetch_binance_klines(binance_symbol, interval="1m", start_time=start, end_time=end, limit=500)
        if data and len(data) >= 20:
            formatted = [
                [
                    int(row[0]),
                    float(row[1]),
                    float(row[2]),
                    float(row[3]),
                    float(row[4]),
                    float(row[5])
                ]
                for row in data
            ]
            print(f"Fetched {len(formatted)} klines for {symbol} from Binance as fallback.")
            return formatted
    except Exception as e:
        print(f"Binance fallback failed for {symbol}: {e}")
    print(f"Could not get enough price data for {symbol} from any source.")
    return None