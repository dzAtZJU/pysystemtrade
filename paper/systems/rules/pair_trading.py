import numpy as np

def t1(prices):
    buy = prices.rolling(7).min() == prices
    sell = prices.rolling(7).max() == prices
    return (buy * 1 + sell * 1)