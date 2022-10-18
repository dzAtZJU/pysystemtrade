from systems.rawdata  import RawData
import pandas as pd

class paperRawData(RawData):
    def daily_denominator_price(self, instrument_code: str) -> pd.Series:
        return self.get_daily_prices(instrument_code)