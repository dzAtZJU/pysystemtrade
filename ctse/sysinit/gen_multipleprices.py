import os,sys
import re
import pandas as pd
from sysdata.csv.csv_multiple_prices import csvFuturesMultiplePricesData
from syscore.fileutils import files_with_extension_in_pathname, get_filename_for_package

'''
use open price
'''

def process_multiple_prices_all_instruments(
    csv_contract_path, csv_multiple_data_path, only=None
):
    csv_multiple_prices = csvFuturesMultiplePricesData(csv_multiple_data_path)
    
    for file in files_with_extension_in_pathname(csv_contract_path, 'xlsx'):
        fp = get_filename_for_package(csv_contract_path, file + '.xlsx')
        ins = file.split('_')[0]
        if (only is not None) and (only is not  ins):
            continue
        print(ins)
        csv = pd.read_excel(fp, header=None, engine='openpyxl').iloc[:, 1:]
        csv.columns = [
            'DATETIME', 'PRICE_CONTRACT', 'OPEN', 'CLOSE', 'HIGH', 'LOW',
            'VOLUME', 'v1', 'v2', 't1', 't2', 't3', 'Contract1', 'OPEN1', 'CLOSE1', 'HIGH1', 'LOW1', 't4'
            ]
        csv = csv.set_index('DATETIME')
        csv = csv[['PRICE_CONTRACT', 'OPEN', 'OPEN1', 'CLOSE', 'CLOSE1']]
        csv.columns = ['PRICE_CONTRACT', 'PRICE', 'FORWARD', 'CLOSE', 'FORWARD_CLOSE']

        def t(name):
            ins, cont, _ = re.split('(\d+)', name)
            cont = '20' + cont
            if len(cont) == 6:
                cont += '00' 
            return cont
        csv.loc[:, 'PRICE_CONTRACT'] = csv['PRICE_CONTRACT'].apply(t)

        previous_row = csv.iloc[0, :]
        for dateindex in csv.index[1:]:
            current_row = csv.loc[dateindex, :]
            if current_row.FORWARD is not None:
                csv.loc[previous_row.name, 'FORWARD'] = current_row.FORWARD
                csv.loc[dateindex, 'FORWARD'] = None
                csv.loc[previous_row.name, 'FORWARD_CLOSE'] = current_row.FORWARD_CLOSE
                csv.loc[dateindex, 'FORWARD_CLOSE'] = None

            previous_row = current_row
        
        csv.loc[:, 'CARRY'] = None
        csv.loc[:, 'CARRY_CONTRACT'] = None
        csv.loc[:, 'FORWARD_CONTRACT'] = None

        csv_multiple_prices.add_multiple_prices(ins, csv, ignore_duplication=True)

if __name__ == '__main__':
    csv_multiple_data_path = 'ctse.data.multiple_prices_csv'
    inputDir = 'ctse.sysinit.pt_multiple_prices'
    only = None

    process_multiple_prices_all_instruments(inputDir, csv_multiple_data_path, only)

    # from sysobjects.adjusted_prices import futuresAdjustedPrices, ct_stitch
    # from sysdata.csv.csv_adjusted_prices import csvFuturesAdjustedPricesData
    # from sysobjects.multiple_prices import futuresMultiplePrices
    # for ins in ['J']:
    #     p = futuresMultiplePrices(pd.read_csv(multipleDir + '/{}.csv'.format(ins), index_col='DATETIME'))
    #     hc = ct_stitch(p)
    #     print(hc)
