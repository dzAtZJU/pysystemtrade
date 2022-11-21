from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from sysdata.config.configdata import Config

from systems.forecasting import Rules
from systems.basesystem import System
from ctse.systems.forecast_combine import ctseForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from ctse.systems.positionsizing import ctsePositionSizing
from systems.positionsizing import PositionSizing
from systems.portfolio import Portfolios
from paper.accounts_stage import paperAccount
from paper.rawdata import paperRawData


def simplesystem(data=None, config=None, log_level="on"):
    """
    Example of how to 'wrap' a complete system
    """
    my_system = System(
        [
            paperAccount(),
            Portfolios(),
            PositionSizing(),
            # ctsePositionSizing(),
            ctseForecastCombine(),
            ForecastScaleCap(),
            Rules(),
            paperRawData()
        ],
        data,
        Config(config),
    )

    my_system.set_logging_level(log_level)

    return my_system

if __name__ == '__main__':
    from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
    import pandas as pd
    import numpy as np
    from seaborn import heatmap
    import matplotlib.pyplot as plt
    from sysquant.estimators.diversification_multipliers import diversification_mult_single_period
    from sysquant.optimisation.weights import portfolioWeights
    from syslogdiag.log_to_screen import logtoscreen

    
    # inss_benchmark = [
    # ['C', 'CU', 'I', 'TA'],
    # ['CF', 'ZN', 'JM', 'V'],
    # ['RM', 'AL', 'J', 'EG']
    # ]

    # date = pd.Timestamp('2021-08-01')
    # for i in range(len(inss_benchmark[2])):
    #     inss = inss_benchmark[0][:i+1]
    #     log = logtoscreen('csvFuturesSimData')
    #     log.set_logging_level('close eye')
    #     data =  csvFuturesSimData(csv_data_paths=dict(
    #                 csvFuturesAdjustedPricesData='ctse.data.adjusted_prices_csv',
    #                 csvFuturesMultiplePricesData='ctse.data.multiple_prices_csv',
    #                 csvFuturesInstrumentData='ctse.data.csvconfig',
    #         ), log=log)
    #     system = simplesystem(
    #         data,
    #         'paper.systems.china.yaml', log_level='close eye')
        # system.config.instrument_weights = {ins:1/len(inss) for ins in inss}
        # correlation_matrix = system.portfolio.get_correlation_matrix(relevant_date=date)
        # idm = diversification_mult_single_period(correlation_matrix, portfolioWeights.all_one_value(correlation_matrix.list_of_keys(), 1 / len(correlation_matrix.list_of_keys())))
        # print(idm)
    data =  csvFuturesSimData(csv_data_paths=dict(
            csvFuturesAdjustedPricesData='ctse.data.adjusted_prices_csv',
            csvFuturesMultiplePricesData='ctse.data.multiple_prices_csv',
            csvFuturesInstrumentData='ctse.data.csvconfig',
    ))
    system = simplesystem(
            data,
            'paper.systems.china.yaml', log_level='close eye')
    r = system.accounts.portfolio().curve()
    print(r)

