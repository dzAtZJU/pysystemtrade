import pandas as pd
from syscore.fileutils import get_pathname_for_package_from_list
from syscore.pdutils import pd_readcsv
from syscore.objects import arg_not_supplied
from syslogdiag.log_to_screen import logtoscreen
from ctse.sysobjects.ctse_strategy_backtest import ctseStrategyBacktest

CTSE_STRATEGY_BACKTEST_DIRECTORY = "ctse.data.strategy_backtest"
DATE_INDEX_NAME = 'tr_datetime'

class csvCTSEStrategyBacktestData:
    def __init__(
        self,
        datapath: str = arg_not_supplied,
        log=logtoscreen("csvCTSEStrategyBacktestData")
    ):
        if datapath is arg_not_supplied:
            datapath = CTSE_STRATEGY_BACKTEST_DIRECTORY

        self._datapath = datapath
        self.log = log


    def __repr__(self):
        return "ctseStrategyBacktestData accessing %s" % self.datapath

    @property
    def datapath(self):
        return self._datapath

    def read(self, instrument: str, strategy:str) -> ctseStrategyBacktest:
        filename = self._filename_given(instrument, strategy)

        try:
            tmp = pd_readcsv(filename, date_index_name=DATE_INDEX_NAME)
        except OSError:
            self.log.warn(
                "Can't find ctse strategy backtest file %s or error reading" % filename,
                instrument_code=instrument,
            )
            return None

        return ctseStrategyBacktest(tmp)

    def _filename_given(self, instrument_code: str, strategy:str):
        filename = get_pathname_for_package_from_list([self.datapath, strategy, "%s.csv" % (instrument_code)])
        return filename