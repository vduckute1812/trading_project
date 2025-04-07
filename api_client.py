import os
from binance.client import Client
from typing import Type, Dict

class APIClient:
    def __init__(self):
        self.__client = self.__get_client()

    def __get_client(self) -> Type[Client]:
        api_key = os.getenv("API_KEY")
        api_secrete = os.getenv("API_SECRETE")
        use_testnet = int(os.getenv("USE_TESTNET"))
        client = Client(api_key, api_secrete)
        if use_testnet:
            client.API_URL = 'https://testnet.binance.vision/api'
        return client

    def get_balance(self, asset: str) -> float:
        """
        Get asset balance of your wallet
        :param asset: name of asset, Ex: USDT, BTC, SOL
        """
        return self.__client.get_asset_balance(asset=asset)
    
    def get_account(self) -> Dict:
        """
        Get assets of your wallet
        """
        return self.__client.get_account()

    def get_market_price(self, symbol: str) -> float:     
        """
        Get market price of the crypto
        :param symbol: name of crypto on money, Ex: BTCUSDT (Bitcoin price on USDT)
        """
        return float(self.__client.get_symbol_ticker(symbol=symbol)["price"])

    def get_historical_klines(self, symbol: str, interval: int, start_date: str = None, end_date: str = None, limit: int = 100):
        """
        Get historical klines of market
        """
        return self.__client.get_historical_klines(symbol, interval, start_date, end_date, limit=limit)

    def buy(self, symbol: str, quantity: float) -> Dict:
        """
        Buy crypto on market
        :param symbol: name of symbol, Ex: BTCUSDT (Bitcoin price on USDT)
        :param quantity: the number of crypto you want to buy
        :return: the information of your order
        """
        return self.__client.order_market_buy(symbol=symbol, quantity=quantity)

    def sell(self, symbol: str, quantity: float) -> Dict:
        """
        Sell crypto on market
        :param symbol: name of crypto on money, Ex: BTCUSDT (Bitcoin price on USDT)
        :param quantity: the number of crypto you want to sell
        :return: the information of your order
        """
        return self.__client.order_market_sell(symbol=symbol, quantity=quantity)
