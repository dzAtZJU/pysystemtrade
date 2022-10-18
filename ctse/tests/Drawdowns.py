import numpy as np
from pandas import DataFrame,Series

class Drawdowns:
    def __init__(self, csv, datetimeTag, navTag):
        navs = np.array(csv[navTag])
        peak_nav = np.fmax.accumulate(navs, axis=0) 
        drawdown = (navs - peak_nav) / peak_nav

        groupIndex = Series(peak_nav).diff().ne(0).cumsum()
        df = DataFrame({'datetime':np.array(csv[datetimeTag]), 'peak nav':peak_nav, 'dd':drawdown, 'groupIndex': groupIndex})
        mddGroups = df.groupby('groupIndex')
        for _, group in mddGroups:
            df.loc[group.index, 'group mdd'] = group['dd'].min()
            df.loc[group['dd'].idxmin(), 'group mdd happens'] = 1
        self.groups = df
    
    def topN(self, n):
        r = self.groups.groupby('groupIndex').agg(min)['dd'].nsmallest(n)
        return list(np.array(r))