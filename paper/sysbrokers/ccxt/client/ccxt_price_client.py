from dateutil.tz import tz
import datetime
import pandas as pd
from sysbrokers.IB.client.ib_client import PACING_INTERVAL_SECONDS
from paper.sysbrokers.ccxt.client.ccxt_instrument_client import ccxtInstrumentsClient
from sysbrokers.IB.ib_positions import resolveBS_for_list
from syscore.exceptions import missingContract, missingData

from syscore.dateutils import (
    strip_timezone_fromdatetime,
    Frequency,
    DAILY_PRICE_FREQ,
)

from syslogdiag.log_to_screen import logtoscreen as logger
from syslogdiag.log_to_screen import logtoscreen

from sysobjects.contracts import futuresContract
from sysexecution.trade_qty import tradeQuantity


class tickerWithBS(object):
    def __init__(self, ticker, BorS: str):
        self.ticker = ticker
        self.BorS = BorS


# we don't include ibClient since we get that through contracts client
class ccxtPriceClient(ccxtInstrumentsClient):
    def broker_get_historical_perpetuals_data(
        self,
        instrument_code,
        bar_freq: Frequency = DAILY_PRICE_FREQ,
            whatToShow="TRADES",
        allow_expired=False,
    ) -> pd.DataFrame:
        """
        Get historical daily data

        :param contract_object_with_ib_broker_config: contract where instrument has ib metadata
        :param freq: str; one of D, H, 5M, M, 10S, S
        :return: futuresContractPriceData
        """

        price_data = self._get_generic_data_for_contract(
            instrument_code, bar_freq=bar_freq, whatToShow=whatToShow
        )

        return price_data

    def get_ticker_object(
        self,
        contract_object_with_ib_data: futuresContract,
        trade_list_for_multiple_legs: tradeQuantity = None,
    ) -> tickerWithBS:

        specific_log = contract_object_with_ib_data.specific_log(self.log)

        try:
            ibcontract = self.ib_futures_contract(
                contract_object_with_ib_data,
                trade_list_for_multiple_legs=trade_list_for_multiple_legs,
            )
        except missingContract:
            specific_log.warn(
                "Can't find matching IB contract for %s"
                % str(contract_object_with_ib_data)
            )
            raise

        self.ib.reqMktData(ibcontract, "", False, False)
        ticker = self.ib.ticker(ibcontract)

        ib_BS_str, ib_qty = resolveBS_for_list(trade_list_for_multiple_legs)

        ticker_with_bs = tickerWithBS(ticker, ib_BS_str)

        return ticker_with_bs

    def cancel_market_data_for_contract_object(
        self,
        contract_object_with_ib_data: futuresContract,
        trade_list_for_multiple_legs: tradeQuantity = None,
    ):

        specific_log = contract_object_with_ib_data.specific_log(self.log)

        try:
            ibcontract = self.ib_futures_contract(
                contract_object_with_ib_data,
                trade_list_for_multiple_legs=trade_list_for_multiple_legs,
            )
        except missingContract:
            specific_log.warn(
                "Can't find matching IB contract for %s"
                % str(contract_object_with_ib_data)
            )
            raise

        self.ib.cancelMktData(ibcontract)

    def ib_get_recent_bid_ask_tick_data(
        self,
        contract_object_with_ib_data: futuresContract,
        tick_count=200,
    ) -> list:
        """

        :param contract_object_with_ib_data:
        :return:
        """
        specific_log = self.log.setup(
            instrument_code=contract_object_with_ib_data.instrument_code,
            contract_date=contract_object_with_ib_data.date_str,
        )
        if contract_object_with_ib_data.is_spread_contract():
            error_msg = "Can't get historical data for combo"
            specific_log.critical(error_msg)
            raise Exception(error_msg)

        try:
            ibcontract = self.ib_futures_contract(contract_object_with_ib_data)
        except missingContract:
            specific_log.warn(
                "Can't find matching IB contract for %s"
                % str(contract_object_with_ib_data)
            )
            raise

        recent_time = datetime.datetime.now() - datetime.timedelta(seconds=60)

        tick_data = self.ib.reqHistoricalTicks(
            ibcontract, recent_time, "", tick_count, "BID_ASK", useRth=False
        )

        return tick_data

    def _get_generic_data_for_contract(
        self,
        instrument_code,
        log: logger = None,
        bar_freq: Frequency = DAILY_PRICE_FREQ,
        whatToShow: str = "TRADES",
    ) -> pd.DataFrame:
        """
        Get historical daily data

        :param contract_object_with_ib_data: contract where instrument has ib metadata
        :param freq: str; one of D, H, 5M, M, 10S, S
        :return: futuresContractPriceData
        """
        if log is None:
            log = self.log

        try:
            barSizeSetting, limit = _get_barsize_and_duration_from_frequency(
                bar_freq
            )
        except Exception as exception:
            log.warn(exception)
            raise missingData

        return self._ib_get_historical_data_of_duration_and_barSize(
            instrument_code,
            limit=limit,
            barSizeSetting=barSizeSetting,
            whatToShow=whatToShow,
            log=log,
        )

    def _raw_ib_data_to_df(
        self, price_data_raw: pd.DataFrame, log: logger
    ) -> pd.DataFrame:

        if price_data_raw is None:
            log.warn("No price data from IB")
            raise missingData

        price_data_as_df = price_data_raw[["open", "high", "low", "close", "volume"]]

        price_data_as_df.columns = ["OPEN", "HIGH", "LOW", "FINAL", "VOLUME"]

        date_index = [
            self._ib_timestamp_to_datetime(price_row)
            for price_row in price_data_raw["date"]
        ]
        price_data_as_df.index = date_index

        return price_data_as_df

    ### TIMEZONE STUFF
    def _ib_timestamp_to_datetime(self, timestamp_ib) -> datetime.datetime:
        """
        Turns IB timestamp into pd.datetime as plays better with arctic, converts IB time (UTC?) to local,
        and adjusts yyyymm to closing vector

        :param timestamp_str: datetime.datetime
        :return: pd.datetime
        """

        local_timestamp_ib = self._adjust_ib_time_to_local(timestamp_ib)
        timestamp = pd.to_datetime(local_timestamp_ib)

        adjusted_ts = adjust_timestamp_to_include_notional_close_and_time_offset(
            timestamp
        )

        return adjusted_ts

    def _adjust_ib_time_to_local(self, timestamp_ib) -> datetime.datetime:

        if getattr(timestamp_ib, "tz_localize", None) is None:
            # daily, nothing to do
            return timestamp_ib

        # IB timestamp already includes tz
        timestamp_ib_with_tz = timestamp_ib
        local_timestamp_ib_with_tz = timestamp_ib_with_tz.astimezone(tz.tzlocal())
        local_timestamp_ib = strip_timezone_fromdatetime(local_timestamp_ib_with_tz)

        return local_timestamp_ib

    # HISTORICAL DATA
    # Works for FX and futures
    def _ib_get_historical_data_of_duration_and_barSize(
        self,
        instrument_code,
        limit: int,
        barSizeSetting: str = "1h",
        whatToShow="TRADES",
        log: logger = None,
    ) -> pd.DataFrame:
        """
        Returns historical prices for a contract, up to today
        ibcontract is a Contract
        :returns list of prices in 4 tuples: Open high low close volume
        """
        assert limit <= 100

        if log is None:
            log = self.log

        '''
            '2021-01-01T10:00+08'
            'BTC-USDT-SWAP'
        '''
        since = None
        # if isinstance(since, str):
        #     since = int(isoparse(since).timestamp() * 1000)

        dfs = []
        
        if 'Binance' in instrument_code:
            exchange = self.binance
            instrument_code = instrument_code.replace('-Binance', '')
            instrument_code = instrument_code.replace('-', '/')
        else:
            exchange = self.okx
        while True:
            print(since)
            candles = exchange.fetch_ohlcv(instrument_code, timeframe=barSizeSetting, since=since, limit=limit)
            df = pd.DataFrame(candles, columns=['date', 'OPEN', 'HIGH', 'LOW', 'FINAL', 'VOLUME'])
            if len(df) == 0 or df['date'].iloc[-1] == since:
                break
            since = int(df['date'].iloc[-1])
            
            df.index = pd.to_datetime(df.iloc[:, 0], unit='ms', utc=True).dt.tz_convert('Asia/Hong_Kong').dt.tz_localize(None)
            df.drop(columns=['date'], inplace=True)
            dfs.append(df)
            break
            
        rdf = pd.concat(dfs, axis=0)
        rdf = rdf[~rdf.index.duplicated()]
        new_rdf = rdf.copy().iloc[:-1]
        new_rdf.index = rdf.index[1:]

        return new_rdf

def _get_barsize_and_duration_from_frequency(bar_freq: Frequency) -> (str, int):

    barsize_lookup = dict(
        [
            (Frequency.Day, "1d"),
            (Frequency.Hour, "1h"),
            (Frequency.Minutes_15, "15 mins"),
            (Frequency.Minutes_5, "5 mins"),
            (Frequency.Minute, "1 min"),
            (Frequency.Seconds_10, "10 secs"),
            (Frequency.Second, "1 secs"),
        ]
    )

    duration_lookup = dict(
        [
            (Frequency.Day, 3),
            (Frequency.Hour, 4 * 24),
            (Frequency.Minutes_15, "1 W"),
            (Frequency.Minutes_5, "1 W"),
            (Frequency.Minute, "1 D"),
            (Frequency.Seconds_10, "14400 S"),
            (Frequency.Second, "1800 S"),
        ]
    )
    try:
        assert bar_freq in barsize_lookup.keys()
        assert bar_freq in duration_lookup.keys()
    except:
        raise Exception(
            "Barsize %s not recognised should be one of %s"
            % (str(bar_freq), str(barsize_lookup.keys()))
        )

    ib_barsize = barsize_lookup[bar_freq]
    ib_duration = duration_lookup[bar_freq]

    return ib_barsize, ib_duration


def _avoid_pacing_violation(
    last_call_datetime: datetime.datetime, log: logger = logtoscreen("")
):
    printed_warning_already = False
    while _pause_for_pacing(last_call_datetime):
        if not printed_warning_already:
            log.msg(
                "Pausing %f seconds to avoid pacing violation"
                % (
                    last_call_datetime
                    + datetime.timedelta(seconds=PACING_INTERVAL_SECONDS)
                    - datetime.datetime.now()
                ).total_seconds()
            )
            printed_warning_already = True
        pass


def _pause_for_pacing(last_call_datetime: datetime.datetime):
    time_since_last_call = datetime.datetime.now() - last_call_datetime
    seconds_since_last_call = time_since_last_call.total_seconds()
    should_pause = seconds_since_last_call < PACING_INTERVAL_SECONDS

    return should_pause