from sysdata.config.configdata import Config

from systems.forecasting import Rules
from systems.basesystem import System
from ctse.systems.forecast_combine import ctseForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from ctse.systems.positionsizing import ctsePositionSizing
from systems.portfolio import Portfolios
from systems.accounts.accounts_stage import Account
from systems.rawdata import RawData


def simplesystem(data, config, log_level="on"):
    my_system = System(
        [
            Account(),
            Portfolios(),
            ctsePositionSizing(),
            ctseForecastCombine(),
            ForecastScaleCap(),
            Rules(),
            RawData(),
        ],
        data,
        Config(config),
    )

    my_system.set_logging_level(log_level)

    return my_system

if __name__ == '__main__':
    from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
    
    my_system = simplesystem(csvFuturesSimData(), 'paper.systems.simplesystemconfig.yaml')
    my_system.accounts.portfolio()