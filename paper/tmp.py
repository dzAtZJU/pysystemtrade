from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from systems.provided.example.simplesystem import simplesystem
from ctse.systems.ct_system import ct_system
import pandas as pd

system = ct_system()
rawdata = system.rawdata
data = system.data
perc_returns = [rawdata.get_daily_percentage_returns(instrument_code).rename(instrument_code) for instrument_code in system.get_instrument_list()]
perc_returns_df = pd.concat(perc_returns, axis=1)
use_returns =  perc_returns_df.resample("5B").sum()

def get_forecast_and_future_corr(Nweeks_back, Nweeks_forward):
    forecast = get_historic_correlations(Nweeks_back)
    future = get_future_correlations(Nweeks_forward)

    pd_result = merge_forecast_and_future(forecast, future, Nweeks_forward)

    return pd_result

def merge_forecast_and_future(forecast, future, Nweeks_forward):
    assets = forecast.columns # should be the same won't check
    pd_result = []
    for asset in assets:
        result_for_asset = pd.concat([forecast[asset], future[asset]], axis=1)
        # remove tail with nothing
        result_for_asset = result_for_asset[:-Nweeks_forward]

        # remove overlapping periods which bias R^2
        selector = range(0, len(result_for_asset.index), Nweeks_forward)
        result_for_asset = result_for_asset.iloc[selector]

        result_for_asset.columns = ['forecast', 'turnout']
        pd_result.append(result_for_asset)

    pd_result = pd.concat(pd_result, axis=0)

    return pd_result

def get_future_correlations(Nweeks_forward):
    corr = get_rolling_correlations(use_returns, Nweeks_forward)
    corr = corr.ffill()
    future_corr = corr.shift(-Nweeks_forward)

    return future_corr

def get_historic_correlations(Nweeks_back):
    corr = get_rolling_correlations(use_returns, Nweeks_back)
    corr = corr.ffill()

    return corr

def get_rolling_correlations(use_returns, Nperiods):
    roll_df = use_returns.rolling(Nperiods, min_periods=4).corr()
    perm_names = get_asset_perm_names(use_returns)
    roll_list = [get_rolling_corr_for_perm_pair(perm_pair, roll_df) for perm_pair in perm_names]
    roll_list_df = pd.concat(roll_list, axis=1)
    roll_list_df.columns = ["%s/%s" % (asset1, asset2) for (asset1, asset2) in perm_names]

    return roll_list_df

def get_asset_perm_names(use_returns):
    asset_names = use_returns.columns
    permlist = []
    for asset1 in asset_names:
        for asset2 in asset_names:
            if asset1==asset2:
                continue
            pairing = [asset1, asset2]
            if pairing in permlist:
                continue
            pairing.reverse()
            if pairing in permlist:
                continue

            permlist.append(pairing)

    return permlist

def get_rolling_corr_for_perm_pair(perm_pair, roll_df):
    return roll_df[perm_pair[0]][:,perm_pair[1]]

df = get_forecast_and_future_corr(12,12)
df