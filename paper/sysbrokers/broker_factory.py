from paper.sysbrokers.okx_spot_price_data import okxSpotPriceData
from syscore.objects import missing_data, resolve_function
from sysdata.config.production_config import get_production_config
from sysdata.data_blob import dataBlob

def get_broker_class_list(data: dataBlob):
    """
    Returns a list of classes that are specific to the broker being used.
    IB classes are returned by default. If you would like to use a different
    broker, then create a custom get_class_list() function in your private
    directory and specify the function name in private_config.yaml under the
    field name: broker_factory_func
    """
    config = data.config

    broker_factory_func = config.get_element_or_missing_data('broker_factory_func')

    get_class_list = resolve_function(broker_factory_func)

    broker_class_list = get_class_list()

    return broker_class_list


def get_crypto_exchange_class_list():
    return [
        okxSpotPriceData
    ]
