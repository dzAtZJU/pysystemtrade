from paper.sysbrokers.ccxt.ccxt_perpetuals_price_data import ccxtPerpetualsPriceData
from paper.sysbrokers.ccxt.ccxt_capital_data import ccxtCapitalData

def get_broker_class_list():
    return [
        ccxtPerpetualsPriceData,
        ccxtCapitalData
    ]
