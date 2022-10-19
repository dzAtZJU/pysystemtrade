from copy import copy

from paper.sysbrokers.broker_factory import get_broker_class_list
from paper.sysobjects.spot_prices import spotPrices
from sysbrokers.broker_fx_handling import brokerFxHandlingData
from sysbrokers.broker_static_data import brokerStaticData
from sysbrokers.broker_execution_stack import brokerExecutionStackData
from sysbrokers.broker_futures_contract_price_data import brokerFuturesContractPriceData
from sysbrokers.broker_futures_contract_data import brokerFuturesContractData
from sysbrokers.broker_capital_data import brokerCapitalData
from sysbrokers.broker_contract_position_data import brokerContractPositionData
from sysbrokers.broker_fx_prices_data import brokerFxPricesData
from sysbrokers.broker_instrument_data import brokerFuturesInstrumentData

from syscore.objects import (
    arg_not_supplied,
    missing_order,
    missing_contract,
    missing_data
)
from syscore.dateutils import Frequency, DAILY_PRICE_FREQ, listOfOpeningTimes

from sysdata.data_blob import dataBlob
from sysdata.tools.cleaner import apply_price_cleaning

from sysexecution.orders.broker_orders import brokerOrder
from sysexecution.orders.list_of_orders import listOfOrders
from sysexecution.tick_data import dataFrameOfRecentTicks
from sysexecution.tick_data import analyse_tick_data_frame, tickerObject, analysisTick
from sysexecution.orders.contract_orders import contractOrder
from sysexecution.trade_qty import tradeQuantity
from sysexecution.order_stacks.broker_order_stack import orderWithControls

from sysobjects.contract_dates_and_expiries import expiryDate
from sysobjects.contracts import futuresContract
from sysobjects.instruments import futuresInstrumentWithMetaData
from sysobjects.production.positions import contractPosition, listOfContractPositions
from sysobjects.spot_fx_prices import fxPrices
from sysobjects.futures_per_contract_prices import futuresContractPrices
from sysproduction.data.positions import diagPositions
from sysproduction.data.currency_data import dataCurrency
from sysproduction.data.control_process import diagControlProcess
from sysproduction.data.generic_production_data import productionDataLayerGeneric


class dataExchange(productionDataLayerGeneric):
    def _add_required_classes_to_data(self, data) -> dataBlob:

        # Add a list of broker specific classes that will be aliased as self.data.broker_fx_prices,
        # self.data.broker_futures_contract_price ... and so on

        broker_class_list = get_broker_class_list(data)
        data.add_class_list(broker_class_list)
        return data

    @property
    def exchange_spot_price(self) -> brokerFuturesContractPriceData:
        return self.data.exchange_spot_price

    def get_prices_at_frequency_for_instrument_code(
        self, instrument_code:str, frequency: Frequency
    ) -> spotPrices:

        return self.exchange_spot_price.get_prices_at_frequency_for_instrument_code(instrument_code,
                                                                                                   frequency,
                                                                                                   return_empty=False)

    def get_brokers_instrument_code(self, instrument_code: str) -> str:
        return self.broker_futures_instrument_data.get_brokers_instrument_code(
            instrument_code
        )