from paper.sysproduction.update_historical_prices import update_historical_prices
from paper.topic.common_import import *
from sysquant.estimators.vol import simple_ewvol_calc
from scipy.stats import gmean

def screen(look_back_days, vol_look_back_days, end=pd.Timestamp.now(), ins = 'Hour/BTC-BUSD-Binance'):
    start = end - np.timedelta64(look_back_days + vol_look_back_days , "D")
    period = (start, end)
    vol_look_back_hours = vol_look_back_days * 24

    '''Data'''
    history = artic_lib.read('{}'.format(ins)).data
    volume = select_period(history['VOLUME'], period)
    close = select_period(history['FINAL'].rename('close price'), period)
    show(pd.DataFrame({'holdl return': ['{:.1%}'.format(close[-1] / close[0] - 1)], 'min max chg': ['{:.1%}'.format(max(close.max() / close[0].min() - 1, 1 - close.min() / close[0].max()))]}), caption=ins)

    '''Feature'''
    feature1 = close
    fig = feature1.plot(legend=True, figsize=(16, 4))
    plt.title('{} {} - {}'.format(ins, close.index[0], close.index[-1]))

    if vol_look_back_hours > 0:
        feature2 = simple_ewvol_calc(close.pct_change(), days=vol_look_back_hours, min_periods=vol_look_back_hours).rename('vol') * np.sqrt(24) * np.sqrt(365)
        feature2.plot(legend=True, figsize=(16, 4), secondary_y=True)
    else:
        feature3 = volume
        feature3.plot(legend=True, figsize=(16, 4), secondary_y=True, lw=0.5)
    plt.show()

    plt.figure(figsize=(8,4))
    plt.title('Return Distribution')
    _ = sns.histplot(feature1.pct_change().rename('return'), log_scale=(False, True), binwidth=0.004)
    plt.show()
    # show(feature1.pct_change().sort_values())

if __name__ == '__main__':
    screen(look_back_days=1, vol_look_back_days=0)