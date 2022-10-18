from syscore.pdutils import pd_readcsv
from sysdata.csv.csv_futures_contract_prices import ConfigCsvFuturesPrices
from sysdata.csv.csv_adjusted_prices import csvFuturesAdjustedPricesData
import os
from syscore.fileutils import (
    files_with_extension_in_resolved_pathname,
    get_resolved_pathname,
)

barchart_csv_config = ConfigCsvFuturesPrices(
    input_date_index_name="Date",
    input_skiprows=0,
    input_skipfooter=0,
    input_column_mapping=dict(
        OPEN="Mid", HIGH="High", LOW="Low", FINAL="Last", VOLUME="Volume"
    ),
)

def strip_file_names(pathname, outpath):
    # These won't have .csv attached
    resolved_pathname = get_resolved_pathname(pathname)
    file_names = files_with_extension_in_resolved_pathname(resolved_pathname)
    writer = csvFuturesAdjustedPricesData(outpath)
    for filename in file_names:
        print(filename)
        new_full_name = os.path.join(resolved_pathname, filename+'.csv')
        csv = pd_readcsv(new_full_name, barchart_csv_config.input_date_index_name, input_column_mapping=barchart_csv_config.input_column_mapping)
        csv = csv.FINAL.sort_index()
        writer.add_adjusted_prices(filename, csv, ignore_duplication=True)

def transfer_barchart_prices_to_arctic(datapath, outpath):
    strip_file_names(datapath, outpath)
    # init_arctic_with_csv_futures_contract_prices(
    #     datapath, csv_config=barchart_csv_config
    # )


if __name__ == "__main__":
    input("Will overwrite existing prices are you sure?! CTL-C to abort")
    # modify flags as required
    datapath = "paper.sysinit.raw"
    outpath = "paper.data.spot"
    transfer_barchart_prices_to_arctic(datapath, outpath)
