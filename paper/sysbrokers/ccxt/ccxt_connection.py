"""
IB connection using ib-insync https://ib-insync.readthedocs.io/api.html

"""

import time

from ccxt import Exchange
import ccxt
from syscore.exceptions import missingData
from syscore.constants import arg_not_supplied

from syslogdiag.log_to_screen import logtoscreen

from sysdata.config.production_config import get_production_config


class connectionCCXT(object):
    """
    Connection object for connecting IB
    (A database plug in will need to be added for streaming prices)
    """

    def __init__(
        self,
        apiKey,
        secret,
        password,
        log=logtoscreen("connectionCCXT"),
    ):
        self._log = log
        self._okx = ccxt.okex5({
            'apiKey': apiKey,
            'secret': secret,
            'password': password
        })
        self._binance = ccxt.binanceusdm()

    @property
    def okx(self) -> Exchange:
        return self._okx
    
    @property
    def binance(self) -> Exchange:
        return self._binance

    @property
    def log(self):
        return self._log

    def __repr__(self):
        return "IB broker connection" + str(self._ib_connection_config)

    def client_id(self):
        return self._ib_connection_config["client"]

    @property
    def account(self):
        return self._account

    def close_connection(self):
        pass
        # self.log.msg("Terminating %s" % str(self._ib_connection_config))
        # try:
        #     # Try and disconnect IB client
        #     self.ib.disconnect()
        # except BaseException:
        #     self.log.warn(
        #         "Trying to disconnect IB client failed... ensure process is killed"
        #     )


def get_broker_account() -> (str, str, str):
    production_config = get_production_config()
    account_id = production_config.get_element("apikey")
    account_id1 = production_config.get_element("secretkey")
    password = production_config.get_element("password")
    return (account_id, account_id1, password)
