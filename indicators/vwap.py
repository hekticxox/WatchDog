import pandas as pd

def compute_vwap(df):
    # df must have columns: 'close', 'volume'
    vwap = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    return vwap