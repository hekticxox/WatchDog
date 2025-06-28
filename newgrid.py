# kucoin_ai_grid_bot.py with trailing SL/TP and AI volatility grid

import time
import hmac
import hashlib
import requests
import uuid
import json
from datetime import datetime
import statistics

# === CONFIG ===
CONFIG = {
    "api_key": "YOUR_KUCOIN_API_KEY",
    "api_secret": "YOUR_KUCOIN_API_SECRET",
    "api_passphrase": "YOUR_API_PASSPHRASE",
    "symbol": "BTCUSDTM",
    "leverage": 5,
    "grid_levels": 10,
    "base_order_size": 10,
    "margin_mode": "isolated",
    "trailing_stop_percent": 0.5,
    "enable_take_profit": True,
    "take_profit_percent": 2,
    "check_interval": 10,
    "volatility_window": 10  # Number of price samples to calculate volatility
}

KUCOIN_BASE_URL = "https://api-futures.kucoin.com"
price_history = []

# === AUTH ===
def generate_signature(endpoint, method="GET", body=""):
    now = int(time.time() * 1000)
    str_to_sign = f"{now}{method}{endpoint}{body}"
    signature = hmac.new(CONFIG['api_secret'].encode(), str_to_sign.encode(), hashlib.sha256).hexdigest()
    return now, signature

def kucoin_request(method, endpoint, data=None):
    if data is None:
        data = ""
    elif isinstance(data, dict):
        data = json.dumps(data)
    
    now, sig = generate_signature(endpoint, method, data)
    headers = {
        "KC-API-SIGN": sig,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-KEY": CONFIG["api_key"],
        "KC-API-PASSPHRASE": CONFIG["api_passphrase"],
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json"
    }

    url = f"{KUCOIN_BASE_URL}{endpoint}"
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, data=data)
    else:
        raise Exception("Unsupported HTTP method")

    return response.json()

# === MARKET DATA ===
def fetch_market_price():
    r = requests.get(f"{KUCOIN_BASE_URL}/api/v1/mark-price/{CONFIG['symbol']}/current")
    price = float(r.json()['data']['value'])
    price_history.append(price)
    if len(price_history) > CONFIG['volatility_window']:
        price_history.pop(0)
    return price

def estimate_volatility():
    if len(price_history) < 2:
        return 0.005  # default spacing 0.5%
    stddev = statistics.stdev(price_history)
    avg_price = statistics.mean(price_history)
    return stddev / avg_price

# === ORDERS ===
def place_order(side, price, size):
    endpoint = "/api/v1/orders"
    order = {
        "clientOid": str(uuid.uuid4()),
        "symbol": CONFIG['symbol'],
        "side": side,
        "price": str(price),
        "size": str(size),
        "leverage": CONFIG['leverage'],
        "type": "limit",
        "reduceOnly": False
    }
    return kucoin_request("POST", endpoint, order)

def place_trailing_stop(side, entry_price):
    endpoint = "/api/v1/orders"
    offset = CONFIG['trailing_stop_percent'] / 100 * entry_price
    trigger_price = entry_price + offset if side == "buy" else entry_price - offset
    order = {
        "clientOid": str(uuid.uuid4()),
        "symbol": CONFIG['symbol'],
        "side": "sell" if side == "buy" else "buy",
        "type": "trailingStop",
        "triggerPrice": str(trigger_price),
        "triggerType": "last",
        "stop": "entry",
        "size": str(CONFIG['base_order_size'] / entry_price),
        "reduceOnly": True
    }
    print(f"[TRAILING STOP] {side} entry, placing order: {order}")