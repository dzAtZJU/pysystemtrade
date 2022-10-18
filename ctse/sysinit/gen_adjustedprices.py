from sysobjects.adjusted_prices import futuresAdjustedPrices, _panama_stitch
from sysdata.csv.csv_adjusted_prices import csvFuturesAdjustedPricesData
from sysdata.csv.csv_multiple_prices import csvFuturesMultiplePricesData
from sysobjects.multiple_prices import futuresMultiplePrices
from syscore.fileutils import  files_with_extension_in_pathname

'''
use panama stiching
'''

if __name__ == '__main__':
    csv_multiple_data_path = 'ctse.data.multiple_prices_csv'
    csv_adjust_data_path = 'ctse.data.adjusted_prices_csv'
    csv_multiple_prices = csvFuturesMultiplePricesData(csv_multiple_data_path)
    csv_adjust_prices = csvFuturesAdjustedPricesData(csv_adjust_data_path)

    for only in  files_with_extension_in_pathname(csv_multiple_data_path, 'csv'):
        print(only)
        mp = csv_multiple_prices.get_multiple_prices(only)
        ap= _panama_stitch(mp)
        csv_adjust_prices.add_adjusted_prices(only, ap, ignore_duplication=True)