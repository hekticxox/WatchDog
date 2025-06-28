import pandas as pd
import ta

def compute_macd(close_series, window_slow=26, window_fast=12, window_sign=9):
    macd = ta.trend.MACD(
        close_series.astype(float),
        window_slow=window_slow,
        window_fast=window_fast,
        window_sign=window_sign
    )
    return macd.macd(), macd.macd_signal(), macd.macd_diff()