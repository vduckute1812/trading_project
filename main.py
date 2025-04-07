import joblib
from wallet import Wallet
from candle_bot import CandleBot
import time

class TradingHandler:
    def __init__(self, symbol: str):
        self.__wallet = Wallet()
        self.__bot = CandleBot(symbol=symbol)


    def run_bot(self):
        while True:
            try:
                action, confidence = self.__bot.handle()

                if action == 1:
                    print(f"BUY Signal | Confidence: {confidence:.2f}")
                    # place_order('buy', amount)
                elif action == -1:
                    print(f"SELL Signal | Confidence: {confidence:.2f}")
                    # place_order('sell', amount)
                else:
                    print(f"No signal | AI: {action}, Confidence: {confidence:.2f}")
                self.__wallet.get_total_profit()
                # wait for 5 minutes
                time.sleep(300)

            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)

handler = TradingHandler(symbol="SOLUSDT")
handler.run_bot()