from ctse.sysdata.csv_ctse_strategy_backtest_data import csvCTSEStrategyBacktestData
from ctse.sysobjects.ctse_strategy_backtest import ctseStrategyBacktest
from ctse.systems.ct_system import ct_system
import pandas as pd
from syscore.pdutils import pd_readcsv
import numpy as np

def get_continuious_leveraged_returns(leverage_ratio, returns):
    return leverage_ratio * returns

def get_leveraged_returns(leverage_ratio, returns):
    u = (returns + 1).cumprod().shift(1, fill_value=1)
    return leverage_ratio * returns* u / (leverage_ratio * u - leverage_ratio + 1)

def get_static_leverage_factor_forecast(leverage_factor):
    inss  = ct_system(capital_correction_method='syscore.capital.full_compounding').data.get_instrument_list()
    rs = []
    for ins in inss[:]:
        sys = ct_system(
        position_sizing_method='trade_vol_target',
        annual_vol_target=12,
        capital_correction_method='syscore.capital.fixed_capital', instrument_weights={ins:1}
        )
        dumb = sys.positionSize.daily_risk_target_capital_pct(ins).rename(ins)
        rs.append(pd.Series(leverage_factor, index=dumb.index).rename(ins))
    csv = pd.concat(rs, axis=1)
    return csv

def get_dynamic_leverage_factor_forecast(year_risk_target):
    inss  = ct_system(capital_correction_method='syscore.capital.full_compounding').data.get_instrument_list()
    rs = []
    target = year_risk_target
    for ins in inss[:]:
        sys = ct_system(
        position_sizing_method='trade_vol_target',
        annual_vol_target=target,
        capital_correction_method='syscore.capital.fixed_capital', instrument_weights={ins:1}
        )
        rs.append(sys.positionSize.daily_risk_target_capital_pct(ins).rename(ins))
    
    csv = pd.concat(rs, axis=1)
    return csv

def backtest(
    year_risk_target_or_leverage_factor,
    leverage_forecast_method=get_dynamic_leverage_factor_forecast,
    leverage_execution_method=get_continuious_leveraged_returns):

    leverage_ratio_forecast = leverage_forecast_method(year_risk_target_or_leverage_factor)
    inss  = ct_system(capital_correction_method='syscore.capital.full_compounding').data.get_instrument_list()
    ori_backtest_data= csvCTSEStrategyBacktestData()
    for ins in inss:
        print(ins)
        ori_backtest = ori_backtest_data.read(ins, 'DMA_LONG_1_D')
        ori_backtest.loc[:, 'leverage_factor'] = leverage_ratio_forecast[ins].shift(1).reindex(ori_backtest.index)
        ori_backtest.loc[:, 'leveraged_returns'] = 0
        for before_open, close in ori_backtest.get_trades():
            leverage_ratio = ori_backtest['leverage_factor'].loc[before_open]
            trade_returns = ori_backtest.query_trade_returns(before_open, close)
            ori_backtest.loc[:, 'leveraged_returns'].update(leverage_execution_method(leverage_ratio, trade_returns))
        ori_backtest.loc[:, 'leveraged_nav'] = (ori_backtest['leveraged_returns'] + 1).cumprod()
        ori_backtest.to_csv(r'ctse/data/tmp/{}/{}_{}.csv'.format(leverage_execution_method.__name__, ins, year_risk_target_or_leverage_factor))

if __name__ == '__main__':
    # backtest(12)
    # backtest(16)
    # backtest(20)
    # backtest(24)
    # backtest(28)
    # backtest(30)

    # backtest(1, leverage_forecast_method=get_static_leverage_factor_forecast)
    # backtest(2, leverage_forecast_method=get_static_leverage_factor_forecast)
    # backtest(3, leverage_forecast_method=get_static_leverage_factor_forecast)
    # backtest(4, leverage_forecast_method=get_static_leverage_factor_forecast)
    # backtest(5, leverage_forecast_method=get_static_leverage_factor_forecast)
    # backtest(6, leverage_forecast_method=get_static_leverage_factor_forecast)
    # backtest(7, leverage_forecast_method=get_static_leverage_factor_forecast)
    # backtest(8, leverage_forecast_method=get_static_leverage_factor_forecast)

    backtest(1, leverage_forecast_method=get_static_leverage_factor_forecast, leverage_execution_method=get_leveraged_returns)
    backtest(2, leverage_forecast_method=get_static_leverage_factor_forecast, leverage_execution_method=get_leveraged_returns)
    backtest(3, leverage_forecast_method=get_static_leverage_factor_forecast, leverage_execution_method=get_leveraged_returns)
    backtest(4, leverage_forecast_method=get_static_leverage_factor_forecast, leverage_execution_method=get_leveraged_returns)
    backtest(5, leverage_forecast_method=get_static_leverage_factor_forecast, leverage_execution_method=get_leveraged_returns)
    backtest(6, leverage_forecast_method=get_static_leverage_factor_forecast, leverage_execution_method=get_leveraged_returns)
    backtest(7, leverage_forecast_method=get_static_leverage_factor_forecast, leverage_execution_method=get_leveraged_returns)
    backtest(8, leverage_forecast_method=get_static_leverage_factor_forecast, leverage_execution_method=get_leveraged_returns)

