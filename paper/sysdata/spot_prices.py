"""
Adjusted prices:

- back-adjustor
- just adjusted prices

"""

from sysdata.base_data import baseData
from paper.sysobjects.spot_prices import spotPrices

USE_CHILD_CLASS_ERROR = "You need to use a child class of futuresAdjustedPricesData"


class spotPricesData(baseData):
    """
    Read and write data class to get adjusted prices

    We'd inherit from this class for a specific implementation

    """

    def __repr__(self):
        return USE_CHILD_CLASS_ERROR

    def keys(self):
        return self.get_list_of_instruments()

    def is_code_in_data(self, instrument_code: str) -> bool:
        if instrument_code in self.get_list_of_instruments():
            return True
        else:
            return False

    def add_spot_prices(
        self,
        instrument_code: str,
        adjusted_price_data: spotPrices,
        ignore_duplication: bool = False,
    ):
        if self.is_code_in_data(instrument_code):
            if ignore_duplication:
                pass
            else:
                self.log.error(
                    "There is already %s in the data, you have to delete it first"
                    % instrument_code,
                    instrument_code=instrument_code,
                )

        self._add_spot_prices_without_checking_for_existing_entry(
            instrument_code, adjusted_price_data
        )

        self.log.terse(
            "Added data for instrument %s" % instrument_code,
            instrument_code=instrument_code,
        )

    def get_spot_prices(self, instrument_code: str) -> spotPrices:
        if self.is_code_in_data(instrument_code):
            adjusted_prices = self._get_spot_prices_without_checking(
                instrument_code
            )
        else:
            adjusted_prices = spotPrices.create_empty()
        return adjusted_prices

    def _add_spot_prices_without_checking_for_existing_entry(
        self, instrument_code: str, adjusted_price_data: spotPrices
    ):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def get_list_of_instruments(self) -> list:
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def _get_spot_prices_without_checking(
        self, instrument_code: str
    ) -> spotPrices:
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)
