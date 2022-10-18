import pandas as pd

def holdl(price):
    r =  pd.Series(([1,1,1,1,1,1,1,1,1,1] *int(( len(price)/9)))[:len(price)], index=price.index)
    return r