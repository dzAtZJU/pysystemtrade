from syscore.objects import arg_not_supplied

from sysdata.csv.csv_futures_contract_prices import csvFuturesContractPriceData, ConfigCsvFuturesPrices
from sysobjects.contracts import futuresContract

datapath = 'sysinit.china.formatted'
config = csv_config = ConfigCsvFuturesPrices(
    input_date_index_name = "DATETIME")

def init_arctic_with_csv_futures_contract_prices(
    datapath: str, csv_config=arg_not_supplied
):
    csv_prices = csvFuturesContractPriceData(datapath)
    input(
        "WARNING THIS WILL ERASE ANY EXISTING ARCTIC PRICES WITH DATA FROM %s ARE YOU SURE?! (CTRL-C TO STOP)"
        % csv_prices.datapath
    )

    instrument_codes = csv_prices.get_list_of_instrument_codes_with_merged_price_data()
    instrument_codes.sort()
    for instrument_code in instrument_codes:
        init_arctic_with_csv_futures_contract_prices_for_code(
            instrument_code, datapath, csv_config=csv_config
        )


def init_arctic_with_csv_futures_contract_prices_for_code(
    instrument_code: str, datapath: str, csv_config=arg_not_supplied
):
    csv_prices = csvFuturesContractPriceData(datapath, config=csv_config)
    
    csv_price_dict = csv_prices.get_merged_prices_for_instrument(instrument_code)

    print("Have .csv prices for the following contracts:")
    print(instrument_code)
    print(sorted(csv_price_dict.keys()))

    for contract_date_str, prices_for_contract in csv_price_dict.items():
        print("Processing %s" % contract_date_str)
        print(".csv prices are \n %s" % str(prices_for_contract))

if __name__ == "__main__":
    init_arctic_with_csv_futures_contract_prices(datapath)