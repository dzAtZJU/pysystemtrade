import numpy as np
import pandas as pd
import math
from statsmodels.stats.moment_helpers import corr2cov, cov2corr
import riskfolio as rp

def optimize(assets_df, method):
    if method == 'naive equal':
        weights = len(assets_df.columns) * [1/len(assets_df.columns)]
        return weights
    elif method == 'classic markowitz':
        classic_optimizer = rp.Portfolio(assets_df)
        classic_optimizer.mu = assets_df.mean()
        classic_optimizer.cov = assets_df.cov()
        classic_weights = classic_optimizer.optimization().T.values.tolist()[0]
        return classic_weights
    else:
        raise Exception()

class ExpectedPortfolio:
    '''
    basic math of standard portofolio optimization
    '''

    def __init__(self, assets_mean, assets_cov=None, assets_corr=None, assets_std=None, name=None):
        self.name = name
        self.assets_mean = assets_mean
        if assets_cov is not None:
            self.assets_cov = assets_cov
            self.assets_corr = cov2corr(self.assets_cov)
        elif assets_corr is not None and assets_std is not None:
            self.assets_corr = assets_corr
            self.assets_cov = corr2cov(self.assets_corr, assets_std)

    def update_weights(self, new_weights):
        self.weights = new_weights

    def diversification_multiplier(self):
        '''
        risk lowering ratio from target risk
        '''

        return 1 / math.sqrt(np.dot(np.dot(self.assets_corr, self.weights), self.weights))

    def mean(self):
        return np.dot(self.assets_mean, self.weights)

    def var(self):
        return np.dot(np.dot(self.assets_cov, self.weights), self.weights)

    def std(self):
        return math.sqrt(self.var())

    def sharpe(self):
        return self.mean() / self.std()

    def geometric_mean(self):
        '''
        Approximation
        -------------
        Assumption
            A1. no skew or kurtosis
        '''

        return self.mean() - 0.5 * self.var()

    def geometric_sharpe(self):
        '''
        Approximation
        -------------
        '''

        return self.geometric_mean() / self.std()

    def describe(self, annualize = True):
        se = pd.Series([self.mean(), self.std(), self.sharpe(), self.geometric_sharpe(), self.diversification_multiplier()],
        index=['mean', 'std', 'sharpe', 'geo_sharpe', 'diversification multiplier'], name=self.name)
        if annualize:
            se  *= [252, 16, 16, 16, 1]
        
        styles = [
            dict(selector="caption",props=[("font-size", "125%")]),
            dict(selector="th",props=[("font-family", "Bradley Hand")]),
            dict(selector="td",props=[("font-family", "Bradley Hand")])
            ]

# Bradley Hand'
        return  se.to_frame().T.style.set_caption('summary statistics').set_table_styles(styles)

    def weightsPlot(self):
        geometric_mean_list = []
        std_list = []
        geometric_sharpe_list = []
        for weights in [[i,1-i] for i in np.arange(0, 1, 0.1)]:
            self.updaet_weights(weights)
            geometric_mean_list.append(self.geometric_mean())
            std_list.append(self.std())
            geometric_sharpe_list.append(self.geometric_sharpe())

        import matplotlib.pyplot as plt
        pd.DataFrame(
            {
                'geometric_mean': geometric_mean_list,
                'std': std_list,
                'geometric_sharpe': geometric_sharpe_list
            }           
        ).plot(secondary_y = ['geometric_mean'], legend=True, figsize=(15,8))

    @classmethod
    def diversification_multiplier_plot(cls, target_mean, target_std):
        _dict = {}
        for corr in [0, 0.5, 0.9]:
            for weights_pattern in [[1], [1,2,4]]:
                diversification_multiplier_list = []
                for n in range(1, 10):
                    means = np.ones(n) * target_mean
                    stds = np.ones(n) * target_std
                    corrs = np.ones((n,n)) * corr
                    np.fill_diagonal(corrs, 1)
                    p = ExpectedPortfolio(means, corr2cov(corrs, stds))
                    weights = pd.Series(weights_pattern).sample(n, replace=True)
                    weights = weights / weights.sum()
                    p.update_weights(weights)
                    diversification_multiplier_list.append(p.diversification_multiplier())
                _dict['corr={} weights pattern={}'.format(corr, weights_pattern)] = pd.Series(diversification_multiplier_list)
        pd.DataFrame(_dict).plot()

    @classmethod
    def similar_assets_effect(cls, mean, std, corr):
        mean_list = []
        geometric_mean_list = []
        geometric_sharpe_list = []
        std_list = []
        for n in range(1, 10):
            means = np.ones(n) * mean
            stds = np.ones(n) * std
            corrs = np.ones((n,n)) * corr
            np.fill_diagonal(corrs, 1)
            p = ExpectedPortfolio(means, corr2cov(corrs, stds))
            p.update_weights(np.ones(n) / n)
            mean_list.append(p.mean())
            geometric_mean_list.append(p.geometric_mean())
            std_list.append(p.std())
            geometric_sharpe_list.append(p.geometric_sharpe())
        
        before = geometric_mean_list[0]
        after = geometric_mean_list[-1]
        print('geometric_mean: {} * {} = {}'.format(before, after/before, after))

        pd.DataFrame(
            {
                'geometric_mean': geometric_mean_list,
                # 'std': std_list,
                'geometric_sharpe': geometric_sharpe_list,
                # 'mean': mean_list
            }           
        ).plot(secondary_y = ['std', 'geometric_sharpe'], legend=True, figsize=(15,8))