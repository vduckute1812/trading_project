import os
from typing import Type, Dict

def get_client() -> Type[Client]:
    API_KEY = os.getenv("API_KEY")
    API_SECRETE = os.getenv("API_SECRETE")
    return Client(API_KEY, API_SECRETE)

def get_balance(client: Type[Client], asset: str) -> float:
    """
    Get asset balance of your wallet
    :param asset: name of asset, Ex: USDT, BTC, SOL
    """
    return client.get_asset_balance(asset=asset)

def get_market_price(client: Type[Client], symbol: str) -> float:     
    """
    Get market price of the crypto
    :param symbol: name of crypto on money, Ex: BTCUSDT (Bitcoin price on USDT)
    """
    return client.get_symbol_ticker(symbol=symbol)["price"]

def get_historical_klines(client: Type[Client], symbol: str, interval: int, start_date: str = "", end_date: str = ""):
    """
    Get historical klines of market
    """
    return client.get_historical_klines(symbol, interval, start_date, end_date)

def buy(client: Type[Client], symbol: str, quantity: float) -> Dict:
    """
    Buy crypto on market
    :param symbol: name of symbol, Ex: BTCUSDT (Bitcoin price on USDT)
    :param quantity: the number of crypto you want to buy
    :return: the information of your order
    """
    return client.order_market_buy(symbol=symbol, quantity=quantity)

def sell(client: Type[Client], symbol: str, quantity: float) -> Dict:
    """
    Sell crypto on market
    :param symbol: name of crypto on money, Ex: BTCUSDT (Bitcoin price on USDT)
    :param quantity: the number of crypto you want to sell
    :return: the information of your order
    """
    return client.order_market_sell(symbol=symbol, quantity=quantity)
