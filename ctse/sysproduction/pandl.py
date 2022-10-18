from ctse.sysdata.csv_ctse_historic_orders import (
    csvCTSEStrategyHistoricOrdersData
)
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.production.tradeable_object import instrumentStrategy
from systems.basesystem import System
from ctse.systems.ct_system import ct_system
from systems.accounts.pandl_calculators.pandl_using_fills import (
        pandlCalculationWithFills
    )

def get_pandl_series_for_strategy_instrument(
    system:System, instrument_strategy: instrumentStrategy
):
    print("Data for %s" % (instrument_strategy))
    instrument_code = instrument_strategy.instrument_code
    strategy_name = instrument_strategy.strategy_name

    # fx = get_fx_series_for_instrument(data, instrument_code)

    # diag_instruments = diagInstruments(data)
    value_per_point = system.data.db_futures_instrument_data.get_instrument_data(instrument_code).meta_data.Pointsize

    positions = system.positionSize.get_subsystem_position(instrument_code)
        
    prices = system.data.daily_prices(instrument_code)

    capital = system.accounts.get_notional_capital()

    fills = csvCTSEStrategyHistoricOrdersData().get_fills_history_for_instrument_strategy(instrument_strategy)

    calculator = pandlCalculationWithFills.using_positions_and_prices_merged_from_fills(
        prices,
        positions=positions,
        fills=fills,
        capital=capital,
        value_per_point=value_per_point,
    )

    return  calculator

system = ct_system()
instrument_strategy = instrumentStrategy(
            instrument_code='J', strategy_name='dma_long_1_D'
        )
cal = get_pandl_series_for_strategy_instrument(system, instrument_strategy)
r = cal.pandl_in_base_currency()
print(r.cumsum())