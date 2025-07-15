import os
import requests
import time
import hmac
import base64
import math  # <-- Add this line
from dotenv import load_dotenv
import asyncio
from textual.app import App, ComposeResult # type: ignore # type: ignore
from textual.containers import Horizontal, Vertical # type: ignore
from textual.widgets import Static # type: ignore
from textual.reactive import reactive # type: ignore
import pandas as pd
from indicators.rsi import compute_rsi
from indicators.macd import compute_macd
from data.kucoin_data import fetch_klines_rest
from strategies.multi_factor import multi_factor_signal  # Add this import at the top

load_dotenv()
API_KEY = os.getenv("KUCOIN_API_KEY")
API_SECRET = os.getenv("KUCOIN_API_SECRET")
API_PASSPHRASE = os.getenv("KUCOIN_API_PASSPHRASE")
BASE_URL = "https://api-futures.kucoin.com"

def _kucoin_sign(method, endpoint, params=""):
    now = int(time.time() * 1000)
    str_to_sign = f"{now}{method}{endpoint}{params}"
    signature = base64.b64encode(
        hmac.new(API_SECRET.encode(), str_to_sign.encode(), digestmod="sha256").digest()
    ).decode()
    passphrase = base64.b64encode(
        hmac.new(API_SECRET.encode(), API_PASSPHRASE.encode(), digestmod="sha256").digest()
    ).decode()
    return now, signature, passphrase

# --- You must implement this function using your KuCoin API wrapper ---
def fetch_open_positions_kucoin():
    endpoint = "/api/v1/positions"
    url = BASE_URL + endpoint
    now, signature, passphrase = _kucoin_sign("GET", endpoint)
    headers = {
        "KC-API-KEY": API_KEY,
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json",
    }
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
                contract_size = CONTRACT_SIZES.get(symbol, 1)
                print(f"DEBUG: {symbol} qty={qty}, contract_size={contract_size}")  # <--- Add this line
                side = "buy" if qty > 0 else "sell"
                size = abs(qty) * contract_size
                entry = pos.get("avgEntryPrice", "-")
                pnl = float(pos.get("unrealisedPnl", 0))
                result[symbol] = {
                    "side": side,
                    "size": size,
                    "entry": entry,
                    "pnl": pnl
                }
        return result
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return {}

def fetch_contract_sizes():
    endpoint = "/api/v1/contracts/active"
    url = BASE_URL + endpoint
    now, signature, passphrase = _kucoin_sign("GET", endpoint)
    headers = {
        "KC-API-KEY": API_KEY,
        "KC-API-SIGN": signature,
        "KC-API-TIMESTAMP": str(now),
        "KC-API-PASSPHRASE": passphrase,
        "KC-API-KEY-VERSION": "2",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        sizes = {}
        if data.get("code") == "200000":
            for contract in data["data"]:
                print("DEBUG contract keys:", contract.keys())
                # Use 'multiplier' as the contract size
                sizes[contract["symbol"]] = float(contract["multiplier"])
        return sizes
    except Exception as e:
        print(f"Error fetching contract sizes: {e}")
        return {}

CONTRACT_SIZES = fetch_contract_sizes()
print("DEBUG: CONTRACT_SIZES loaded:", CONTRACT_SIZES)

class PositionBox(Static):
    def __init__(self, symbol, side, position_size, entry, pnl, rsi=None, macd=None, suggestion=None, s1=None, r1=None, points=None, total_points=None, point_details=None):
        super().__init__()
        self.symbol = symbol
        self.side = side
        self.position_size = position_size
        self.entry = entry
        self.pnl = pnl
        self.rsi = rsi
        self.macd = macd
        self.suggestion = suggestion
        self.s1 = s1
        self.r1 = r1
        self.points = points
        self.total_points = total_points
        self.point_details = point_details

    def render(self):
        # Use suggestion for color, not side
        color = {
            "buy": "green",
            "sell": "red",
            "hold": "yellow"
        }.get((self.suggestion or "").lower(), "white")
        pnl_str = f"{self.pnl:.2%}" if isinstance(self.pnl, float) else str(self.pnl)
        rsi_str = f"{self.rsi:.2f}" if self.rsi is not None else "-"
        macd_str = f"{self.macd:.4f}" if self.macd is not None else "-"
        suggestion_str = self.suggestion.upper() if self.suggestion else "-"
        extra_line = ""
        if suggestion_str == "BUY" and self.s1 is not None:
            extra_line = f"S1: {self.s1:.5f}"
        elif suggestion_str == "SELL" and self.r1 is not None:
            extra_line = f"R1: {self.r1:.5f}"
        score_line = ""
        if self.points is not None and self.total_points is not None:
            score_line = f"Score: {self.points}/{self.total_points} [{self.point_details}]"
        return (
            f"[b]{self.symbol}[/b]\n"
            f"[{color}]{suggestion_str}[/{color}]\n"
            f"Size: {self.position_size}\n"
            f"Entry: {self.entry}\n"
            f"PnL: {pnl_str}\n"
            f"RSI: {rsi_str}\n"
            f"MACD: {macd_str}\n"
            f"Suggestion: [{color}]{suggestion_str}[/{color}]\n"
            f"{extra_line}\n"
            f"{score_line}"
        )

class TopCandidatesBox(Static):
    def __init__(self, top_candidates):
        super().__init__()
        self.top_candidates = list(top_candidates)

    def render(self):
        if not self.top_candidates:
            return "[b]Top 5 Candidates:[/b]\nNo candidates found."
        lines = [f"[b]Top 5 Candidates:[/b]"]
        positions = getattr(self.app, "positions", {})
        for i, symbol in enumerate(self.top_candidates[:5], 1):
            pos = positions.get(symbol) if positions else None
            if pos and pos.get("points") is not None:
                score = pos.get("points", "-")
                total = pos.get("total_points", "-")
                suggestion = pos.get("suggestion", "-")
                details = pos.get("point_details", "")
                lines.append(f"{i}. {symbol} | Score: {score}/{total} | Signal: {suggestion} | {details}")
            else:
                # If not in open positions, fetch latest data and calculate score
                try:
                    end = int(time.time() * 1000)
                    start = end - 60 * 60 * 1000  # last 1 hour
                    data = fetch_klines_with_fallback(symbol, start, end)
                    if data and len(data) > 50:
                        df = pd.DataFrame(data, columns=["timestamp","open","high","low","close","volume"])
                        df["close"] = df["close"].astype(float)
                        points, total_points, point_details = calculate_signal_points(df)
                        # Add dashboard point if in top candidates
                        points += 1
                        total_points += 1
                        if point_details:
                            point_details += ",DashboardTop"
                        else:
                            point_details = "DashboardTop"
                        # Optionally, you can also run your multi_factor_signal here for suggestion
                        rsi = compute_rsi(df["close"])
                        macd, macd_signal, _ = compute_macd(df["close"])
                        last_rsi = float(rsi.iloc[-1])
                        last_macd = float(macd.iloc[-1])
                        last_macd_signal = float(macd_signal.iloc[-1])
                        last_close = float(df["close"].iloc[-1])
                        suggestion = multi_factor_signal(
                            last_rsi, last_macd, last_macd_signal, last_close,
                            0, 0, 0, 0, 0, 0
                        )
                        suggestion = (suggestion or "-").lower()
                        lines.append(f"{i}. {symbol} | Score: {points}/{total_points} | Signal: {suggestion} | {point_details}")
                    else:
                        lines.append(f"{i}. {symbol} | No data")
                except Exception as e:
                    lines.append(f"{i}. {symbol} | Error: {e}")
        return "\n".join(lines)

class PositionsDashboard(App):
    CSS_PATH = None
    BINDINGS = [("q", "quit", "Quit")]

    positions = reactive({})

    async def on_mount(self):
        await self.refresh_positions()
        self.set_interval(2, self.refresh_positions)

    async def refresh_positions(self):
        positions = fetch_open_positions_kucoin()
        top_candidates = get_top_candidates()
        for symbol in positions:
            end = int(time.time() * 1000)
            start = end - 60 * 60 * 1000  # last 1 hour
            data = fetch_klines_with_fallback(symbol, start, end)
            if data and len(data) > 50:
                df = pd.DataFrame(data, columns=["timestamp","open","high","low","close","volume"])
                df["close"] = df["close"].astype(float)
                rsi = compute_rsi(df["close"])
                macd, macd_signal, macd_diff = compute_macd(df["close"])
                last_rsi = float(rsi.iloc[-1])
                last_macd = float(macd.iloc[-1])
                if math.isnan(last_rsi):
                    last_rsi = None
                if math.isnan(last_macd):
                    last_macd = None
                print(f"DEBUG {symbol}: RSI={last_rsi}, MACD={last_macd}")
                positions[symbol]["rsi"] = last_rsi
                positions[symbol]["macd"] = last_macd
                # --- Suggestion logic ---
                # Add other indicators as needed, or use defaults if not available
                last_macd_signal = float(macd_signal.iloc[-1])
                last_close = float(df["close"].iloc[-1])
                # You may want to add more indicators here if your multi_factor_signal needs them
                suggestion = multi_factor_signal(
                    last_rsi, last_macd, last_macd_signal, last_close,
                    0, 0, 0, 0, 0, 0  # Fill with zeros or real values if available
                )
                # Normalize suggestion to lower-case and restrict to allowed values
                suggestion = (suggestion or "").lower()
                if suggestion not in ("buy", "sell", "hold"):
                    suggestion = "hold"
                positions[symbol]["suggestion"] = suggestion

                # --- Calculate S1/R1 (example: pivot points, here just using min/max of last 20 bars) ---
                s1 = df["low"].tail(20).min()
                r1 = df["high"].tail(20).max()
                positions[symbol]["s1"] = s1
                positions[symbol]["r1"] = r1

                # --- Calculate signal points ---
                points, total_points, point_details = calculate_signal_points(df)
                positions[symbol]["points"] = points
                positions[symbol]["total_points"] = total_points
                positions[symbol]["point_details"] = ",".join(point_details)

                # Require at least 3 points for a "buy" or "sell" to be considered
                if suggestion in ("buy", "sell") and points < 3:
                    suggestion = "hold"
                positions[symbol]["suggestion"] = suggestion

                # --- Add to top candidates if applicable ---
                if symbol in top_candidates:
                    positions[symbol]["points"] = positions[symbol].get("points", 0) + 1
                    if positions[symbol].get("point_details"):
                        positions[symbol]["point_details"] += ",DashboardTop"
                    else:
                        positions[symbol]["point_details"] = "DashboardTop"
                    positions[symbol]["total_points"] = positions[symbol].get("total_points", 0) + 1
            else:
                positions[symbol]["rsi"] = None
                positions[symbol]["macd"] = None
                positions[symbol]["suggestion"] = None
                positions[symbol]["s1"] = None
                positions[symbol]["r1"] = None
                positions[symbol]["points"] = 0
                positions[symbol]["total_points"] = 0
                positions[symbol]["point_details"] = ""
        self.positions = positions

    def compose(self) -> ComposeResult:
        self.top_container = Vertical()
        self.positions_container = Vertical()
        # Top picks at the top
        top_candidates = list(get_top_candidates())
        yield Static("[b]Top Picks[/b]", classes="section-title")
        yield TopCandidatesBox(top_candidates)
        yield Static("[b]Current Positions[/b]", classes="section-title")
        yield self.positions_container

    def watch_positions(self, positions):
        self.positions_container.remove_children()
        def sort_key(item):
            symbol, pos = item
            signal = (pos.get("suggestion") or "").lower()
            rsi = pos.get("rsi", float("inf"))
            prox_support = pos.get("prox_support", float("inf"))
            prox_resist = pos.get("prox_resist", float("inf"))
            if signal == "buy":
                return (0, rsi, prox_support)
            elif signal == "sell":
                return (1, -rsi, prox_resist)
            else:
                return (2, float("inf"), float("inf"))

        sorted_positions = sorted(positions.items(), key=sort_key)
        boxes = []
        for symbol, pos in sorted_positions:
            boxes.append(PositionBox(
                symbol, pos["side"], pos["size"], pos["entry"], pos["pnl"],
                rsi=pos.get("rsi"), macd=pos.get("macd"), suggestion=pos.get("suggestion"),
                s1=pos.get("s1"), r1=pos.get("r1"),
                points=pos.get("points"), total_points=pos.get("total_points"), point_details=pos.get("point_details")
            ))
        for box in boxes:
            self.positions_container.mount(box)

# --- Add this function near the top (after your imports) ---
def get_top_candidates():
    try:
        with open("top_candidates.txt") as f:
            return set(line.strip() for line in f if line.strip())
    except Exception:
        return set()

# Add this function near the top (after your imports)
def fetch_klines_with_fallback(symbol, start, end, interval="1m"):
    # Try KuCoin first
    data = fetch_klines_rest(symbol, start, end)
    if data and len(data) > 50:
        return data
    # Fallback to Binance
    binance_symbol = symbol.replace("USDTM", "USDT")  # Adjust if needed
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={binance_symbol}&interval=1m&limit=1000"
    try:
        resp = requests.get(url, timeout=10)
        klines = resp.json()
        # Format: [open_time, open, high, low, close, volume, ...]
        return [
            [k[0], float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])]
            for k in klines
        ]
    except Exception as e:
        print(f"Binance fallback failed for {symbol}: {e}")
        return []

def calculate_signal_points(df, last_idx=None):
    """Returns (points, total_points, details) for the latest bar in df."""
    if last_idx is None:
        last_idx = -1
    points = 0
    total = 0
    details = []

    # 1. Volume Spike
    vol_spike = df["volume"].iloc[last_idx] > (df["volume"].rolling(20).mean().iloc[last_idx] * 2)
    total += 1
    if vol_spike:
        points += 1
        details.append("VolSpike")

    # 2. Breakout
    recent_high = df["high"].rolling(20).max().iloc[last_idx-1]
    recent_low = df["low"].rolling(20).min().iloc[last_idx-1]
    close = df["close"].iloc[last_idx]
    breakout_long = close > recent_high
    breakout_short = close < recent_low
    total += 1
    if breakout_long or breakout_short:
        points += 1
        details.append("Breakout")

    # 3. MA Confluence
    ema21 = df["close"].ewm(span=21).mean().iloc[last_idx]
    sma50 = df["close"].rolling(50).mean().iloc[last_idx]
    ma_long = close > ema21 and close > sma50
    ma_short = close < ema21 and close < sma50
    total += 1
    if ma_long or ma_short:
        points += 1
        details.append("MA")

    # 4. MACD Cross
    macd, macd_signal, _ = compute_macd(df["close"])
    macd_cross_long = macd.iloc[last_idx-1] < macd_signal.iloc[last_idx-1] and macd.iloc[last_idx] > macd_signal.iloc[last_idx]
    macd_cross_short = macd.iloc[last_idx-1] > macd_signal.iloc[last_idx-1] and macd.iloc[last_idx] < macd_signal.iloc[last_idx]
    total += 1
    if macd_cross_long or macd_cross_short:
        points += 1
        details.append("MACDcross")

    # 5. RSI Reversal
    rsi = compute_rsi(df["close"])
    rsi_long = rsi.iloc[last_idx-1] < 30 and rsi.iloc[last_idx] > 30
    rsi_short = rsi.iloc[last_idx-1] > 70 and rsi.iloc[last_idx] < 70
    total += 1
    if rsi_long or rsi_short:
        points += 1
        details.append("RSIrev")

    # 6. Funding Rate Extreme (if available)
    if "FundingRate" in df.columns:
        funding = df["FundingRate"].iloc[last_idx]
        total += 1
        if abs(funding) > 0.001:
            points += 1
            details.append("Funding")

    # 7. Orderbook Imbalance (if available)
    if "Imbalance" in df.columns:
        imb = df["Imbalance"].iloc[last_idx]
        total += 1
        if abs(imb) > 0.2:
            points += 1
            details.append("OBImb")

    return points, total, details

def format_top_candidates_for_message_and_file(top_candidates, positions):
    """
    Returns a string with detailed info for top candidates, suitable for Telegram and for writing to a file.
    """
    lines = ["Top 5 Candidates:"]
    for i, symbol in enumerate(top_candidates[:5], 1):
        pos = positions.get(symbol) if positions else None
        if pos and pos.get("points") is not None:
            score = pos.get("points", "-")
            total = pos.get("total_points", "-")
            suggestion = pos.get("suggestion", "-")
            details = pos.get("point_details", "")
            lines.append(f"{i}. {symbol} | Score: {score}/{total} | Signal: {suggestion} | {details}")
        else:
            # Fallback: fetch and calculate as in TopCandidatesBox.render()
            try:
                end = int(time.time() * 1000)
                start = end - 60 * 60 * 1000  # last 1 hour
                data = fetch_klines_with_fallback(symbol, start, end)
                if data and len(data) > 50:
                    df = pd.DataFrame(data, columns=["timestamp","open","high","low","close","volume"])
                    df["close"] = df["close"].astype(float)
                    points, total_points, point_details = calculate_signal_points(df)
                    points += 1
                    total_points += 1
                    if point_details:
                        point_details += ",DashboardTop"
                    else:
                        point_details = "DashboardTop"
                    rsi = compute_rsi(df["close"])
                    macd, macd_signal, _ = compute_macd(df["close"])
                    last_rsi = float(rsi.iloc[-1])
                    last_macd = float(macd.iloc[-1])
                    last_macd_signal = float(macd_signal.iloc[-1])
                    last_close = float(df["close"].iloc[-1])
                    suggestion = multi_factor_signal(
                        last_rsi, last_macd, last_macd_signal, last_close,
                        0, 0, 0, 0, 0, 0
                    )
                    suggestion = (suggestion or "-").lower()
                    lines.append(f"{i}. {symbol} | Score: {points}/{total_points} | Signal: {suggestion} | {point_details}")
                else:
                    lines.append(f"{i}. {symbol} | No data")
            except Exception as e:
                lines.append(f"{i}. {symbol} | Error: {e}")
    return "\n".join(lines)

if __name__ == "__main__":
    PositionsDashboard().run()