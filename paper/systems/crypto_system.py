"""
This is a futures system

A system consists of a system, plus a config

"""
from syscore.objects import arg_not_supplied

from sysdata.config.configdata import Config
from sysproduction.data.control_process import get_strategy_class_object_config
from systems.forecasting import Rules
from systems.basesystem import System
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from paper.systems.rawdata import RawData
from paper.systems.positionsizing import PositionSizing
from systems.portfolio import Portfolios
from paper.systems.accounts.accounts_stage import perpetualsAccount
from sysproduction.data.sim_data import get_sim_data_object_for_production


def perpetuals_system(
    data=arg_not_supplied,
    config=arg_not_supplied,
    trading_rules=arg_not_supplied,
    log_level="on",
):
    """

    :param data: data object (defaults to reading from csv files)
    :type data: sysdata.data.simData, or anything that inherits from it

    :param config: Configuration object (defaults to futuresconfig.yaml in this directory)
    :type config: sysdata.configdata.Config

    :param trading_rules: Set of trading rules to use (defaults to set specified in config object)
    :type trading_rules: list or dict of TradingRules, or something that can be parsed to that

    :param log_level: How much logging to do
    :type log_level: str


    >>> system=futures_system(log_level="off")
    >>> system
    System with stages: accounts, portfolio, positionSize, rawdata, combForecast, forecastScaleCap, rules
    >>> system.rules.get_raw_forecast("EDOLLAR", "ewmac2_8").dropna().head(2)
                ewmac2_8
    1983-10-10  0.695929
    1983-10-11 -0.604704

                ewmac2_8
    2015-04-21  0.172416
    2015-04-22 -0.477559
    >>> system.rules.get_raw_forecast("EDOLLAR", "carry").dropna().head(2)
                   carry
    1983-10-10  0.952297
    1983-10-11  0.854075

                   carry
    2015-04-21  0.350892
    2015-04-22  0.350892
    """

    if data is arg_not_supplied:
        data = get_sim_data_object_for_production()

    if config is arg_not_supplied:
        config = Config('paper.systems.crypto.yaml')

    rules = Rules(trading_rules)

    system = System(
        [
            perpetualsAccount(),
            Portfolios(),
            PositionSizing(),
            RawData(),
            ForecastCombine(),
            ForecastScaleCap(),
            rules,
        ],
        data,
        config,
    )

    system.set_logging_level(log_level)

    return system


if __name__ == "__main__":
    perpetuals_system()