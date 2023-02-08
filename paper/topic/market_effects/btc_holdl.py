import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from syscore.fileutils import get_filename_for_package
from paper.systems.crypto_system import perpetuals_system
from itables import show
def select(se, start, end):
    return se[(se.index >= start) &(se.index <= end)]

system = perpetuals_system(config='paper.systems.crypto_v1_base.yaml')
system.accounts.pandl_for_instrument_forecast('BTC-USDT-SWAP', 'market_effects').cumsum().plot()
