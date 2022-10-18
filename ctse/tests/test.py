import pandas as pd
import matplotlib.pyplot as plt
from ctse.systems.ct_system import ct_system, instrument_weights
instruments = list(instrument_weights.keys())[2:8]

rs = []
for ins in instruments:
    nihe = pd.read_csv('/Users/weiranzhou/Code/pysystemtrade/ctse/data/strategy_backtest/DMA_LONG_1_D/%s.csv' % ins, parse_dates=['tr_datetime'], index_col='tr_datetime')['tr_nav_of_product']
    nihe = nihe / nihe.iloc[0]

    system = ct_system()
    system.config.instrument_weights = {ins:1}
    compunding = system.accounts.portfolio_with_multiplier(delayfill=False, roundpositions=False).curve()
    compunding = compunding / 1000_0000 + 1

    rs.append((compunding / nihe).rename(ins))
pd.concat(rs, axis=1).plot(legend=False)