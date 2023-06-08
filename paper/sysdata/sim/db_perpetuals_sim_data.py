"""
Get data from mongo and arctic used for futures trading

"""

from syscore.constants import arg_not_supplied

from paper.sysdata.arctic.arctic_perpetual_prices import arcticPerpetualsPricesData
# from sysdata.mongodb.mongo_futures_instruments import mongoFuturesInstrumentData
# from sysdata.mongodb.mongo_roll_data import mongoRollParametersData
from sysdata.data_blob import dataBlob
from paper.sysdata.sim.perpetuals_sim_data_with_data_blob import genericBlobUsingPerpetualsSimData

from syslogdiag.log_to_screen import logtoscreen


class dbPerpetualsSimData(genericBlobUsingPerpetualsSimData):
    def __init__(
        self, data: dataBlob = arg_not_supplied, log=logtoscreen("dbPerpetualsSimData")
    ):

        if data is arg_not_supplied:
            data = dataBlob(
                log=log,
                class_list=[
                    arcticPerpetualsPricesData,
                    # mongoFuturesInstrumentData,
                ],
            )

        super().__init__(data=data)

    def __repr__(self):
        return "dbFuturesSimData object with %d instruments" % len(
            self.get_instrument_list()
        )


if __name__ == "__main__":
    import doctest

    doctest.testmod()
