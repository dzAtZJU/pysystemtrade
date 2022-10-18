from systems.rawdata import RawData

class ctseRawData(RawData):
    def get_instrument_code(self, instrument_code) -> str:
        return instrument_code