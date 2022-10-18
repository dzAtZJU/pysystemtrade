from sysdata.csv.csv_historic_orders import (
    strategyHistoricOrdersData
)
import pandas as pd
from ctse.sysdata.csv_ctse_strategy_backtest_data import csvCTSEStrategyBacktestData
from syscore.objects import arg_not_supplied
from ctse.sysobjects.ctse_strategy_backtest import ctseStrategyBacktest
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.production.tradeable_object import instrumentStrategy
from sysexecution.orders.instrument_orders import instrumentOrder
from sysdata.sim.csv_futures_sim_data import csvFuturesSimData

DATE_INDEX_NAME = "DATETIME"

class csvCTSEStrategyHistoricOrdersData(strategyHistoricOrdersData):
    def __init__(
        self, log=logtoscreen("csvCTSEStrategyHistoricOrdersData")
    ):

        super().__init__( log=log)

        self.strategy_backtest_data_source = csvCTSEStrategyBacktestData(
            datapath='ctse.data.strategy_backtest'
        )
        self.sim_data_source = csvFuturesSimData(csv_data_paths=dict(
            csvFuturesAdjustedPricesData='ctse.data.adjusted_prices_csv',
            csvFuturesMultiplePricesData='ctse.data.multiple_prices_csv',
            csvFuturesInstrumentData='ctse.data.csvconfig',
        ))

    def get_order_with_orderid(self, order_id: str) -> instrumentOrder:
        in_s_key, trigger_close_dt, next_dt = order_id.split('$')
        ins_s = instrumentStrategy.from_key(in_s_key)
        backtest = self._read(ins_s)
        ct_open, ct_next_open, ct_force = backtest.get_force_sales_prices(trigger_close_dt)
        panama_open_prices = self.sim_data_source._get_daily_prices_for_directional_instrument(ins_s.instrument_code)
        panam_open = panama_open_prices[trigger_close_dt]
        panam_nex_open = panama_open_prices[next_dt]

        if panam_open ==  panam_nex_open:
            filled_price = panam_nex_open
        else:
            filled_price=panam_open - (ct_open - ct_force) / (ct_open - ct_next_open) * (panam_open - panam_nex_open)

        return instrumentOrder(
            in_s_key,
            1,
            fill=1,
            filled_price=filled_price,
            fill_datetime=pd.Timestamp(next_dt)
        )

    def get_list_of_order_ids_for_instrument_strategy(
            self, instrument_strategy: instrumentStrategy
        ):
        tmp = self._read(instrument_strategy)
        tmp = tmp.get_list_of_order_ids()
        return [instrument_strategy.key + '$ ' + id for id in tmp]

    def _read(self, instrument_strategy):
        return ctseStrategyBacktest(self.strategy_backtest_data_source.read(instrument_strategy.instrument_code, instrument_strategy.strategy_name))