"""
Functions to calculate capital multiplier

ALl return Tx1 pd.Series
"""
from copy import copy
import pandas as pd
import numpy as np

def full_compounding(system, **ignored_args):
    pandl = system.accounts.portfolio(delayfill=False, roundpositions=False).percent
    multiplier = 1.0 + (pandl / 100.0)
    multiplier = multiplier.cumprod().ffill()

    return multiplier