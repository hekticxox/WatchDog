import os
import requests
import time
import base64
import hmac
import hashlib
from dotenv import load_dotenv
import uuid

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

def place_order(symbol, side, size, order_type="market", price=None, leverage=1, client_oid=None):
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
    if order_type == "limit" and price is not None:
        payload["price"] = price
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

def execute_grid_trade(symbol, account_equity, risk_per_trade, stop_loss_pct, grid_level=3, leverage=5):
    """
    symbol: trading pair symbol, e.g., 'BTC-USDT'
    account_equity: total account value (USDT)
    risk_per_trade: fraction of equity to risk (e.g., 0.01 for 1%)
    stop_loss_pct: stop loss as a fraction (e.g., 0.02 for 2%)
    grid_level: number of grid levels
    leverage: leverage for the trade
    """
    # Calculate position size based on account equity and risk parameters
    position_size = calculate_position_size(account_equity, risk_per_trade, stop_loss_pct)

    # Define grid parameters
    grid_spacing = 10  # USDT
    buy_price = None
    sell_price = None

    # Place grid buy orders
    for i in range(grid_level):
        if buy_price is None:
            buy_price = round(position_size * grid_spacing, 2)
        else:
            buy_price += grid_spacing
        grid_place_order(symbol, "buy", buy_price, position_size, leverage)

    # Place grid sell orders
    for i in range(grid_level):
        if sell_price is None:
            sell_price = round(position_size * grid_spacing, 2)
        else:
            sell_price += grid_spacing
        grid_place_order(symbol, "sell", sell_price, position_size, leverage)

def grid_place_order(symbol, side, price, size, leverage=5):
    """
    Places a grid limit order on KuCoin Futures.
    """
    client_oid = str(uuid.uuid4())
    resp = place_order(
        symbol, side, size,
        order_type="limit",
        price=price,
        leverage=leverage,
        client_oid=client_oid
    )
    print(f"[GRID] Placed {side.upper()} order @ {price} for {size} {symbol}. Response: {resp}")
    return resp