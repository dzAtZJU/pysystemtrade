from copy import copy

import numpy as np
import pandas as pd

from syscore.merge_data import full_merge_of_existing_series
from sysobjects.dict_of_named_futures_per_contract_prices import (
    price_column_names,
    contract_column_names,
    price_name,
    contract_name_from_column_name,
)

class spotPrices(pd.Series):
    """
    adjusted price information
    """

    def __init__(self, price_data):
        price_data.index.name = "index"  # arctic compatible
        super().__init__(price_data)

    @classmethod
    def create_empty(cls):
        """
        Our graceful fail is to return an empty, but valid, dataframe
        """

        futures_contract_prices = cls(pd.Series(dtype=float))

        return futures_contract_prices


    def update_with_new_prices(
        self, new_prices
    ):
        """
        Update adjusted prices assuming no roll has happened

        :param updated_multiple_prices: futuresMultiplePrices
        :return: updated adjusted prices
        """

        updated_adj = _update_adjusted_prices_from_multiple_no_roll(
            self, new_prices
        )

        return updated_adj

def _update_adjusted_prices_from_multiple_no_roll(
    existing_adjusted_prices: spotPrices,
    new_prices: spotPrices,
) -> spotPrices:
    """
    Update adjusted prices assuming no roll has happened

    :param existing_adjusted_prices: futuresAdjustedPrices
    :param updated_multiple_prices: futuresMultiplePrices
    :return: updated adjusted prices
    """

    merged_adjusted_prices = full_merge_of_existing_series(
        existing_adjusted_prices, new_prices
    )
    merged_adjusted_prices = spotPrices(merged_adjusted_prices)

    return merged_adjusted_prices