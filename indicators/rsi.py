import pandas as pd
import ta

def compute_rsi(close_series, window=14):
    return ta.momentum.RSIIndicator(close_series, window=window).rsi()