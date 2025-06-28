import pandas as pd
import ta

def compute_atr(high_series, low_series, close_series, window=14):
    atr = ta.volatility.AverageTrueRange(
        high=high_series.astype(float),
        low=low_series.astype(float),
        close=close_series.astype(float),
        window=window
    )
    return atr.average_true_range()