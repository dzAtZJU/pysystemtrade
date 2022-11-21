from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from paper.systems.simplesystem import simplesystem
import pandas as pd
import numpy as np
from seaborn import heatmap
import matplotlib.pyplot as plt
from sysquant.estimators.diversification_multipliers import diversification_mult_single_period
from sysquant.optimisation.weights import portfolioWeights
from syslogdiag.log_to_screen import logtoscreen

log = logtoscreen('csvFuturesSimData')
log.set_logging_level('close eye')
# data = csvFuturesSimData()
data =  csvFuturesSimData(csv_data_paths=dict(
            csvFuturesAdjustedPricesData='ctse.data.adjusted_prices_csv',
            csvFuturesMultiplePricesData='ctse.data.multiple_prices_csv',
            csvFuturesInstrumentData='ctse.data.csvconfig'
    ), log=log)
system = simplesystem(
    data,
    'paper.systems.china.yaml')

n_2_idms = {}
for N in range(2, 36):
    for _ in range(10):
        inss = pd.Series(data.get_instrument_list()).sample(N)

        system = simplesystem(
            data,
            'paper.systems.china.yaml', log_level='close eye')
        system.config.instrument_weights = {ins:1/len(inss) for ins in inss}
        prices = [system.data.daily_prices(instrument_code).rename(instrument_code) for instrument_code in system.get_instrument_list()]
        prices = pd.concat(prices, axis=1).dropna()

        dates = prices.sample(24 * 7).index
        idms = []
        for date in dates:
            correlation_matrix = system.portfolio.get_correlation_matrix(relevant_date=date)
            weights = pd.Series([1, 2, 3, 4]).sample(len(correlation_matrix.list_of_keys()), replace=True)
            weights = weights / weights.sum()
            weights = weights.to_list()
            print(weights)
            weights = portfolioWeights.from_weights_and_keys(weights, correlation_matrix.list_of_keys())
            
            idm = diversification_mult_single_period(correlation_matrix, weights)
            idms.append(idm)
        df = pd.DataFrame({
                'date': dates,
                'idm': idms
            })
        if N not in n_2_idms:
            n_2_idms[N] = df
        else:
            n_2_idms[N] = pd.concat([n_2_idms[N], df])

n_2_idms