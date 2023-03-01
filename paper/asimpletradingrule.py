import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from paper.systems.crypto_system import perpetuals_system
from itables import show
def select(se, start, end):
    return se[(se.index >= start) &(se.index <= end)]

import pandas as pd
from sysquant.estimators.vol import robust_vol_calc


def calc_ewmac_forecast(price, Lfast, Lslow=None):
    """
    Calculate the ewmac trading rule forecast, given a price and EWMA speeds
    Lfast, Lslow and vol_lookback

    """
    # price: This is the stitched price series
    # We can't use the price of the contract we're trading, or the volatility
    # will be jumpy
    # And we'll miss out on the rolldown. See
    # https://qoppac.blogspot.com/2015/05/systems-building-futures-rolling.html

    # price = price.resample("1B").last()

    if Lslow is None:
        Lslow = 4 * Lfast

    # We don't need to calculate the decay parameter, just use the span
    # directly
    fast_ewma = price.ewm(span=Lfast).mean()
    slow_ewma = price.ewm(span=Lslow).mean()
    raw_ewmac = fast_ewma - slow_ewma
    vol = robust_vol_calc(price.diff())
    return raw_ewmac / vol

system = perpetuals_system(config='paper.systems.production.yaml')
data = system.data

instrument_code = 'BTC-USDT-SWAP'
price = data.hourly_prices(instrument_code)
ewmac = calc_ewmac_forecast(price, 4, 16)
ewmac.columns = ['forecast']
show(ewmac.tail(7 * 24))

from systems.accounts.account_forecast import pandl_for_instrument_forecast
vol, position, curve = pandl_for_instrument_forecast(
    forecast=ewmac,
    price = price,
    capital = 2000,
    risk_target = 16,
    target_abs_forecast = 1,
    SR_cost=0.0,
    delayfill=True,
    )