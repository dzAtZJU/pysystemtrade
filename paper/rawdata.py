from systems.rawdata  import RawData
import pandas as pd

class paperRawData(RawData):
    def rolls_per_year(self, instrument_code: str) -> int:
        return 1