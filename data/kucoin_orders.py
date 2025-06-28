import os
import requests
import time
import base64
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("KUCOIN_API_KEY")
API_SECRET = os.getenv("KUCOIN_API_SECRET")
API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")
BASE_URL = "https://api-futures.kucoin.com"

def _get_headers(endpoint, method, body=""):
    now = int(time.time() * 1000)
    str_to_sign = f"{now}{method}{endpoint}{body}"
    signature = base64.b64encode(
        hmac.new(API_SECRET.encode(), str_to_sign.encode(), hashlib.sha256).digest()
    ).decode()
    passphrase = base64.b64encode(
        hmac.new(API_SECRET.encode(), API_PASSPHRASE.encode(), hashlib.sha256).digest()
    ).decode()
    return {
        "KC-API-KEY": API_KEY,
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json"
    }

def place_order(symbol, side, size, client_oid=None, leverage=5, order_type="market"):
    if client_oid is None:
        import uuid
        client_oid = str(uuid.uuid4())
    endpoint = "/api/v1/orders"
    url = BASE_URL + endpoint
    payload = {
        "clientOid": client_oid,
        "symbol": symbol,
        "side": side,
        "leverage": leverage,
        "size": size,
        "type": order_type,  # "market" or "limit"
    }
    # Do NOT include "price" for market orders
    import json
    body_json = json.dumps(payload)
    headers = _get_headers(endpoint, "POST", body_json)
    resp = requests.post(url, headers=headers, data=body_json)
    try:
        return resp.json()
    except Exception:
        return {"error": "Invalid response", "content": resp.content}

def calculate_position_size(account_equity, risk_per_trade, stop_loss_pct):
    """
    account_equity: total account value (USDT)
    risk_per_trade: fraction of equity to risk (e.g., 0.01 for 1%)
    stop_loss_pct: stop loss as a fraction (e.g., 0.02 for 2%)
    """
    risk_amount = account_equity * risk_per_trade
    position_size = risk_amount / stop_loss_pct
    return position_size

def close_position(symbol, side, size, client_oid=None, leverage=5, order_type="market"):
    # For KuCoin Futures, to close a position, you place an order in the opposite direction
    close_side = "sell" if side == "buy" else "buy"
    return place_order(
        symbol, close_side, size,
        client_oid=client_oid,
        leverage=leverage,
        order_type=order_type
    )