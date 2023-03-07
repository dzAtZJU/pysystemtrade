import pandas as pd
import numpy as np
import seaborn as sns
from paper.systems.crypto_system import perpetuals_system
from itables import show
from arctic import Arctic
from itables import show
import matplotlib.pyplot as plt
from pprint import pprint

plt.rcParams['axes.facecolor'] = 'black'
plt.rcParams['figure.facecolor'] = 'black'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'
plt.rcParams['text.color'] = 'white'

store = Arctic('localhost')
artic_lib = store['production.perpetual_prices_v3']

def select_period(se, period):
    start = period[0]
    end = period[1]
    return se[(se.index >= start) &(se.index <= end)]

system = perpetuals_system(config='paper.systems.production.yaml')

# import nasdaqdatalink
# from coinmarketcapapi import CoinMarketCapAPI
# cmc = CoinMarketCapAPI()
# bitcoin_mcp = nasdaqdatalink.get("BCHAIN/MKTCP", authtoken="tUBiAfPRP71_SsxYs_Zw")