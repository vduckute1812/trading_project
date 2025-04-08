import joblib
from wallet import Wallet
from api_client import APIClient
from candle_bot import CandleBot
import time

class TradingHandler:
    def __init__(self, symbol: str):
        self.__wallet = Wallet()
        self.__profit = 0.0
        self.__hold_price = 0
        self.__client = APIClient()
        self.__bot = CandleBot(symbol=symbol)

    def buy(self, symbol):
        try:
            price = self.__client.get_market_price(symbol=symbol)
            self.__hold_price = price
        except Exception as e:
            print(e)

    def sell(self, symbol):
        try:
            price = self.__client.get_market_price(symbol=symbol)
            self.__profit += (price - self.__hold_price)
            self.__hold_price = 0
        except Exception as e:
            print(e)
    def run_bot(self):
        while True:
            try:
                action, confidence = self.__bot.handle()
                if action == 1 and self.__hold_price == 0:
                    print(f"BUY Signal | Confidence: {confidence:.2f}")
                    # place_order('buy', amount)
                elif action == -1 and self.__hold_price > 0:
                    print(f"SELL Signal | Confidence: {confidence:.2f}")
                    # place_order('sell', amount)
                else:
                    print(f"No signal | AI: {action}, Confidence: {confidence:.2f}")
                # wait for 5 minutes
                time.sleep(300)

            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)

handler = TradingHandler(symbol="SOLUSDT")
handler.run_bot()