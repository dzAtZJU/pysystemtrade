import ccxt
from ccxt import Exchange
import pandas as pd
from datetime import datetime
from dateutil.parser import isoparse
import time

# ccxt.okex5({
#             'apiKey': 'f0029f0c-d729-43aa-a277-2db435b93c11',
#             'secret': 'FEDE42B730B675787361DCD1371BEC46'})

def exchange(exchange_id):
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()
    return exchange
        
def fetch_once(since, symbol, timeframe, exhcnage: Exchange):
    if isinstance(since, str):
        since = int(isoparse(since).timestamp() * 1000)
    candles = exhcnage.fetch_ohlcv(symbol, timeframe=timeframe, since=since)
    df = pd.DataFrame(candles)
    df.index = pd.to_datetime(df.iloc[:, 0], unit='ms', utc=True).dt.tz_convert('Asia/Hong_Kong').dt.tz_localize(None)
    return df

def tmp(since:str, timeframe, symbol, exhcnage: Exchange, before=None):
    '''
    caveat
    1. when timeframe is 1d, hour is alwasy 00:00:00 utc
    2. limit should at least <=100 or there will be datetime bug


    '2021-01-01T10:00+08' 
    'BTC-USDT-SWAP'
    '''
    if isinstance(since, str):
        since = int(isoparse(since).timestamp() * 1000)
    if before is not None:
        before = int(isoparse(before).timestamp() * 1000)

    dfs = []
    while True:
        print(pd.to_datetime(since, unit='ms', utc=True).tz_convert('Asia/Hong_Kong').tz_localize(None))

        candles = exhcnage.fetch_ohlcv(symbol, timeframe=timeframe, since=since)
        df = pd.DataFrame(candles, columns=['date', 'OPEN', 'HIGH', 'LOW', 'FINAL', 'VOLUME'])
        if before is not None and len(df) > 0 and df['date'].iloc[0] > before:
            break
        if len(df) == 0 or df['date'].iloc[-1] == since:
            break
        since = int(df['date'].iloc[-1])
        
        df.index = pd.to_datetime(df.iloc[:, 0], unit='ms', utc=True).dt.tz_convert('Asia/Hong_Kong').dt.tz_localize(None)
        df.drop(columns=['date'], inplace=True)
        dfs.append(df)
        
        if len(dfs) % 20 == 0:
            time.sleep(1)

    if len(dfs) == 0:
        return pd.DataFrame()
    rdf = pd.concat(dfs, axis=0)
    rdf = rdf[~rdf.index.duplicated()]
    new_rdf = rdf.copy().iloc[:-1]
    new_rdf.index = rdf.index[1:]
    
    return new_rdf
    
if __name__ == '__main__':
    print(pd.__version__)
    # df = tmp('2021-01-01T10:00+08')
    # print(df)

# from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
# from systems.provided.example.simplesystem import simplesystem
# from ctse.systems.ct_system import ct_system
# import pandas as pd

# system = ct_system()
# rawdata = system.rawdata
# data = system.data
# perc_returns = [rawdata.get_daily_percentage_returns(instrument_code).rename(instrument_code) for instrument_code in system.get_instrument_list()]
# perc_returns_df = pd.concat(perc_returns, axis=1)
# use_returns =  perc_returns_df.resample("5B").sum()

# def get_forecast_and_future_corr(Nweeks_back, Nweeks_forward):
#     forecast = get_historic_correlations(Nweeks_back)
#     future = get_future_correlations(Nweeks_forward)

#     pd_result = merge_forecast_and_future(forecast, future, Nweeks_forward)

#     return pd_result

# def merge_forecast_and_future(forecast, future, Nweeks_forward):
#     assets = forecast.columns # should be the same won't check
#     pd_result = []
#     for asset in assets:
#         result_for_asset = pd.concat([forecast[asset], future[asset]], axis=1)
#         # remove tail with nothing
#         result_for_asset = result_for_asset[:-Nweeks_forward]

#         # remove overlapping periods which bias R^2
#         selector = range(0, len(result_for_asset.index), Nweeks_forward)
#         result_for_asset = result_for_asset.iloc[selector]

#         result_for_asset.columns = ['forecast', 'turnout']
#         pd_result.append(result_for_asset)

#     pd_result = pd.concat(pd_result, axis=0)

#     return pd_result

# def get_future_correlations(Nweeks_forward):
#     corr = get_rolling_correlations(use_returns, Nweeks_forward)
#     corr = corr.ffill()
#     future_corr = corr.shift(-Nweeks_forward)

#     return future_corr

# def get_historic_correlations(Nweeks_back):
#     corr = get_rolling_correlations(use_returns, Nweeks_back)
#     corr = corr.ffill()

#     return corr

# def get_rolling_correlations(use_returns, Nperiods):
#     roll_df = use_returns.rolling(Nperiods, min_periods=4).corr()
#     perm_names = get_asset_perm_names(use_returns)
#     roll_list = [get_rolling_corr_for_perm_pair(perm_pair, roll_df) for perm_pair in perm_names]
#     roll_list_df = pd.concat(roll_list, axis=1)
#     roll_list_df.columns = ["%s/%s" % (asset1, asset2) for (asset1, asset2) in perm_names]

#     return roll_list_df

# def get_asset_perm_names(use_returns):
#     asset_names = use_returns.columns
#     permlist = []
#     for asset1 in asset_names:
#         for asset2 in asset_names:
#             if asset1==asset2:
#                 continue
#             pairing = [asset1, asset2]
#             if pairing in permlist:
#                 continue
#             pairing.reverse()
#             if pairing in permlist:
#                 continue

#             permlist.append(pairing)

#     return permlist

# def get_rolling_corr_for_perm_pair(perm_pair, roll_df):
#     return roll_df[perm_pair[0]][:,perm_pair[1]]

# df = get_forecast_and_future_corr(12,12)
# df
def get_ins_remote_name(ins):
    coin, base, _ = ins.split('-')
    return coin + base

def update(ins, fre, since='2020-01-01T00:00+08'):
    from syscore.fileutils import  resolve_path_and_filename_for_package
    import ccxt, os

    exchange = ccxt.binanceusdm()
    timeframe = {
        '15m': ('15m', 'Minute15'),
        '1h': ('1h', 'Hour')
        }[fre]
    
    file_path = resolve_path_and_filename_for_package('{}.{}_{}.csv'.format('paper.sysinit.data.Binance', timeframe[1], ins))
    try:
        old_data = pd.read_csv(file_path, index_col=0)
    except Exception:
        old_data = None

    symbol = get_ins_remote_name(ins)
    if old_data is  None:
        history = tmp(since, timeframe[0], symbol, exchange)
    elif pd.Timestamp(since) < pd.Timestamp(old_data.index[0] + '+08'):
        history = tmp(since, timeframe[0], symbol, exchange)
    else:
        since = old_data.index[-1] + '+08'
        history = tmp(since, timeframe[0], symbol, exchange)
        history = pd.concat([old_data, history], axis=0)
    history.to_csv(file_path)
    os.system('say "done, bitch"')

if __name__ == '__main__':
    update('BTC-BUSD-Binance', '1h')