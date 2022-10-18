import pandas as pd
import numpy as np
import CSVUtil
from Drawdowns import Drawdowns
from TradingStats import TradingStats

class Measures:
    def __init__(self, csv, datetimeTag, navTag, operateTag):
        """

        Parameters
        ----------
        csv

        datetimeTag
            时间点列名
        navTag
            净值列名
        operateTag
            交易操作列名。可以传 None
        """

        self.csv = csv
        self.datetimeTag = datetimeTag
        self.navTag = navTag
        self.operateTag = operateTag
        self.datetimes = csv[datetimeTag]
        self.navs = csv[navTag]

        if (self.operateTag not in [None, '']):
            self.tradingStats = TradingStats(self.csv, self.navTag, self.operateTag)
        
        self.mddGroups = Drawdowns(self.csv, self.datetimeTag, self.navTag)

        self.groupByYear = CSVUtil.groupByYear(self.datetimeTag, self.csv)
        if len(self.groupByYear) > 1:
            self.measuresByYear = {}
            for year,group in self.groupByYear:
                self.measuresByYear[year] = Measures(group, self.datetimeTag, self.navTag, self.operateTag)

        self.months = CSVUtil.months(self.datetimeTag, self.csv)
        self.years = self.months / 12  

    def nav(self):
        """
        净值
        """

        return self.navs.iat[-1]

    def sharpe(self):
        """
        夏普：(日收益平均/日收益标准差)*sqrt(252)
        """

        dates = CSVUtil.groupByDate(self.datetimeTag, self.csv)

        returns = dates.last()[self.navTag] / dates.last()[self.navTag].shift(1) - 1
        return returns.mean() / returns.std() * np.sqrt(252)
    
    def calmar(self):
        """
        卡尔玛: 最近三年 - 复合年增长率/最大回撤
        """
        
        # newCSV = CSVUtil.recentYears(3, self.datetimeTag, self.csv)
        # newMeasures =  Measures(newCSV, self.datetimeTag, self.navTag, self.operateTag)
        # newMDD = newMeasures.mddTop5()[0]
        # return newMeasures.cagr() / abs(newMDD)
        return self.cagr() / abs(self.mddTop5()[0])

    def mddTop5(self):
        """
        前5个历史最大回撤

        Returns
        -------
        list        
        """

        return self._mddTopN(5)
    
    def meanDrawdownByYear(self):
        """
        每年的平均回撤: 年内所有行情点回撤值的平均值

        Returns
        -------
        map        
        """

        r = {}
        for year,_ in self.groupByYear:
            r[year] = self.measuresByYear[year]._meanDD()
        return r


    def mddByYear(self):
        """
        每年的最大回撤

        Returns
        -------
        map  
        """
        
        r = {}
        for year,_ in self.groupByYear:
            r[year] = self.measuresByYear[year]._mdd()
        return r

    def returnByYear(self):
        """
        每年的收益

        Returns
        -------
        map
        """

        r = {}
        for year,_ in self.groupByYear:
            r[year] = self.measuresByYear[year]._return()
        return r

    def periodWinRatio(self):
        """
        行情胜率：盈利的行情数/有净值变化的行情数
        """

        return (self.navs.diff() > 0).sum() / (self.navs.diff() != 0).sum()

    def operateCount(self):
        """交易操作次数，包括买卖"""

        if self.operateTag in [None, '']:
            return None

        return self.tradingStats.tradingCount() * 2

    def operateCountPerYear(self):
        """平均每年 operateCount"""

        return self.operateCount() / self.years

    def holdingTime(self):
        """持仓时间。单位：年"""

        if self.operateTag in [None, '']:
            return None

        return self.years * (self.csv[self.operateTag] >= 1).sum() / self.csv[self.operateTag].size

    def holdingTimePerYear(self):
        """平均每年 holdingTime"""

        return self.holdingTime() / self.years


    def cagrPerHoldingYear(self):
        """满仓年化"""

        return (1 + self.cagr()) ** (1/self.holdingTimePerYear()) - 1

    def returnPerTrade(self):
        """
        平均每笔交易收益: 类似于复合年增长率，计算复合每笔交易增长率
        """
        
        if self.operateTag in [None, '']:
            return None

        return (1+self.cagr()) ** (1/ self.tradingStats.tradingCount()) - 1

    
    def cagr(self):
        """
        复合年增长率：(1+总收益)**(12/总月数)-1
        """

        factor = 12/self.months
        ratio = self._return() + 1
        return ratio ** factor - 1

    def _mdd(self):
        return self._mddTopN(1)[0]
    
    def _mddTopN(self, n):
        return self.mddGroups.topN(n)

    def _meanDD(self):
        peak_nav = np.fmax.accumulate(self.navs, axis=0) 
        drawdown = (self.navs - peak_nav) / peak_nav
        return drawdown.mean()

    def _return(self):
        return self.navs.iat[-1]/self.navs.iat[0] - 1

if __name__ == '__main__':
    csv = pd.read_csv(r'D:\project\data\out\DMA\TA_120\fake2.csv', encoding='GBK')
    measures = Measures(csv, 'tr_datetime', 'tr_nav_of_product', 'tr_operate_flag')
    print('交易操作次数', measures.operateCount())
    print('持仓时间', measures.holdingTime())
    print('净值', measures.nav())
    print('夏普', measures.sharpe())
    print('卡尔玛', measures.calmar())
    print('年化', measures.cagr())
    print('满仓年化', measures.cagrPerHoldingYear())
    print('前5个历史最大回撤', measures.mddTop5())
    print('前5个历史最大回撤平均', np.mean(measures.mddTop5()))
    print('平均回撤', np.mean(measures._meanDD()))