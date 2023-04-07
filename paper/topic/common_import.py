import syscore.pandas.strategy_functions as  strategy_functions
import pandas as pd
import numpy as np
import seaborn as sns
from paper.systems.crypto_system import perpetuals_system
from itables import show
from arctic import Arctic
from itables import show
import matplotlib.pyplot as plt
from pprint import pprint
from binance.client import Client
from sysdata.config.configdata import Config
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

def get_client():
    config = Config('paper.systems.production.yaml')
    config.fill_with_defaults()
    client = Client(config.get_element('binance_report_apikey'), config.get_element('binance_report_secretkey'), testnet=False)
    return client
# import nasdaqdatalink
# from coinmarketcapapi import CoinMarketCapAPI
# cmc = CoinMarketCapAPI()
# bitcoin_mcp = nasdaqdatalink.get("BCHAIN/MKTCP", authtoken="tUBiAfPRP71_SsxYs_Zw")

if __name__ == '__main__':
    for ins in system.portfolio.get_instrument_list():
        # pos = system.portfolio.get_actual_position(ins).rename(ins)
        # show(pos)
        pl = system.accounts.portfolio(roundpositions=False)
        print(pl)