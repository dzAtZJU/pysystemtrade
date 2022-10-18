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

class paperAccount(Account):
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

        raw_costs = self.get_raw_cost_data(instrument_code)

        price = self.get_daily_price(instrument_code)
        fx = self.get_fx_rate(instrument_code)
        value_of_price_point = self.get_value_of_block_price_move(instrument_code)

        capital = self.get_notional_capital()

        vol_normalise_currency_costs = self.config.vol_normalise_currency_costs

        pandl_calculator = pandlCalculationWithCashCostsAndFills(
            price,
            raw_costs=raw_costs,
            positions=positions,
            capital=capital,
            value_per_point=value_of_price_point,
            delayfill=delayfill,
            fx=fx,
            roundpositions=roundpositions,
            vol_normalise_currency_costs=vol_normalise_currency_costs,
            rolls_per_year=0
        )

        account_curve = accountCurve(pandl_calculator, weighted=True)

        return account_curve

    def _pandl_for_subsystem_with_cash_costs(
        self, instrument_code, delayfill=True, roundpositions=True
    ) -> accountCurve:

        raw_costs = self.get_raw_cost_data(instrument_code)
        price = self.get_daily_price(instrument_code)
        positions = self.get_buffered_subsystem_position(instrument_code)

        fx = self.get_fx_rate(instrument_code)

        value_of_price_point = self.get_value_of_block_price_move(instrument_code)

        capital = self.get_notional_capital()

        vol_normalise_currency_costs = self.config.vol_normalise_currency_costs

        pandl_calculator = pandlCalculationWithCashCostsAndFills(
            price,
            raw_costs=raw_costs,
            positions=positions,
            capital=capital,
            value_per_point=value_of_price_point,
            delayfill=delayfill,
            fx=fx,
            roundpositions=roundpositions,
            vol_normalise_currency_costs=vol_normalise_currency_costs,
            rolls_per_year=0,
        )

        account_curve = accountCurve(pandl_calculator)

        return account_curve