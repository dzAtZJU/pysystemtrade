import pandas as pd
from systems.positionsizing import PositionSizing
from systems.system_cache import diagnostic

class ctsePositionSizing(PositionSizing):
    @diagnostic()
    def get_volatility_scalar(self, instrument_code: str) -> pd.Series:
        self.log.msg(
            "Calculating volatility scalar for %s" % instrument_code,
            instrument_code=instrument_code,
        )

        if self.position_sizing_method == 'none_so_every_trade_cash_all_in':
            vol_scalar = self.get_cash_all_in_scalar(instrument_code)
        elif self.position_sizing_method == 'trade_vol_target':
            signal = self.parent.rules.get_raw_forecast(instrument_code, 'dma_long_1_D')
            entry = signal * (signal.shift(1) == 0)
            vol_scalar = super().get_volatility_scalar(instrument_code)
            import numpy as np
            tmp = signal.replace(1, np.nan)
            tmp[entry == 1] = 1
            return (tmp * vol_scalar).ffill()
        # elif self.position_sizing_method == 'fixed_contract':
        #     tmp = self.get_underlying_price(instrument_code)
        #     vol_scalar = pd.Series([1] * len(tmp), index=tmp.index)
        else:
            assert False
            
        return vol_scalar

    @diagnostic()
    def get_cash_all_in_scalar(self, instrument_code) -> float:
        block_notional_value  = self.get_block_value(instrument_code) * 100
        return self.get_notional_trading_capital() / block_notional_value

    @property
    def position_sizing_method(self) -> str:
        return self.config.position_sizing_method

    def daily_risk_target_capital_pct(self, instrument_code):
        vol_scalar = super().get_volatilityw_scalar( instrument_code)
        tmp = self.get_block_value(instrument_code) * 100 * vol_scalar / self.get_notional_trading_capital()
        return tmp

    def contract_exposure(self, instrument_code):
        underlying_price = self.get_underlying_price(instrument_code)
        value_of_price_move = self.parent.data.get_value_of_block_price_move(
            instrument_code
        )

        return  underlying_price.ffill() * value_of_price_move
