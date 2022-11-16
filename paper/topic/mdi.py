import pandas as pd

def snr(s: pd.Series):
    return abs((s[-1] - s[0])) / s.diff().abs().sum()

def rolling_snr(s: pd.Series, window: int):
    return s.rolling(window, min_periods=window).apply(snr)