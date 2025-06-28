import pandas as pd
import ta

def compute_bollinger(close_series, window=20, window_dev=2):
    bb = ta.volatility.BollingerBands(
        close_series.astype(float),
        window=window,
        window_dev=window_dev
    )
    return bb.bollinger_hband(), bb.bollinger_lband(), bb.bollinger_mavg()