from http.client import PRECONDITION_REQUIRED
import os,sys
import pandas as pd

def 

inputDir = r'/Users/weiranzhou/Code/pysystemtrade/sysinit/china/ct_adjusted_prices'
outdir = r'/Users/weiranzhou/Code/pysystemtrade/sysinit/china/adjusted_prices'

def import_day_data():
    for file in os.listdir(inputDir):
        if 'xlsx' not in file:
            continue

        fp = os.path.join(inputDir, file)
        csv = pd.read_excel(fp, parse_dates=['tr_date'])
        
        csv = csv[['tr_datetime', 'tr_the_close_price']]
        csv.columns = ['DATETIME', 'price']

        instrument = file.split('_')[0]
        csv.to_csv(os.path.join(outdir, instrument + '.csv'), index=False)
        print(instrument)

import_day_data()