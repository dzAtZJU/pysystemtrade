from syscore.constants import arg_not_supplied

from paper.sysdata.sim.db_perpetuals_sim_data import dbPerpetualsSimData
from paper.sysdata.data_blob import dataBlob
from paper.sysdata.arctic.arctic_perpetual_prices import arcticPerpetualsPricesData
from sysdata.mongodb.mongo_futures_instruments import mongoFuturesInstrumentData

def get_sim_data_object_for_production(data=arg_not_supplied) -> dataBlob:
    # Check data has the right elements to do this
    if data is arg_not_supplied:
        data = dataBlob()

    data.add_class_list(
        [
            arcticPerpetualsPricesData,
            mongoFuturesInstrumentData,
        ]
    )

    return dbPerpetualsSimData(data)
