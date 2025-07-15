# utils.py
from data.kucoin_data import fetch_klines_rest
from data.kucoin_orders import close_position
import requests
import os
import json
import time
import base64
import hmac

BASE_URL = "https://api-futures.kucoin.com"

def fetch_klines_with_fallback(symbol, start, end):
    data = fetch_klines_rest(symbol, start, end)
    if data and len(data) >= 20:
        return data
    # Fallback: try Binance (convert symbol if needed)
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

def fetch_open_positions_full():
    """
    Fetch open positions with full info for dashboard/trailing stop.
    """
    # You may need to update _get_headers or import it here if needed
    endpoint = "/api/v1/positions"
    url = BASE_URL + endpoint
    # You may need to move _get_headers to utils.py as well if it's used here
    from dotenv import load_dotenv
    load_dotenv()
    API_KEY = os.getenv("KUCOIN_API_KEY")
    API_SECRET = os.getenv("KUCOIN_API_SECRET")
    API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")
    def _get_headers(endpoint, method, body=""):
        if API_KEY is None:
            raise ValueError("KUCOIN_API_KEY environment variable is not set.")
        if API_SECRET is None:
            raise ValueError("KUCOIN_API_SECRET environment variable is not set.")
        if isinstance(body, dict):
            body = json.dumps(body)
        now = str(int(time.time() * 1000))
        str_to_sign = f"{now}{method}{endpoint}{body}"
        signature = base64.b64encode(
            hmac.new(API_SECRET.encode(), str_to_sign.encode(), digestmod="sha256").digest()
        ).decode()
        if API_PASSPHRASE is None:
            raise ValueError("KUCOIN_API_PASSPHRASE environment variable is not set.")
        passphrase = base64.b64encode(
            hmac.new(API_SECRET.encode(), API_PASSPHRASE.encode(), digestmod="sha256").digest()
        ).decode()
        return {
            "KC-API-TIMESTAMP": now,
            "KC-API-KEY": API_KEY,
            "KC-API-SIGN": signature,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "2",
            "Content-Type": "application/json"
        }
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