import pandas as pd

# Load your signal log
df = pd.read_csv("signal_log.csv")

# Load your historical price data
prices = pd.read_csv("historical_prices.csv")  # You need to provide this file

def fetch_future_price(symbol, timestamp, minutes_ahead=60):
    """
    Fetch the close price of 'symbol' at 'timestamp' + minutes_ahead.
    """
    future_time = int(timestamp) + minutes_ahead * 60 * 1000  # if timestamp is in ms
    df = prices[(prices['symbol'] == symbol) & (prices['timestamp'] >= future_time)]
    if not df.empty:
        return df.iloc[0]['close']
    return None

def get_outcome(row, future_minutes=60):
    """
    Label if the signal would have been profitable after 'future_minutes'.
    """
    future_price = fetch_future_price(row['symbol'], row['timestamp'], future_minutes)
    entry_price = row['VWAP'] if 'VWAP' in row else None
    if pd.isna(future_price) or pd.isna(entry_price):
        return None
    if row['SIGNAL'] == 'buy':
        return 1 if future_price > entry_price else 0
    elif row['SIGNAL'] == 'sell':
        return 1 if future_price < entry_price else 0
    else:
        return None

# Label each row (this may take time if you have a lot of data)
df['PROFITABLE'] = df.apply(get_outcome, axis=1)

# Analyze indicator patterns
good = df[df['PROFITABLE'] == 1]
bad = df[df['PROFITABLE'] == 0]

print("Good trade avg RSI:", good['RSI'].mean())
print("Bad trade avg RSI:", bad['RSI'].mean())
print("Good trade avg MACD:", good['MACD'].mean())
print("Bad trade avg MACD:", bad['MACD'].mean())
print("Good trade avg ATR:", good['ATR'].mean())
print("Bad trade avg ATR:", bad['ATR'].mean())
# ...repeat for other indicators

# Save labeled data for further analysis
df.to_csv("signal_log_labeled.csv", index=False)