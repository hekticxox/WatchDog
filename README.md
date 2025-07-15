# FuturesGridBot

**FuturesGridBot** is an advanced cryptocurrency trading bot for KuCoin Futures, featuring:

- Automated signal scanning and trade execution
- Dynamic trailing stop-loss management
- Multi-factor technical analysis (RSI, MACD, Bollinger Bands, ATR, Stochastic, VWAP, etc.)
- Real-time and historical data support (KuCoin REST, WebSocket, Binance fallback)
- Telegram notifications
- Interactive dashboards (terminal and Textual UI)
- Position and risk management

---

## Folder Structure

```
FuturesGridBot/
│
├── bot_main.py              # Main entry point for trading, monitoring, and trailing stop
├── dashboard.py             # Terminal dashboard (DataTable, signal log)
├── dashboard2.py            # Advanced dashboard (Textual UI, top picks, positions)
├── newgrid.py               # Alternative grid bot with AI/volatility logic
├── realtime_ws_trading.py   # Real-time trading via KuCoin WebSocket
├── analyze_signals.py       # Signal analysis and labeling
├── telegram_notify.py       # Telegram notification integration
├── fetch_binance_klines.py  # Binance kline fallback fetcher
├── get_kucoin_ws_token.py   # KuCoin WebSocket token utility
├── requirements.txt         # Python dependencies
├── .env                     # API keys and secrets (not tracked)
├── top_candidates.txt       # Top 5 buy candidates (auto-updated)
├── bad_symbols.txt          # Symbols to avoid (auto-updated)
├── signal_log.csv           # Signal log (raw)
├── signal_log_labeled.csv   # Signal log (labeled)
├── historical_prices.csv    # Historical price data
│
├── data/
│   ├── kucoin_data.py       # KuCoin REST data functions
│   ├── kucoin_orders.py     # KuCoin order/position functions
│   ├── orderbook.py         # Orderbook utilities
│   ├── risk.py              # Position sizing, risk management
│   └── __init__.py
│
├── indicators/
│   ├── macd.py, rsi.py, ... # Technical indicator implementations
│   └── __init__.py
│
├── strategies/
│   ├── multi_factor.py      # Multi-factor signal logic
│   └── ...
│
└── __pycache__/
```

---

## How to Use

### 1. **Setup**

- Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```
- Copy `.env.example` to `.env` and fill in your KuCoin API keys and Telegram credentials.

### 2. **Run the Bot**

- **Trade & Monitor:**  
  ```sh
  python bot_main.py
  ```
  Select mode 1 for full trading, 2 for monitor-only, or 3 for trailing stop management.

- **Dashboards:**  
  ```sh
  python dashboard.py      # Table view
  python dashboard2.py     # Textual UI with top picks and positions
  ```

- **Real-time Trading (WebSocket):**  
  ```sh
  python realtime_ws_trading.py
  ```

### 3. **Telegram Alerts**

- Set `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` in your `.env` file.
- Alerts will be sent for top picks and trade actions.

---

## Key Features

- **Multi-Factor Signals:**  
  Combines RSI, MACD, Bollinger Bands, ATR, Stochastic, VWAP, and more for robust trade signals.

- **Trailing Stop Management:**  
  Dynamically manages stops based on ATR, with auto-close on trigger.

- **Fallback Data:**  
  If KuCoin data is insufficient, fetches from Binance.

- **Interactive Dashboards:**  
  View top picks, open positions, and scores in real time.

- **Position Sizing & Risk:**  
  Auto-calculates position size based on equity and leverage.

---

## Recommendations & TODOs

### 1. **Code Consistency**
- **Signal Scoring:**  
  Ensure the scoring logic in `bot_main.py` matches `dashboard2.py` (use a shared function if possible).
- **Top Candidates:**  
  Use the same formatting for `top_candidates.txt`, Telegram, and dashboard (see `format_top_candidates_for_message_and_file` in `dashboard2.py`).

### 2. **Error Handling**
- Add more robust error handling for API/network failures.
- Log errors to a file for debugging.

### 3. **Security**
- Never commit your `.env` file or API keys.
- Consider rate limiting and retry logic for API calls.

### 4. **Testing**
- Add unit tests for your indicator and strategy modules.

### 5. **Documentation**
- Add docstrings to all functions.
- Document your strategy logic in `strategies/`.

### 6. **Enhancements**
- Add more indicators or alternative strategies in `strategies/`.
- Consider adding backtesting support.
- Add a Dockerfile for easy deployment.

---

## Example `.env`

```
KUCOIN_API_KEY=your_key
KUCOIN_API_SECRET=your_secret
KUCOIN_API_PASSPHRASE=your_passphrase
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

---

## Example Telegram Message

```
Top 5 Candidates:
1. BTCUSDTM | Score: 5/6 | Signal: buy | RSI<35, MACD>0, DashboardTop
2. ETHUSDTM | Score: 4/6 | Signal: buy | RSI<35, DashboardTop
...
```

---

## Final Notes

- **Your codebase is modular and well-structured.**
- **Most improvements are about consistency and user experience.**
- **Keep your scoring and signal logic DRY (don’t repeat yourself).**
- **Keep your dashboards and notifications in sync for clarity.**

---

**Let me know if you want a sample Dockerfile, more advanced error handling, or help with any specific module!**