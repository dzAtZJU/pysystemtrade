from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from systems.basesystem import System
from systems.trading_rules import TradingRule
from sysdata.config.configdata import Config
from systems.forecast_scale_cap import ForecastScaleCap
from ctse.systems.accounts_stage import ctseAccount
from ctse.systems.rawdata import ctseRawData
from systems.forecasting import Rules
from ctse.systems.forecast_combine import ctseForecastCombine
from ctse.systems.positionsizing import ctsePositionSizing

from systems.portfolio import Portfolios
import pandas as pd
from syscore.dateutils import ROOT_BDAYS_INYEAR
from ctse.systems.rules.dma_long import dma_long_1_D
import numpy as np

_instrument_weights={
            'RB': 0.0945,
            'J': 0.105,
            'JM': 0.0175,
            'I': 0.07,
            'HC': 0.063,
            'CU': 0.0125,
            'NI': 0.075,
            'SN': 0.075,
            'AL': 0.05,
            'ZN': 0.0375,
            'AG': 0.0,
            'AU': 0.0,
            'SC': 0.008,
            'FU': 0.004,
            'BU': 0.012,
            'SA': 0.004,
            'MA': 0.0056,
            'PP': 0.0056,
            'FG': 0.0056,
            'EG': 0.0096,
            'RU': 0.0,
            'TA': 0.0096,
            'V': 0.008,
            'L': 0.004,
            'SP': 0.004,
            'C': 0.007,
            'Y': 0.021,
            'JD': 0.0,
            'RM': 0.0035,
            'P': 0.0105,
            'SR': 0.0,
            'M': 0.007,
            'OI': 0.0035,
            'A': 0.0035,
            'CF': 0.0105,
            'AP': 0.0035
        }

def ct_system(
    capital_correction_method='syscore.capital.fixed_capital',
    position_sizing_method='none_so_every_trade_cash_all_in',
    annual_vol_target=25,
    notional_capital_leverage=1,
    instrument_weights=_instrument_weights):
    ''''
    
    Parameter
    ----------
    capital_correction_method:
        'syscore.capital.fixed_capital'
        'ctse.syscore.capital.full_compounding'
    position_sizing_method:
        'none_so_every_trade_cash_all_in'
        'vol_target'
    '''
    my_config = Config(
        dict(
            capital_multiplier=dict(func=capital_correction_method),
            position_sizing_method=position_sizing_method,
            percentage_vol_target=annual_vol_target,
            trading_rules=dict(dma_long_1_D=TradingRule(dma_long_1_D, data=['rawdata.get_natural_frequency_prices', 'rawdata.get_instrument_code'])),
            notional_capital_leverage=notional_capital_leverage,
            instrument_weights=instrument_weights,
            notional_trading_capital=1000_0000,
            forecast_weights=dict(dma_long_1_D=1),
            average_absolute_forecast=1,
            base_currency="CNY"
        ), default_filename="ctse.systems.defaults.yaml")
    my_system = System(
        [
            ctseRawData(),
            Rules(), 
            ForecastScaleCap(),
            ctseForecastCombine(),
            ctsePositionSizing(),
            Portfolios(),
            ctseAccount()
        ],
        csvFuturesSimData(csv_data_paths=dict(
            csvFuturesAdjustedPricesData='ctse.data.adjusted_prices_csv',
            csvFuturesMultiplePricesData='ctse.data.multiple_prices_csv',
            csvFuturesInstrumentData='ctse.data.csvconfig'
        )),
        my_config,
    )

    my_system.set_logging_level('off')
    return my_system

if __name__ == '__main__':
    inss  = ct_system(capital_correction_method='syscore.capital.full_compounding').data.get_instrument_list()
    rs = []
    for ins in inss[:1]:
        # sys = ct_system(
        # position_sizing_method='trade_vol_target',
        # annual_vol_target=20,
        # capital_correction_method='syscore.capital.fixed_capital', instrument_weights={ins:1}
        # )
        sys =  ct_system(capital_correction_method='syscore.capital.fixed_capital', instrument_weights={ins:1})
        # rs.append(sys.positionSize.get_subsystem_position(ins) * sys.positionSize.contract_exposure(ins))
        rs.append(sys.rawdata.daily_returns_volatility(ins))
    import pandas as pd
    csv = pd.concat(rs, axis=1).ffill()
    csv = csv.reset_index().rename({'index':'date'}, axis=1)
    csv.to_csv('daily_returns_volatility.csv')