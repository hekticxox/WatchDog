import requests
import numpy as np

def fetch_orderbook(symbol):
    url = f"https://api-futures.kucoin.com/api/v1/level2/snapshot"
    params = {"symbol": symbol}
    resp = requests.get(url, params=params)
    data = resp.json()
    if data["code"] == "200000":
        return data["data"]
    else:
        print(f"Error fetching orderbook for {symbol}: {data}")
        return None

def orderbook_imbalance(orderbook):
    # Convert bids/asks to numpy arrays of floats
    bids = np.array([[float(price), float(size)] for price, size in orderbook["bids"]])
    asks = np.array([[float(price), float(size)] for price, size in orderbook["asks"]])
    bid_vol = bids[:,1].sum() if bids.size else 0
    ask_vol = asks[:,1].sum() if asks.size else 0
    return (bid_vol - ask_vol) / (bid_vol + ask_vol + 1e-9) if (bid_vol + ask_vol) > 0 else 0

def volume_profile(orderbook, bins=10):
    bids = np.array([[float(price), float(size)] for price, size in orderbook["bids"]])
    asks = np.array([[float(price), float(size)] for price, size in orderbook["asks"]])
    prices = np.concatenate([bids[:,0], asks[:,0]]) if bids.size and asks.size else np.array([])
    volumes = np.concatenate([bids[:,1], asks[:,1]]) if bids.size and asks.size else np.array([])
    if prices.size and volumes.size:
        hist, bin_edges = np.histogram(prices, bins=bins, weights=volumes)
        return hist, bin_edges
    else:
        return np.array([]), np.array([])

def orderbook_spread(orderbook):
    best_bid = float(orderbook["bids"][0][0]) if orderbook["bids"] else None
    best_ask = float(orderbook["asks"][0][0]) if orderbook["asks"] else None
    if best_bid is not None and best_ask is not None:
        return best_ask - best_bid
    return None

def largest_wall(orderbook, side="bids"):
    levels = orderbook[side]
    if not levels:
        return None, None
    arr = np.array([[float(price), float(size)] for price, size in levels])
    idx = np.argmax(arr[:,1])
    return arr[idx,0], arr[idx,1]  # price, size

def cumulative_depth(orderbook, pct=0.1):
    # pct is percent (e.g., 0.1 for 0.1%)
    if not orderbook["bids"] or not orderbook["asks"]:
        return 0, 0
    best_bid = float(orderbook["bids"][0][0])
    best_ask = float(orderbook["asks"][0][0])
    mid = (best_bid + best_ask) / 2
    lower = mid * (1 - pct/100)
    upper = mid * (1 + pct/100)
    bids = np.array([[float(price), float(size)] for price, size in orderbook["bids"] if float(price) >= lower])
    asks = np.array([[float(price), float(size)] for price, size in orderbook["asks"] if float(price) <= upper])
    bid_liquidity = bids[:,1].sum() if bids.size else 0
    ask_liquidity = asks[:,1].sum() if asks.size else 0
    return bid_liquidity, ask_liquidity

def orderbook_slope(orderbook, side="bids", levels=10):
    arr = np.array([[float(price), float(size)] for price, size in orderbook[side][:levels]])
    if arr.shape[0] < 2:
        return 0
    prices = arr[:,0]
    volumes = arr[:,1].cumsum()
    # Linear fit: slope of cumulative volume vs price
    slope = np.polyfit(prices, volumes, 1)[0]
    return slope