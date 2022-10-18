from systems.accounts.accounts_stage import Account
from ctse.sysdata.csv_ctse_historic_orders import (
    csvCTSEStrategyHistoricOrdersData
)
from sysobjects.instruments import instrumentCosts
from systems.accounts.pandl_calculators.pandl_using_fills import (
        pandlCalculationWithFills,
        merge_fill_prices_with_prices
    )
from systems.accounts.pandl_calculators.pandl_cash_costs import pandlCalculationWithCashCostsAndFills
import pandas as pd
from systems.accounts.curves.account_curve import accountCurve
from sysobjects.production.tradeable_object import instrumentStrategy

class ctseAccount(Account):
    @property
    def name(self):
        return "accounts"

    def _pandl_for_instrument_with_cash_costs(
        self,
        instrument_code: str,
        positions: pd.Series,
        delayfill: bool = True,
        roundpositions: bool = True,
    ) -> accountCurve:

        if not roundpositions:
            self.log.warn(
                "Using roundpositions=False with cash costs may lead to inaccurate costs (fixed costs, eg commissions will be overstated!!!"
            )

        value_of_price_point = self.get_value_of_block_price_move(instrument_code)
        capital = self.get_notional_capital()

        instrument_strategy = instrumentStrategy('DMA_LONG_1_D', instrument_code)
        fills = csvCTSEStrategyHistoricOrdersData().get_fills_history_for_instrument_strategy(instrument_strategy)

        price = self.get_daily_price(instrument_code)
        price = merge_fill_prices_with_prices(price, fills)
        price = price.shift(-1)

        pandl_calculator = pandlCalculationWithCashCostsAndFills(
            price,
            raw_costs=instrumentCosts(),
            positions=positions,
            capital=capital,
            value_per_point=value_of_price_point,
            delayfill=delayfill,
            roundpositions=roundpositions,
            rolls_per_year=1,
        )

        account_curve = accountCurve(pandl_calculator, weighted=True)

        return account_curve

    def fills(self, instrument_code):
        instrument_strategy = instrumentStrategy('DMA_LONG_1_D', instrument_code)
        fills = csvCTSEStrategyHistoricOrdersData().get_fills_history_for_instrument_strategy(instrument_strategy)
        return fills