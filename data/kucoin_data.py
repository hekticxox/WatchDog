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

def fetch_account_equity(currency="USDT"):
    endpoint = f"/api/v1/account-overview?currency={currency}"
    url = BASE_URL + endpoint
    headers = _get_headers(endpoint, "GET")
    resp = requests.get(url, headers=headers)
    data = resp.json()
    if data["code"] == "200000":
        return float(data["data"]["accountEquity"])
    else:
        print(f"Error fetching account equity: {data}")
        return None

def fetch_contract_detail(symbol):
    url = f"https://api-futures.kucoin.com/api/v1/contracts/{symbol}"
    resp = requests.get(url)
    data = resp.json()
    if data["code"] == "200000":
        return data["data"]
    else:
        print(f"Error fetching contract detail for {symbol}: {data}")
        return None

def fetch_funding_rate(symbol):
    contract = fetch_contract_detail(symbol)
    if contract:
        return contract.get("fundingFeeRate")
    return None

def fetch_open_interest(symbol):
    contract = fetch_contract_detail(symbol)
    if contract:
        return contract.get("openInterest")
    return None

def fetch_klines_rest(symbol, start, end, interval="1min"):
    url = f"https://api-futures.kucoin.com/api/v1/kline/query"
    params = {
        "symbol": symbol,
        "granularity": 1,  # 1 minute
        "from": int(start),  # keep as milliseconds
        "to": int(end)       # keep as milliseconds
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if data["code"] == "200000":
        return data["data"]
    else:
        print(f"Error fetching klines for {symbol}: {data}")
        return None

def fetch_active_symbols():
    url = "https://api-futures.kucoin.com/api/v1/contracts/active"
    resp = requests.get(url)
    data = resp.json()
    if data["code"] == "200000":
        return [item["symbol"] for item in data["data"]]
    else:
        print("Error fetching active symbols:", data)
        return []