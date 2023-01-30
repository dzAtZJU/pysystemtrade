from syscore.pdutils import pd_readcsv
from syscore.dateutils import Frequency
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from paper.sysdata.arctic.arctic_perpetual_prices import arcticPerpetualsPricesData
from sysobjects.futures_per_contract_prices import futuresContractPrices
import os
import numpy as np
import pandas as pd

from syscore.fileutils import (
    files_with_extension_in_resolved_pathname,
    get_resolved_pathname,
)

datapath = "paper.sysinit.data.binance"

barchart_csv_config = ConfigCsvFuturesPrices(
    input_date_index_name="date",
    input_skiprows=0,
    input_skipfooter=0,
    input_column_mapping=dict(
        OPEN="OPEN", HIGH="HIGH", LOW="LOW", FINAL="FINAL", VOLUME="VOLUME"
    ),
)

def strip_file_names(pathname, outpath):
    # These won't have .csv attached
    resolved_pathname = get_resolved_pathname(pathname)
    file_names = files_with_extension_in_resolved_pathname(resolved_pathname)
    arctic_prices = arcticPerpetualsPricesData()
    for filename in file_names:
        print(filename)
        fre, ins = filename.split("_")
        fre = Frequency[fre]
        new_full_name = os.path.join(resolved_pathname, filename+'.csv')
        csv = futuresContractPrices(pd_readcsv(new_full_name, barchart_csv_config.input_date_index_name, input_column_mapping=barchart_csv_config.input_column_mapping))
        
        assert (pd.Series(csv.index).diff().dropna() / np.timedelta64(1,'h') == 1).all()
        
        arctic_prices.write_prices_at_frequency(ins, csv, fre)
        written_prices = arctic_prices.get_prices_at_frequency(ins, fre)
        print("Read back prices are \n %s" % str(written_prices))

def transfer_barchart_prices_to_arctic(datapath, outpath):
    strip_file_names(datapath, outpath)

if __name__ == "__main__":
    input("Will overwrite existing prices are you sure?! CTL-C to abort")
    # modify flags as required
    outpath = "paper.data.perpetuals"
    transfer_barchart_prices_to_arctic(datapath, outpath)
