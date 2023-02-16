import numpy as np

def pair_trading(prices, prices_for_pair, lookback=10):
    sd = cal_sd(prices, prices_for_pair, lookback)
    sd = sd.clip(-0.5, 0.5)
    sd[(sd!=-0.5) & (sd!=0.5) & (sd!=0)] = np.nan
    sd = sd.ffill()
    return sd
    
def cal_sd(prices, prices_for_pair, lookback):
    sd = si(prices_for_pair, lookback) - si(prices, lookback)
    return sd

def si(prices, lookback):
    return (prices - prices.rolling(lookback).min()) / (prices.rolling(lookback).max() - prices.rolling(lookback).min())