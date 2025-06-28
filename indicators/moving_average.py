import pandas as pd

def compute_ema(close_series, span=21):
    return close_series.ewm(span=span, adjust=False).mean()

def compute_sma(close_series, window=21):
    return close_series.rolling(window=window).mean()