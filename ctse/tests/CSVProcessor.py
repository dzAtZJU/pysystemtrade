import pandas as pd
import numpy as np
from Measures import Measures
import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__),'../../Common/config'))
from ProjectEnvironment import ProjectEnvironment
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))
from MarketNavs import MarketCSVs

class FinalProcessor:
    def __init__(self, marketsCSV, sectorsCSV, long, short):
        """
        read with index
        """

        self.csvs = {}
        self.long = long
        self.short = short
        if self.long:
            self.csvs['long'] = MarketCSVs.longCSVs() 
        if self.short:
            self.csvs['short'] = MarketCSVs.shortCSVs()         
        self.marketsCSV = marketsCSV
        self.sectorsCSV = sectorsCSV

    def processMarketsCSV(self) -> pd.DataFrame:
        strategies = []
        if self.long:
            strategies.append('long')
        if self.short:
            strategies.append('short')

        leadingRowNames = ['权重']
        _weights = [x for xs in ProjectEnvironment.productWeightList for x in xs]
        _markest = [x for xs in ProjectEnvironment.productCodeList for x in xs]
        _mw = dict(zip(_markest, _weights))
        self.marketsCSV.loc[leadingRowNames[0]] = [np.nan] + [_mw[market] for market in self.marketsCSV.columns[1:]]

        avgRowNames = []
        for strategy in strategies:
            r1 = '{}买卖操作次数'.format(strategy)
            r2 = '{}持仓时间(年)'.format(strategy)
            r3 = '{}交易年数'.format(strategy)
            for market in self.marketsCSV.columns[1:]:
                csv = pd.read_csv(self.csvs[strategy][market], encoding='GBK')
                ms = Measures(csv, 'tr_datetime', 'tr_nav_of_product', 'tr_operate_flag')
                self.marketsCSV.loc[r1, market] = ms.operateCount()
                self.marketsCSV.loc[r2, market] = ms.holdingTime()
                self.marketsCSV.loc[r3, market] = ms.years
            
            avgRowNames += [r3, r1, r2]

        if len(strategies) == 1:
            strategy = strategies[0]
            r3 = '{}交易年数'.format(strategy)
            r4 = '{}平均每年买卖操作次数'.format(strategy)
            r5 = '{}平均每年持仓时间(年)'.format(strategy)
            self.marketsCSV.loc[r4, :] = self.marketsCSV.loc[r4.replace('平均每年', ''), :] / self.marketsCSV.loc[r3, :]
            self.marketsCSV.loc[r5, :] = self.marketsCSV.loc[r5.replace('平均每年', ''), :] / self.marketsCSV.loc[r3, :]

            r6 = '{}满仓年化'.format(strategies[0])
            self.marketsCSV.loc[r6, :] = (1 + self.marketsCSV.loc['年化', :]) ** (1/self.marketsCSV.loc[r5, :]) - 1
            avgRowNames = [r6] +  [r4, r5] + avgRowNames

        bothRows = []
        if self.long and self.short:
            r1 = '买卖操作次数'
            r2 = '持仓时间(年)'
            r3 = '交易年数'
            r4 = '平均每年买卖操作次数'
            r5 = '平均每年持仓时间(年)'
            r6 = '满仓年化'
            self.marketsCSV.loc[r1, :] = self.marketsCSV.loc['long'+r1, :] + self.marketsCSV.loc['short'+r1, :] 
            self.marketsCSV.loc[r2, :] = self.marketsCSV.loc['long'+r2, :] + self.marketsCSV.loc['short'+r2, :]
            self.marketsCSV.loc[r3, :] = self.marketsCSV.loc[['long'+r3,'short'+r3], :].sum(axis=0, skipna=False)/2 
            self.marketsCSV.loc[r4, :] = self.marketsCSV.loc[r1, :] / self.marketsCSV.loc[r3, :]
            self.marketsCSV.loc[r5, :] = self.marketsCSV.loc[r2, :] / self.marketsCSV.loc[r3, :]
            self.marketsCSV.loc[r6, :] = (1 + self.marketsCSV.loc['年化', :]) ** (1/self.marketsCSV.loc[r5, :]) - 1
            bothRows += [r6, r4, r5, r3, r1, r2]

        intRows = filter(lambda x: type(x) is int, self.marketsCSV.index.values)
        strRows = filter(lambda x: type(x) is str, self.marketsCSV.index.values)
        strRows = filter(lambda x: x not in (avgRowNames + bothRows + leadingRowNames), strRows)

        if len(bothRows) > 0:
            return self.marketsCSV.reindex(list(intRows) + leadingRowNames + bothRows + list(strRows) + list(avgRowNames))
        else:
            return self.marketsCSV.reindex(list(intRows) + leadingRowNames + list(avgRowNames) + list(strRows))


    def processSectorsCSV(self) -> pd.DataFrame:
        def f1(strategy):
            rowNames = ['{}买卖操作次数'.format(strategy), '{}持仓时间(年)'.format(strategy)]
            for sector, markets in zip(ProjectEnvironment.tableTitleName[1:-1], ProjectEnvironment.productCodeList):
                for rowName in rowNames:
                    self.sectorsCSV.loc[rowName, sector] = self.marketsCSV.loc[rowName, markets].sum()
            for rowName in rowNames:
                self.sectorsCSV.loc[rowName, ProjectEnvironment.tableTitleName[-1]] = self.sectorsCSV.loc[rowName, ProjectEnvironment.tableTitleName[1:-1]].sum()

            return rowNames

        def f12():
            rowNames = ['买卖操作次数', '持仓时间(年)']
            for rowName in rowNames:
                self.sectorsCSV.loc[rowName, :] = self.sectorsCSV.loc[['long'+rowName, 'short'+rowName], :].sum(axis=0, skipna=False)


            avgRowNames = ['板块平均每年每品种买卖操作次数', '板块平均每年每品种持仓时间(年)']
            for sector, markets in zip(ProjectEnvironment.tableTitleName[1:-1], ProjectEnvironment.productCodeList):
                for avgRowName in avgRowNames:
                    rowName = avgRowName.replace('板块平均每年每品种', '')
                    self.sectorsCSV.loc[avgRowName, sector] = self.sectorsCSV.loc[rowName, sector] / self.marketsCSV.loc['交易年数', markets].sum()

            allYears = self.marketsCSV.loc['交易年数', ProjectEnvironment.productCodeTitleList[1:]].sum()
            for avgRowName in avgRowNames:
                rowName = avgRowName.replace('板块平均每年每品种', '')
                self.sectorsCSV.loc[avgRowName, ProjectEnvironment.tableTitleName[-1]] = self.sectorsCSV.loc[rowName, ProjectEnvironment.tableTitleName[1:-1]].sum() / allYears

            r = '满仓年化'
            self.sectorsCSV.loc[r, :] = (1 + self.sectorsCSV.loc['年化', :]) ** (1/self.sectorsCSV.loc['板块平均每年每品种持仓时间(年)', :]) - 1

            return [r] + avgRowNames + rowNames

        leadingRowNames = ['权重']
        _mw = dict(zip(ProjectEnvironment.tableTitleName[1:-1], ProjectEnvironment.blockWeight[0]))
        self.sectorsCSV.loc[leadingRowNames[0]] = [np.nan] + [_mw[bn] for bn in self.sectorsCSV.columns[1:-1]] + [np.nan]

        rows = []
        strategies = []
        if self.long:
            rows += f1('long')
            strategies.append('long')
        if self.short:
            rows += f1('short')
            strategies.append('short')
        if len(strategies) == 1:
            strategy = strategies[0]
            avgRowNames = ['{}板块平均每年每品种买卖操作次数'.format(strategy), '{}板块平均每年每品种持仓时间(年)'.format(strategy)]
            for sector, markets in zip(ProjectEnvironment.tableTitleName[1:-1], ProjectEnvironment.productCodeList):
                for avgRowName in avgRowNames:
                    rowName = avgRowName.replace('板块平均每年每品种', '')
                    self.sectorsCSV.loc[avgRowName, sector] = self.marketsCSV.loc[rowName, markets].sum() / self.marketsCSV.loc['{}交易年数'.format(strategy), markets].sum()

            allYears = self.marketsCSV.loc['{}交易年数'.format(strategy), ProjectEnvironment.productCodeTitleList[1:]].sum()
            for avgRowName in avgRowNames:
                rowName = avgRowName.replace('板块平均每年每品种', '')
                self.sectorsCSV.loc[avgRowName, ProjectEnvironment.tableTitleName[-1]] = self.sectorsCSV.loc[rowName, ProjectEnvironment.tableTitleName[1:-1]].sum() / allYears


            r6 = '{}满仓年化'.format(strategies[0])
            r5 = '{}板块平均每年每品种持仓时间(年)'.format(strategies[0])
            self.sectorsCSV.loc[r6, :] = (1 + self.sectorsCSV.loc['年化', :]) ** (1/self.sectorsCSV.loc[r5, :]) - 1
            rows = [r6] + avgRowNames + rows

        bothRows = []
        if self.long and self.short:
            bothRows = f12()

        intRows = filter(lambda x: type(x) is int, self.sectorsCSV.index.values)
        strRows = filter(lambda x: type(x) is str, self.sectorsCSV.index.values)
        strRows = filter(lambda x: x not in (rows + bothRows + leadingRowNames), strRows)

        if len(bothRows) > 0:
            return self.sectorsCSV.reindex(list(intRows) + leadingRowNames + bothRows + list(strRows) + list(rows))
        else:
            return self.sectorsCSV.reindex(list(intRows) + leadingRowNames + list(rows) + list(strRows))

class LastNavProcessor:
    def __init__(self, csv):
        self.csv = csv
        self.dateColumn = ProjectEnvironment.tableTitleName[0]
        self.navColumns = ProjectEnvironment.tableTitleName[1:]

        self.csv.loc[:, self.dateColumn] = pd.to_datetime(self.csv[self.dateColumn])

    def process(self) -> pd.DataFrame:
        results = {}

        for navColumn in self.navColumns:
            result = {}

            measures = Measures(pd.concat([self.csv[self.dateColumn], self.csv[navColumn]], axis=1), self.dateColumn, navColumn, None)
            
            result['夏普'] = measures.sharpe()
            result['卡尔玛'] = measures.calmar()
            result['日胜率'] = measures.periodWinRatio()
            result['年化'] = measures.cagr()
            result['平均回撤'] = measures._meanDD()

            mddTops = measures.mddTop5()
            for i in range(0,5):
                if i < len(mddTops): 
                    result['mdd{}'.format(i+1)] = mddTops[i]

            meanDrawdowns = measures.meanDrawdownByYear()
            result |= {'平均回撤{}'.format(k): v for k, v in meanDrawdowns.items()}


            mdds = measures.mddByYear()
            result |= {'最大回撤{}'.format(k): v for k, v in mdds.items()}

            result |= {'收益{}'.format(k): v for k, v in measures.returnByYear().items()}

            results[navColumn] = (result)

        df = pd.DataFrame(results)
        ddRownames = sorted((filter(lambda x: 'mdd' in x, df.index.values)))
        yearDDRownames = sorted((filter(lambda x: (('回撤' in x)) and ('2' in x), df.index.values)))
        yearReturnRownames = sorted((filter(lambda x: (('收益' in x)) and ('2' in x), df.index.values)))
        otherRows = sorted(list(set(df.index.values)-set(ddRownames + yearDDRownames + yearReturnRownames)), reverse=True)
        df = df.reindex(otherRows + ddRownames + yearDDRownames + yearReturnRownames)
        self.csv.loc[:, self.dateColumn] = self.csv[self.dateColumn].dt.strftime('%Y/%m/%d')
        return pd.concat([self.csv, df])

class PrdNavProcessor:
    def __init__(self, csv):
        self.csv = csv
        self.dateColumn = 'date'
        self.navColumns = self.csv.columns[1:]

        self.csv.loc[:, self.dateColumn] = pd.to_datetime(self.csv[self.dateColumn])
        self.csv.replace([0, '0'], np.nan, inplace=True)
    
    def process(self) -> pd.DataFrame:
        results = {}

        for navColumn in self.navColumns:
            df = pd.concat([self.csv[self.dateColumn], self.csv[navColumn]], axis=1)
            df = df.iloc[df[navColumn].first_valid_index():df[navColumn].last_valid_index(), :]

            result = {}
            measures = Measures(df, self.dateColumn, navColumn, None)
            result['夏普'] = measures.sharpe()
            result['卡尔玛'] = measures.calmar()
            result['日胜率'] = measures.periodWinRatio()
            result['年化'] = measures.cagr()
            result['平均回撤'] = measures._meanDD()

            mddTops = measures.mddTop5()
            for i in range(0,5):
                if i < len(mddTops): 
                    result['mdd{}'.format(i+1)] = mddTops[i]

            meanDrawdowns = measures.meanDrawdownByYear()
            result |= {'平均回撤{}'.format(k): v for k, v in meanDrawdowns.items()}

            mdds = measures.mddByYear()
            result |= {'最大回撤{}'.format(k): v for k, v in mdds.items()}

            result |= {'收益{}'.format(k): v for k, v in measures.returnByYear().items()}
            
            results[navColumn] = (result)
        
        df = pd.DataFrame(results)
        ddRownames = sorted((filter(lambda x: 'mdd' in x, df.index.values)))
        yearDDRownames = sorted((filter(lambda x: (('回撤' in x)) and ('2' in x), df.index.values)))
        yearReturnRownames = sorted((filter(lambda x: (('收益' in x)) and ('2' in x), df.index.values)))
        otherRows = sorted(list(set(df.index.values)-set(ddRownames + yearDDRownames + yearReturnRownames)), reverse=True)
        df = df.reindex(otherRows + ddRownames + yearDDRownames + yearReturnRownames)
        self.csv.loc[:, self.dateColumn] = self.csv[self.dateColumn].dt.strftime('%Y/%m/%d')
        return pd.concat([self.csv, df])


if __name__ == '__main__':
    csv = pd.read_csv(r'S:\业务团队\刘艳艳\20220509-做多条件对比\out-long-open-2\LAST\new_t_v2_prd_nav.csv', index_col=0, encoding='GBK').loc['最大回撤2018', ['IC', 'IF']]
    print(csv)
    # PrdNavProcessor(pd.read_csv(r'input/new_t_prd_nav.csv', encoding='GBK').iloc[:,1:]).process().to_csv('input/prd_test.csv', encoding='GBK')
