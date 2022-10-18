from systems.forecast_combine import ForecastCombine
from systems.system_cache import diagnostic, dont_cache, input, output
import pandas as pd

class ctseForecastCombine(ForecastCombine):
    @dont_cache
    def get_raw_monthly_forecast_weights(self, instrument_code: str) -> pd.DataFrame:
        """
        Get forecast weights depending on whether we are estimating these or
        not

        :param instrument_code: str
        :return: forecast weights
        """

        # get estimated weights, will probably come back as annual data frame
        if self._use_estimated_weights():
            forecast_weights = self.get_monthly_raw_forecast_weights_estimated(
                instrument_code
            )
        else:
            ## will come back as 2*N data frame
            forecast_weights = self.get_raw_fixed_forecast_weights(instrument_code)

        return forecast_weights