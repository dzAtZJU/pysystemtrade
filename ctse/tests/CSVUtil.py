from operator import itemgetter
import pandas as pd
import numpy as np
from collections import deque

def groupByConsecutive(tag, df):
    return df.groupby(df[tag].diff().ne(0).cumsum())

def groupTagByConsecutive(tag, df):
    return (df[tag].diff().ne(0).cumsum())

def groupByDate(date_tag, df):
    return df.groupby(pd.to_datetime(df[date_tag]).dt.date)

def isAfterNoonFirst(date_tag, df):
    return groupByDate(date_tag, df)[date_tag].transform(lambda c:(pd.to_datetime(c).dt.hour > 12) & (pd.to_datetime(c).shift(1).dt.hour <= 12))

def stateBoundary(tag, df):
    return (df[tag] == 1) & ((df[tag].shift(1)) == 0)

def years(datetimeTag, df):
    return months(datetimeTag, df) / 12
     
def months(tag, df):
    st = pd.Timestamp(df[tag].iat[0])
    et = pd.Timestamp(df[tag].iat[-1])
    return (et - st) / np.timedelta64(1, 'M')

def recentYears(n, tag, df):
    days = df.groupby(pd.to_datetime(df[tag]).dt.date)
    days = map(itemgetter(1), days)
    return pd.concat(deque(days, maxlen=252*n))
    
def groupByYear(datetimeTag, df):
    return df.groupby(pd.to_datetime(df[datetimeTag]).dt.year)

def byFreq(freq, df: pd.DataFrame, dateTimeColumn):
    df = df.copy()
    df[dateTimeColumn] = pd.to_datetime(df[dateTimeColumn])
    df = df.set_index(dateTimeColumn)
    return df.groupby(pd.Grouper(freq=freq))