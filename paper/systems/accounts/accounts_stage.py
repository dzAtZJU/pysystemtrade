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
import pandas as pd

from syscore.dateutils import ROOT_BDAYS_INYEAR
from syscore.objects import arg_not_supplied
from syscore.pdutils import sum_series
from sysquant.estimators.vol import robust_daily_vol_given_price

from systems.system_cache import diagnostic
from systems.accounts.account_costs import accountCosts
from systems.accounts.pandl_calculators.pandl_SR_cost import pandlCalculationWithSRCosts
from systems.accounts.curves.account_curve import accountCurve
from syscore.dateutils import Frequency
class perpetualsAccount(Account):
    # @property
    # def name(self):
    #     return "accounts"

    # def get_SR_holding_cost_only(self, instrument_code: str) -> float:
    #     self.log.warn(
    #             "ignoring perpetuals holding costs for now"
    #         )
    #     return 0.1

    @diagnostic(not_pickable=True)
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
        value_of_price_point = self.get_value_of_block_price_move(instrument_code)

        capital = self.get_notional_capital()

        vol_normalise_currency_costs = self.config.vol_normalise_currency_costs
        rolls_per_year = self.get_rolls_per_year(instrument_code)

        pandl_calculator = pandlCalculationWithCashCostsAndFills(
            price,
            raw_costs=raw_costs,
            positions=positions,
            capital=capital,
            value_per_point=value_of_price_point,
            delayfill=delayfill,
            roundpositions=roundpositions,
            vol_normalise_currency_costs=vol_normalise_currency_costs,
            rolls_per_year=rolls_per_year,
        )

        account_curve = accountCurve(pandl_calculator, weighted=True)

        return account_curve

    @diagnostic(not_pickable=True)
    def _pandl_for_subsystem_with_cash_costs(
        self, instrument_code, delayfill=True, roundpositions=True
    ) -> accountCurve:

        raw_costs = self.get_raw_cost_data(instrument_code)
        price = self.get_daily_price(instrument_code)
        positions = self.get_buffered_subsystem_position(instrument_code)

        value_of_price_point = self.get_value_of_block_price_move(instrument_code)

        capital = self.get_notional_capital()

        vol_normalise_currency_costs = self.config.vol_normalise_currency_costs
        rolls_per_year = self.get_rolls_per_year(instrument_code)

        pandl_calculator = pandlCalculationWithCashCostsAndFills(
            price,
            raw_costs=raw_costs,
            positions=positions,
            capital=capital,
            value_per_point=value_of_price_point,
            delayfill=delayfill,
            roundpositions=roundpositions,
            vol_normalise_currency_costs=vol_normalise_currency_costs,
            rolls_per_year=rolls_per_year,
        )

        account_curve = accountCurve(pandl_calculator)

        return account_curve

    @diagnostic(not_pickable=True)
    def pandl_for_instrument_forecast(
        self, instrument_code: str, rule_variation_name: str, delayfill: bool = True
    ) -> accountCurve:
        """
        Get the p&l for one instrument and forecast; as % of arbitrary capital

        :param instrument_code: instrument to get values for
        :type instrument_code: str

        :param rule_variation_name: rule to get values for
        :type rule_variation_name: str

        :param delayfill: Lag fills by one day
        :type delayfill: bool

        :returns: accountCurve

        >>> from systems.basesystem import System
        >>> from systems.tests.testdata import get_test_object_futures_with_portfolios
        >>> (portfolio, posobject, combobject, capobject, rules, rawdata, data, config)=get_test_object_futures_with_portfolios()
        >>> system=System([portfolio, posobject, combobject, capobject, rules, rawdata, Account()], data, config)
        >>>
        >>> system.accounts.pandl_for_instrument_forecast("EDOLLAR", "ewmac8").ann_std()
        0.20270495775586916

        """

        self.log.msg(
            "Calculating pandl for instrument forecast for %s %s"
            % (instrument_code, rule_variation_name),
            instrument_code=instrument_code,
            rule_variation_name=rule_variation_name,
        )

        forecast = self.get_capped_forecast(instrument_code, rule_variation_name)

        price = self.get_raw_price(instrument_code)

        daily_returns_volatility = self.get_daily_returns_volatility(instrument_code)

        # We NEVER use cash costs for forecasts ...
        SR_cost = self.get_SR_cost_for_instrument_forecast(
            instrument_code, rule_variation_name
        )

        target_abs_forecast = self.target_abs_forecast()

        capital = self.get_notional_capital()
        risk_target = self.get_annual_risk_target()
        value_per_point = self.get_value_of_block_price_move(instrument_code)

        pandl_fcast = pandl_for_instrument_forecast(
            forecast,
            price=price,
            capital=capital,
            risk_target=risk_target,
            daily_returns_volatility=daily_returns_volatility,
            target_abs_forecast=target_abs_forecast,
            SR_cost=SR_cost,
            delayfill=delayfill,
            value_per_point=value_per_point,
        )

        return pandl_fcast

    @diagnostic()
    def get_SR_cost_for_instrument_forecast(
        self, instrument_code: str, rule_variation_name: str
    ) -> float:
        return 0.001


ARBITRARY_FORECAST_CAPITAL = 100
ARBITRARY_FORECAST_ANNUAL_RISK_TARGET_PERCENTAGE = 0.16


ARBITRARY_VALUE_OF_PRICE_POINT = 1.0

def pandl_for_instrument_forecast(
    forecast: pd.Series,
    price: pd.Series,
    capital: float = ARBITRARY_FORECAST_CAPITAL,
    fx=arg_not_supplied,
    risk_target: float = ARBITRARY_FORECAST_ANNUAL_RISK_TARGET_PERCENTAGE,
    daily_returns_volatility: pd.Series = arg_not_supplied,
    target_abs_forecast: float = 10.0,
    SR_cost=0.0,
    delayfill=True,
    value_per_point=ARBITRARY_VALUE_OF_PRICE_POINT,
) -> accountCurve:

    if daily_returns_volatility is arg_not_supplied:
        daily_returns_volatility = robust_daily_vol_given_price(price)

    normalised_forecast = _get_normalised_forecast(
        forecast, target_abs_forecast=target_abs_forecast
    )

    average_notional_position = _get_average_notional_position(
        daily_returns_volatility,
        risk_target=risk_target,
        value_per_point=value_per_point,
        capital=capital,
    )

    notional_position = _get_notional_position_for_forecast(
        normalised_forecast, average_notional_position=average_notional_position
    )

    pandl_calculator = pandlCalculationWithSRCosts(
        price,
        SR_cost=SR_cost,
        positions=notional_position,
        daily_returns_volatility=daily_returns_volatility,
        average_position=average_notional_position,
        capital=capital,
        value_per_point=value_per_point,
        delayfill=delayfill,
    )

    account_curve = accountCurve(pandl_calculator, frequency=Frequency.Day)

    return account_curve


def _get_notional_position_for_forecast(
    normalised_forecast: pd.Series, average_notional_position: pd.Series
) -> pd.Series:

    aligned_average = average_notional_position.reindex(
        normalised_forecast.index, method="ffill"
    )

    return aligned_average * normalised_forecast


def _get_average_notional_position(
    daily_returns_volatility: pd.Series,
    capital: float = ARBITRARY_FORECAST_CAPITAL,
    risk_target: float = ARBITRARY_FORECAST_ANNUAL_RISK_TARGET_PERCENTAGE,
    value_per_point=ARBITRARY_VALUE_OF_PRICE_POINT,
) -> pd.Series:

    daily_risk_target = risk_target / ROOT_BDAYS_INYEAR
    daily_cash_vol_target = capital * daily_risk_target

    instrument_currency_vol = daily_returns_volatility * value_per_point
    average_notional_position = daily_cash_vol_target / instrument_currency_vol

    return average_notional_position


def _get_normalised_forecast(
    forecast: pd.Series, target_abs_forecast: float = 10.0
) -> pd.Series:

    normalised_forecast = forecast / target_abs_forecast

    return normalised_forecast
