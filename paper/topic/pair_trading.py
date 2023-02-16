import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from syscore.fileutils import get_filename_for_package
from paper.systems.crypto_system import perpetuals_system
from itables import show

def select(se, start, end):
    return se[(se.index >= start) &(se.index <= end)]


system = perpetuals_system(config='paper.systems.pair_trading.yaml')

from paper.systems.rules.pair_trading import cal_sd, si, pair_trading

st = '2022-06-25'
et = '2023-07-08'
p1 = 'UAL'
p2 = 'AAL'

select((system.data.daily_prices(p1).rename(p1)), st, et).plot(figsize=(15, 6), legend=True)
select((system.data.daily_prices(p2)).rename(p2), st, et).plot(secondary_y=True, legend=True)
plt.show()

# select((system.data.daily_prices(p1).rename(p1)).pct_change(), st, et).plot(figsize=(15, 6), legend=True)
# select((system.data.daily_prices(p2)).rename(p2).pct_change(), st, et).plot(secondary_y=True, legend=True)
# plt.show()

select(system.data.daily_prices(p1).rename(p1).pct_change() - system.data.daily_prices(p2).rename(p2).pct_change(), st, et).plot(figsize=(15, 6), legend=True)
plt.show()


select(si(system.data.daily_prices(p1), 10).rename(p1), st, et).plot(figsize=(15, 6), legend=True)
select(si(system.data.daily_prices(p2),10).rename(p2), st, et).plot(legend=True)
plt.show()

select(system.rules.get_raw_forecast(p1, "pair_trading"), st, et).plot(figsize=(15, 6), legend=True)
plt.show()
# select(system.rawdata.annualised_percentage_volatility("BNB-USDT-SWAP").tail(360).plot(secondary_y=True)

pl = select(system.accounts.pandl_for_instrument_forecast(p1, 'pair_trading'), st, et).rename(p1)
pl.cumsum().plot(figsize=(15, 6), legend=True)
pl2 = select(system.accounts.pandl_for_instrument_forecast(p2, 'pair_trading'), st, et).rename(p2)
pl2.cumsum().plot(figsize=(15, 6), legend=True)
plt.show()
(pl + pl2).cumsum().plot(figsize=(15, 6), legend=True)


# sd = cal_sd(system.data.daily_prices('BNB-USDT-SWAP'), system.data.daily_prices('ETH-USDT-SWAP'), 10).rename('BNB')
# sd = sd.clip(-0.4, 0.4)
# sd[(sd!=-0.4) & (sd!=0.4) & (sd!=0)] = np.nan
# sd = sd.ffill()
# sd.plot(figsize=(15, 6), legend=True)