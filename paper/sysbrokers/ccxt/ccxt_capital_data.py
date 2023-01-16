from paper.sysbrokers.ccxt.ccxt_connection import connectionCCXT
from sysbrokers.IB.client.ib_accounting_client import ibAccountingClient
from sysbrokers.broker_capital_data import brokerCapitalData

from syscore.objects import arg_not_supplied

from sysobjects.spot_fx_prices import listOfCurrencyValues

from syslogdiag.logger import logger
from syslogdiag.log_to_screen import logtoscreen


class ccxtCapitalData(brokerCapitalData):
    def __init__(
        self, ccxtconnection: connectionCCXT, log: logger = logtoscreen("ibCapitalData")
    ):
        super().__init__(log=log)
        self._ccxtconnection = ccxtconnection

    @property
    def ccxtconnection(self) -> connectionCCXT:
        return self._ccxtconnection

    def __repr__(self):
        return "IB capital data"

    def get_account_value_across_currency(
        self, account_id: str = arg_not_supplied
    ) -> listOfCurrencyValues:
        '''
        in usdt
        '''
        rep = self.ccxtconnection.ccxt.fetch_balance({"ccy": "USDT"})
        return [rep['USDT']['total']]

    def get_excess_liquidity_value_across_currency(self,
                                                   account_id: str = arg_not_supplied
                                                   )-> listOfCurrencyValues:
        rep = self.ccxtconnection.ccxt.fetch_balance({"ccy": "USDT"})
        return [float(rep['info']['data'][0]['details'][0]['upl'])]

    """
    Can add other functions not in parent class to get IB specific stuff which could be required for
      strategy decomposition
    """
