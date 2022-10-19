from paper.sysdata.spot_prices import (
    spotPricesData
)
from paper.sysobjects.spot_prices import spotPrices
from sysdata.arctic.arctic_connection import arcticData
from syslogdiag.log_to_screen import logtoscreen
import pandas as pd

ADJPRICE_COLLECTION = "spot_prices"


class arcticSpotPricesData(spotPricesData):
    """
    Class to read / write multiple futures price data to and from arctic
    """

    def __init__(self, mongo_db=None, log=logtoscreen("arcticFuturesAdjustedPrices")):

        super().__init__(log=log)

        self._arctic = arcticData(ADJPRICE_COLLECTION, mongo_db=mongo_db)

    def __repr__(self):
        return repr(self._arctic)

    @property
    def arctic(self):
        return self._arctic

    def get_list_of_instruments(self) -> list:
        # from sysdata.csv.csv_instrument_data import csvFuturesInstrumentData

        # data_in = csvFuturesInstrumentData('paper.data.spots.csvconfig')
        # return data_in.get_list_of_instruments()
        return self.arctic.get_keynames()
     
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
