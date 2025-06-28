import pandas as pd
import ta

def compute_stochastic(high_series, low_series, close_series, window=14, smooth_window=3):
    stoch = ta.momentum.StochasticOscillator(
        high=high_series.astype(float),
        low=low_series.astype(float),
        close=close_series.astype(float),
        window=window,
        smooth_window=smooth_window
    )
    return stoch.stoch(), stoch.stoch_signal()