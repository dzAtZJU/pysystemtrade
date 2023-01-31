from paper.sysdata.perpetuals.perpetuals_prices import (
    perpetualsPriceData
)
from paper.sysobjects.spot_prices import spotPrices
from sysobjects.futures_per_contract_prices import futuresContractPrices
from sysdata.arctic.arctic_connection import arcticData
from syslogdiag.log_to_screen import logtoscreen
import pandas as pd
from syscore.dateutils import Frequency, DAILY_PRICE_FREQ, MIXED_FREQ


PERPETUAL_PRICE_COLLECTION = "perpetual_prices_v3"

class arcticPerpetualsPricesData(perpetualsPriceData):
    """
    Class to read / write multiple futures price data to and from arctic
    """

    def __init__(self, mongo_db=None, log=logtoscreen("arcticFuturesAdjustedPrices")):

        super().__init__(log=log)

        self._arctic_connection = arcticData(PERPETUAL_PRICE_COLLECTION, mongo_db=mongo_db)

    def __repr__(self):
        return repr(self._arctic_connection)

    @property
    def arctic_connection(self):
        return self._arctic_connection

    def get_list_of_instruments(self) -> list:
        return self.arctic_connection.get_keynames()
     
    def _get_spot_prices_without_checking(
        self, instrument_code: str
    ) -> spotPrices:
        data = self.arctic.read(instrument_code)

        instrpricedata = spotPrices(data[data.columns[0]])

        return instrpricedata

    def _add_spot_prices_without_checking_for_existing_entry(
        self, instrument_code: str, adjusted_price_data: spotPrices
    ):
        adjusted_price_data_aspd = pd.DataFrame(adjusted_price_data)
        adjusted_price_data_aspd.columns = ["price"]
        adjusted_price_data_aspd = adjusted_price_data_aspd.astype(float)
        self.arctic.write(instrument_code, adjusted_price_data_aspd)
        self.log.msg(
            "Wrote %s lines of prices for %s to %s"
            % (len(adjusted_price_data), instrument_code, str(self)),
            instrument_code=instrument_code,
        )

    def _write_merged_prices_for_contract_object_no_checking(
        self,
        instrument_code,
        futures_price_data: futuresContractPrices,
    ):
        """
        Write prices
        CHECK prices are overriden on second write

        :param futures_contract_object: futuresContract
        :param futures_price_data: futuresContractPriceData
        :return: None
        """

        self._write_prices_at_frequency_for_contract_object_no_checking(instrument_code,
                                                                        frequency=MIXED_FREQ,
                                                                        futures_price_data=futures_price_data)

    def _write_prices_at_frequency_for_contract_object_no_checking(
        self,
        instrument_code,
        futures_price_data: futuresContractPrices,
        frequency: Frequency
    ):

        ident = from_contract_and_freq_to_key(instrument_code,
                                              frequency=frequency)
        futures_price_data_as_pd = pd.DataFrame(futures_price_data)

        self.arctic_connection.write(ident, futures_price_data_as_pd)

        self.log.msg(
            "Wrote %s lines of prices for %s at %s to %s"
            % (len(futures_price_data), str(instrument_code), str(frequency), str(self))
        )
    
    def _get_prices_at_frequency_for_contract_object_no_checking \
                    (self, instrument_code, frequency: Frequency) -> futuresContractPrices:

        ident = from_contract_and_freq_to_key(instrument_code,
                                              frequency=frequency)

        # Returns a data frame which should have the right format
        data = self.arctic_connection.read(ident)

        return futuresContractPrices(data)

    def get_contracts_with_merged_price_data(self) -> list:
        """

        :return: list of contracts
        """

        list_of_contracts = self.get_contracts_with_price_data_for_frequency(frequency=MIXED_FREQ)

        return list_of_contracts

    def get_contracts_with_price_data_for_frequency(self,
                                                    frequency: Frequency) -> list:

        list_of_contract_and_freq_tuples = self._get_contract_and_frequencies_with_price_data()
        list_of_contracts = [
            freq_and_contract_tuple[1]
            for freq_and_contract_tuple in list_of_contract_and_freq_tuples
            if freq_and_contract_tuple[0] == frequency
        ]

        return list_of_contracts

    def _get_contract_and_frequencies_with_price_data(self) -> list:
        """

        :return: list of futures contracts as tuples
        """

        all_keynames = self._all_keynames_in_library()
        list_of_contract_and_freq_tuples = [
            from_key_to_freq_and_contract(keyname) for keyname in all_keynames
        ]

        return list_of_contract_and_freq_tuples

    def _all_keynames_in_library(self) -> list:
        return self.arctic_connection.get_keynames()

def from_key_to_freq_and_contract(keyname):
    first_split = keyname.split("/")
    if len(first_split)==1:
        frequency = MIXED_FREQ
        contract_str = keyname
    else:
        frequency = Frequency[first_split[0]]
        contract_str = first_split[1]

    return frequency, contract_str

def from_contract_and_freq_to_key(instrument_code,
                                  frequency: Frequency):
    if frequency is MIXED_FREQ:
        frequency_str = ""
    else:
        frequency_str = frequency.name+"/"

    return from_tuple_to_key([frequency_str, instrument_code])

def from_tuple_to_key(keytuple):
    return keytuple[0]+keytuple[1]