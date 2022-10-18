OPERATE_HOLDING = [1, '1', 2, '2']
from ctse.sysdata.csv_ctse_strategy_backtest_data import csvCTSEStrategyBacktestData

def dma_long_1_D(price, instrument):
    '''
    only forecast 0, 1
    '''

    forecast = csvCTSEStrategyBacktestData().read(instrument, 'DMA_LONG_1_D').forecast()
    # assert (price.index == forecast.index).all()
    return forecast

if __name__ == '__main__':
    from sysdata.csv.csv_adjusted_prices import csvFuturesAdjustedPricesData
    ins = 'J'
    price = csvFuturesAdjustedPricesData('ctse.data.adjusted_prices_csv').get_adjusted_prices(ins)
    r = dma_long_1_D(price, ins)
    pass
    