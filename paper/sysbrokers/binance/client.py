import ccxt
import schedule
import pandas as pd
import time
from datetime import datetime
from arctic import Arctic, arctic
from arctic import Arctic, arctic
from arctic.date import DateRange
from arctic.tickstore.tickstore import TickStore
from systems.provided.rules.ewmac import hour_ewmac
from systems.accounts.account_forecast import pandl_for_instrument_forecast
from binance.client import Client
from sysdata.config.configdata import Config

config = Config('paper.systems.production.yaml')
config.fill_with_defaults()
client = Client(config.get_element('binance_mock_apikey'), config.get_element('binance_mock_secretkey'), testnet=True)

binance = ccxt.binanceusdm()
db = Arctic('localhost')
Lib_Key = 'binance_v1'

Root = '/Users/weiranzhou/Code/pysystemtrade/'
Root = '/home/ec2-user/pysystemtrade/'
Ins = 'BTC/USDT'
Fre = '1h'
Time = ":00"
Sleep = 60 #seconds
Capital = 1000
Risk_target = 0.5
Target_Abs_Forecast = 1

class T:
    @property
    def finance_library(self) -> TickStore:
        return db[Lib_Key]

    def init_symbol(self, Ins):
        self.finance_library.delete(Ins)
        df =  pd.read_csv(Root  +  r'paper/sysinit/data/binance/Hour_BTC-USDT-Binance.csv')
        df.index = pd.to_datetime(df['date']).dt.tz_localize('Asia/Hong_Kong')
        df = df.drop(columns=['date'])
        self.finance_library.write(Ins, df)
        print(self.finance_library.max_date(Ins))

    def clear_symbol(self, Ins):
        self.finance_library.delete(Ins)

    @classmethod
    def init_db(self):
        db.initialize_library(Lib_Key, arctic.TICK_STORE)
        
    def read_one_year(self, instrument_code, curret_datetime):
        return self.finance_library.read(instrument_code, date_range=DateRange(curret_datetime - pd.Timedelta(365, 'days'), curret_datetime), columns = ['FINAL']).iloc[: ,0]
    
    def read_all(self, instrument_code, curret_datetime):
        return self.finance_library.read(instrument_code, date_range=DateRange(None, curret_datetime), columns = ['FINAL']).iloc[: ,0]
    
    def update_price(self, instrument_code):
        candles = binance.fetch_ohlcv(instrument_code, timeframe=Fre, limit=24 * 3)
        rdf = pd.DataFrame(candles, columns=['date', 'OPEN', 'HIGH', 'LOW', 'FINAL', 'VOLUME'])
        rdf.index = pd.to_datetime(rdf.iloc[:, 0], unit='ms', utc=True).dt.tz_convert('Asia/Hong_Kong')#.dt.tz_localize(None)
        rdf = rdf.drop(columns=['date'])

        new_rdf = rdf.copy().iloc[:-1]
        new_rdf.index = rdf.index[1:]

        max_date = self.finance_library.max_date(instrument_code)
        new_rdf = new_rdf[new_rdf.index > max_date]
        if not new_rdf.empty:
            self.finance_library.write(Ins, new_rdf)

        return new_rdf

    def cal_position(self, price):
        forecast = hour_ewmac(price)

        vol, position, account = pandl_for_instrument_forecast(
        forecast=forecast,
        price = price,
        capital = Capital,
        risk_target = Risk_target,
        target_abs_forecast = Target_Abs_Forecast,
        SR_cost=0.1,
        delayfill=True
        )
        position = position.round(2)
        return position


def main():
    t = T()

    def log(txt):
        with open('job.txt', 'a') as f:
            f.write('{} {}\n'.format(datetime.now().replace(microsecond=0), txt))

    def  job():
        try:
            new_df = t.update_price(Ins)
            if new_df.empty:
                log('[WARN] return since no new price data')
                return
            
            curret_datetime = new_df.index[-1]
            price = t.read_one_year(Ins, curret_datetime)
            position = t.cal_position(price)

            current_pos = float(client.futures_position_information(symbol=Ins.replace('/', ''))[0]['positionAmt'])
            if current_pos != position.iloc[-2]:
                log('[WARN] current position != last optimal position')

            optimal_pos = position.iloc[-1]
            if current_pos == optimal_pos:
                log('current position {} is optimal'.format(current_pos))
                return 

            diff = optimal_pos - current_pos
            abs_diff = round(abs(diff), 2)
            log('market price is {}, last optimal position is {}, optimal position is {}'.format(price[-1], position[-2], position[-1]))
            order_info = None
            if diff > 0:
                order_info = client.futures_create_order(symbol='BTCUSDT', side='BUY', type='MARKET', quantity=abs_diff)
            else:
                order_info  = client.futures_create_order(symbol='BTCUSDT', side='SELL', type='MARKET', quantity=abs_diff)
            log('orderId: {} {} {}'.format(order_info['orderId'], order_info['side'], order_info['origQty']))
        except Exception as e:
            log('[ERROR] {}'.format(e))
    

    if Fre == '1m':
        schedule.every().minute.at(Time).do(job)
    elif Fre == '1h':
        schedule.every().hour.at(Time).do(job)
    else:
        assert False, 'Fre not supported'

    while True:
        schedule.run_pending()
        time.sleep(Sleep)
    
    

if __name__ == '__main__':
    # T.init_db()
    # t = T()
    # t.init_symbol(Ins)
    # t.update_price(Ins)
    # t.clear_symbol(Ins)
    # job()
    main()