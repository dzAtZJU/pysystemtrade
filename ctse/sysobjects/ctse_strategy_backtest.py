from syscore.objects import missing_data
from dataclasses import dataclass
import datetime as datetime
from copy import copy
import pandas as pd

class ctseStrategyBacktest(pd.DataFrame):
    DATETIME = 'tr_datetime'
    OPEN = 'tr_the_open_price'
    CLOSE = 'tr_the_close_price'
    HIGH = 'tr_the_max_price'
    LOW = 'tr_the_min_price'
    NAV = 'tr_nav_of_product'
    OPERATE = 'tr_operate'
    STOP_LOSS_KEYWORD = '止损'
    OPERATE_FLAG = 'tr_operate_flag'
    STATE_FLAG = 'tr_state_flag'

    STATE_NONE = [0, '0']
    NO_OPERATE = [-1, '-1']
    TRIGGER_OPEN = [1, '1']
    HOLD = [2, '2']
    FORECAST_HOLD = TRIGGER_OPEN + HOLD
    TRIGGER_CLOSE = [3, '3']

    def __init__(self, data):
        super().__init__(data)

        data.index.name = "index"  # arctic compatible

    def forecast(self):
        return self[self.OPERATE_FLAG].isin(self.FORECAST_HOLD) * 1

    def get_trades(self):
        before_trigger_open_index = self.loc[
            self[self.OPERATE_FLAG].shift(-1).isin(self.TRIGGER_OPEN)
            & (self[self.STATE_FLAG].isin(self.STATE_NONE))
            ].index

        close_index = self.loc[
            self[self.OPERATE_FLAG].isin(self.TRIGGER_CLOSE)
            ].index

        assert len(before_trigger_open_index) == len(close_index)
        return list(zip(before_trigger_open_index, close_index))

    def query_trade_returns(self, before_trigger_open_index, close_index):
        return self[(self.index >= before_trigger_open_index) & (self.index <= close_index)][self.NAV].pct_change().iloc[1:]

    def get_list_of_order_ids(self):
        stop_loss_close_dt_list  = self.loc[
            self[self.OPERATE_FLAG].isin(self.TRIGGER_CLOSE) &
            self[self.OPERATE].str.contains(self.STOP_LOSS_KEYWORD)
            ].index
        id_list = []
        for  dt in stop_loss_close_dt_list:
            next = self.loc[dt:].index[1]
            id_list.append('%s$%s' % (dt, next))

        return id_list

    def get_force_sales_prices(self, close_dt):
        row = self.loc[close_dt]
        force_sale_price = float(row[self.OPERATE].split('_')[-1])
        open_price = row[self.OPEN]
        next_open_price = self.loc[close_dt:].iloc[1][self.OPEN]
        return ( open_price, next_open_price, force_sale_price)