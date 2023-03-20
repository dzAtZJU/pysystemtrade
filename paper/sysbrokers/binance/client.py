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
Ins = 'BTC-BUSD-Binance'
ins = Ins
Fre = '1h'
Time = ":17"
Sleep = 60 #seconds
Capital = 1000
Risk_target = 0.5
Target_Abs_Forecast = 1

def get_ins_remote_name(local_name):
    coin, base, _ = local_name.split('-')
    return coin + base

def log(txt, local_name):
        with open('{}-job.txt'.format(local_name), 'a') as f:
            f.write('{} {}\n'.format(datetime.now().replace(microsecond=0), txt))
class T:
    @classmethod
    def init_db(self):
        db.initialize_library(Lib_Key, arctic.TICK_STORE)
    
    @property
    def finance_library(self) -> TickStore:
        return db[Lib_Key]

    def init_symbol(self, local_name):
        self.finance_library.delete(local_name)
        df =  pd.read_csv(Root  +  r'paper/sysinit/data/binance/Hour_{}.csv'.format(local_name))
        df.index = pd.to_datetime(df['date']).dt.tz_localize('Asia/Hong_Kong')
        df = df.drop(columns=['date'])
        self.finance_library.write(local_name, df)
        print(self.finance_library.max_date(local_name))

    def clear_symbol(self, local_name):
        self.finance_library.delete(local_name)

    def read_one_year(self, instrument_code, curret_datetime):
        return self.finance_library.read(instrument_code, date_range=DateRange(curret_datetime - pd.Timedelta(365, 'days'), curret_datetime), columns = ['FINAL']).iloc[: ,0]
    
    def read_all(self, instrument_code, curret_datetime):
        return self.finance_library.read(instrument_code, date_range=DateRange(None, curret_datetime), columns = ['FINAL']).iloc[: ,0]
    
    def update_price(self, local_name):
        remote_name = get_ins_remote_name(local_name)
        candles = binance.fetch_ohlcv(remote_name, timeframe=Fre, limit=24 * 3)
        rdf = pd.DataFrame(candles, columns=['date', 'OPEN', 'HIGH', 'LOW', 'FINAL', 'VOLUME'])
        rdf.index = pd.to_datetime(rdf.iloc[:, 0], unit='ms', utc=True).dt.tz_convert('Asia/Hong_Kong')#.dt.tz_localize(None)
        rdf = rdf.drop(columns=['date'])
        log('latest market data is\n {}'.format(rdf.iloc[-1]), local_name)

        new_rdf = rdf.copy().iloc[:-1]
        new_rdf.index = rdf.index[1:]

        max_date = self.finance_library.max_date(local_name)
        new_rdf = new_rdf[new_rdf.index > max_date]
        if not new_rdf.empty:
            self.finance_library.write(local_name, new_rdf)

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

t = T()

def request_order(remote_name, diff):
    abs_diff = round(abs(diff), 2)
    def requese_once():
        if diff > 0:
            order_info = client.futures_create_order(symbol=remote_name, side='BUY', type='MARKET', quantity=abs_diff)
        else:
            order_info  = client.futures_create_order(symbol=remote_name, side='SELL', type='MARKET', quantity=abs_diff)
        return order_info
    
    order_info = None
    try:
        order_info = requese_once()
    except Exception as e:
        log('[ERROR] {}'.format(e), ins)
        query_orders = client.futures_get_open_orders(symbol=remote_name)
        if len(query_orders) > 1:
            order_info = query_orders[0]
        else:
            order_info = requese_once()

    return order_info

def  job():
    try:
        new_df = t.update_price(ins)
        if new_df.empty:
            new_df = t.update_price(ins)
            if new_df.empty:
                log('[WARN] return since no new price data', ins)
                return
        
        price = t.read_one_year(ins, pd.Timestamp.now())
        position = t.cal_position(price)

        remote_name = get_ins_remote_name(ins)
        current_pos = float(client.futures_position_information(symbol=remote_name)[0]['positionAmt'])
        if current_pos != position.iloc[-2]:
            log('[WARN] current position != last optimal position', ins)

        optimal_pos = position.iloc[-1]
        if current_pos == optimal_pos:
            log('market price is {}, current position {} is optimal'.format(price[-1], current_pos), ins)
            return 

        diff = optimal_pos - current_pos
        log('market price is {}, last optimal position is {}, optimal position is {}'.format(price[-1], position[-2], position[-1]), ins)
        order_info = request_order(remote_name, diff)
        log('orderId: {} {} {}'.format(order_info['orderId'], order_info['side'], order_info['origQty']), ins)
    except Exception as e:
        log('[ERROR] {}'.format(e), ins)

def main():
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
    # t.read_all('BTC-BUSD-Binance', pd.Timestamp.now()).to_csv('market-{}.csv'.format('BTC-BUSD-Binance'))
    main()