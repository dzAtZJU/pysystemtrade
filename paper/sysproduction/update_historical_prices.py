"""
Update historical data per contract from interactive brokers data, dump into mongodb
"""

from copy import copy
from syscore.objects import success, failure, arg_not_supplied, missing_data
from syscore.merge_data import spike_in_data
from syscore.dateutils import DAILY_PRICE_FREQ, HOURLY_FREQ, Frequency
from syscore.pdutils import merge_data_with_different_freq

from paper.sysdata.data_blob import dataBlob
from sysdata.tools.manual_price_checker import manual_price_checker
from sysdata.mongodb.mongo_futures_instruments import mongoFuturesInstrumentData

from syslogdiag.email_via_db_interface import send_production_mail_msg

from sysobjects.contracts import futuresContract
from sysobjects.futures_per_contract_prices import futuresContractPrices

from paper.sysproduction.data.prices import diagPrices, updatePrices
from paper.sysproduction.data.broker import dataBroker
from sysdata.tools.cleaner import priceFilterConfig, get_config_for_price_filtering
from sysproduction.data.contracts import dataContracts

NO_SPIKE_CHECKING = 99999999999.0

def update_historical_prices():
    """
    Do a daily update for futures contract prices, using IB historical data

    :return: Nothing
    """
    with dataBlob(log_name="Update-Historical-Prices") as data:
        update_historical_price_object = updateHistoricalPrices(data)
        update_historical_price_object.update_historical_prices()
    return success


class updateHistoricalPrices(object):
    def __init__(self, data):
        self.data = data

    def update_historical_prices(self):
        data = self.data
        update_historical_prices_with_data(data)


def update_historical_prices_with_data(data: dataBlob,
                                       interactive_mode: bool = False):
    cleaning_config = get_config_for_price_filtering(data)
    list_of_codes_all = mongoFuturesInstrumentData(data.mongo_db).get_list_of_instruments()
    for instrument_code in list_of_codes_all:
        data.log.label(instrument_code=instrument_code)
        update_historical_prices_for_instrument(instrument_code, data,
                                                cleaning_config = cleaning_config,
                                                interactive_mode = interactive_mode)

def update_historical_prices_for_instrument(
    instrument_code, data: dataBlob,
        cleaning_config: priceFilterConfig = arg_not_supplied,
        interactive_mode: bool = False
):

    # diag_prices = diagPrices(data)
    # intraday_frequency = diag_prices.get_intraday_frequency_for_historical_download()
    daily_frequency = HOURLY_FREQ

    # list_of_frequencies = [intraday_frequency, daily_frequency]
    list_of_frequencies = [daily_frequency]

    for frequency in list_of_frequencies:
        get_and_add_prices_for_frequency(
            data,
            instrument_code,
            frequency=frequency,
            cleaning_config=cleaning_config,
            interactive_mode = interactive_mode
        )

    # write_merged_prices_for_contract(data,
    #                                  instrument_code,
    #                                  list_of_frequencies=list_of_frequencies)

    return success


def get_and_add_prices_for_frequency(
    data: dataBlob,
    instrument_code,
    frequency: Frequency,
    cleaning_config: priceFilterConfig,
    interactive_mode: bool = False
):
    broker_data_source = dataBroker(data)

    broker_prices = broker_data_source.get_cleaned_prices_at_frequency(
        instrument_code, frequency, cleaning_config = cleaning_config
    )

    if broker_prices is missing_data:
        print("Something went wrong with getting prices for %s to check" % str(contract_object))
        return failure

    if len(broker_prices) == 0:
        print("No broker prices found for %s nothing to check" % str(contract_object))
        return success


    if interactive_mode:
        print("\n\n Manually checking prices for %s \n\n" % str(contract_object))
        max_price_spike = cleaning_config.max_price_spike

        price_data = diagPrices(data)
        old_prices = price_data.get_prices_at_frequency_for_contract_object(contract_object,
                                                                            frequency=frequency)
        new_prices_checked = manual_price_checker(
            old_prices,
            broker_prices,
            column_to_check="FINAL",
            delta_columns=["OPEN", "HIGH", "LOW"],
            type_new_data=futuresContractPrices,
            max_price_spike=max_price_spike
        )
        check_for_spike = False
    else:
        new_prices_checked = copy(broker_prices)
        check_for_spike = True

    error_or_rows_added = price_updating_or_errors(data = data,
                                                   frequency=frequency,
                                                   instrument_code=instrument_code,
                                                   new_prices_checked = new_prices_checked,
                                                   check_for_spike=check_for_spike,
                                                   cleaning_config=cleaning_config
                                                   )
    if error_or_rows_added is failure:
        return failure

    data.log.msg(
        "Added %d rows at frequency %s for %s"
        % (error_or_rows_added, frequency, str(instrument_code))
    )
    return success

def price_updating_or_errors(data: dataBlob,
                             frequency: Frequency,
                             instrument_code,
                             new_prices_checked: futuresContractPrices,
                             cleaning_config: priceFilterConfig,
                             check_for_spike: bool = True
                            ):

    price_updater = updatePrices(data)

    error_or_rows_added = price_updater.update_prices_at_frequency(
        instrument_code=instrument_code,
        new_prices=new_prices_checked,
        frequency=frequency,
        check_for_spike=check_for_spike,
        max_price_spike = cleaning_config.max_price_spike
        )

    if error_or_rows_added is spike_in_data:
        report_price_spike(data, instrument_code)
        return failure

    if error_or_rows_added is failure:
        data.log.warn("Something went wrong when adding rows")
        return failure


    return error_or_rows_added

def report_price_spike(data: dataBlob, instrument_code):
    # SPIKE
    # Need to email user about this as will need manually checking
    msg = (
        "Spike found in prices for %s: need to manually check by running interactive_manual_check_historical_prices"
        % str(instrument_code)
    )
    data.log.warn(msg)
    try:
        send_production_mail_msg(
            data, msg, "Price Spike %s" % instrument_code.instrument_code
        )
    except BaseException:
        data.log.warn(
            "Couldn't send email about price spike for %s" % str(instrument_code)
        )

def write_merged_prices_for_contract(data: dataBlob,
                                     contract_object: futuresContract,
                                     list_of_frequencies: list):

    ## note list of frequencies must have daily as last or groupby won't work with volume

    assert list_of_frequencies[-1]==DAILY_PRICE_FREQ

    diag_prices = diagPrices(data)
    price_updater = updatePrices(data)

    list_of_data = [diag_prices.get_prices_at_frequency_for_contract_object(contract_object,
                                                                            frequency=frequency,
                                                                            )
                    for frequency in list_of_frequencies]

    merged_prices = merge_data_with_different_freq(list_of_data)

    price_updater.overwrite_merged_prices_for_contract(contract_object=contract_object,
                                                          new_prices=merged_prices)



if __name__ == '__main__':
    update_historical_prices()

    # from paper.sysdata.arctic.arctic_perpetual_prices import arcticPerpetualsPricesData
    # from syscore.dateutils import Frequency
    # arcticPerpetualsPricesData().get_prices_at_frequency('XRP-USDT-SWAP', Frequency.Hour).to_csv('tmp-BTC-USDT-SWAP.csv')