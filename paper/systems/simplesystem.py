from sysdata.config.configdata import Config
from syslogdiag.log_to_screen import logtoscreen

from systems.forecasting import Rules
from systems.basesystem import System
from ctse.systems.forecast_combine import ctseForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from ctse.systems.positionsizing import ctsePositionSizing
from systems.portfolio import Portfolios
from systems.accounts.accounts_stage import Account
from systems.rawdata import RawData


def simplesystem(data, config, log_level="on"):
    log = logtoscreen('base_system')
    log.set_logging_level(log_level)

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
        log=log
    )

    return my_system

if __name__ == '__main__':
    from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
    
    my_system = simplesystem(csvFuturesSimData(), 'paper.systems.china.yaml')
    my_system.config.instrument_weights = {
    'AP':1
    }
    my_system.accounts.portfolio()