from sysdata.sim.csv_futures_sim_data import csvFuturesSimData
from sysdata.config.configdata import Config

from systems.forecasting import Rules
from systems.basesystem import System
from ctse.systems.forecast_combine import ctseForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from systems.positionsizing import PositionSizing
from systems.portfolio import Portfolios
from paper.accounts_stage import paperAccount
from paper.rawdata import paperRawData


def simplesystem(data=None, config=None, log_level="on"):
    """
    Example of how to 'wrap' a complete system
    """
    if config is None:
        config = Config("paper.simplesystemconfig.yaml")
    if data is None:
        data = csvFuturesSimData(csv_data_paths=dict(
            csvFuturesAdjustedPricesData='paper.data.spot',
            csvFuturesInstrumentData='paper.data.csvconfig'
        ))

    my_system = System(
        [
            paperAccount(),
            Portfolios(),
            PositionSizing(),
            ctseForecastCombine(),
            ForecastScaleCap(),
            Rules(),
            paperRawData()
        ],
        data,
        config,
    )

    my_system.set_logging_level(log_level)

    return my_system

if __name__ == '__main__':
    sys = simplesystem()
    r = sys.portfolio.get_unsmoothed_raw_instrument_weights()
    print(r)
