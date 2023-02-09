import numpy as np

def sd(prices, prices_for_pair, lookback=10):
    sd = si(prices_for_pair, lookback) - si(prices, lookback)
    return sd

def si(prices, lookback):
    return (prices - prices.rolling(lookback).min()) / (prices.rolling(lookback).max() - prices.rolling(lookback).min())