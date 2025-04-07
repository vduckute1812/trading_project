from typing import List
import pandas as pd
import ta
import matplotlib.pyplot as plt

class TechniqueIndicator:
    def __init__(self, klines: List):
        self._df = klines

    def extract(self):
        self._normalize_data()
        self._calculate_indications()
        return self._df

    def _normalize_data(self) -> List:
        """
        Normalizer data and extract ohlcv features,
        We use ohlcv for training model
        """
        self._df = pd.DataFrame(self._df, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'
        ])
        self._df['timestamp'] = pd.to_datetime(self._df['timestamp'], unit='ms')
        self._df.set_index('timestamp', inplace=True)

        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        self._df[numeric_cols] = self._df[numeric_cols].astype(float)

    def _calculate_indications(self) -> List:
        """
        Calculate the technical indications, RSI, EMA, MACD
        :param df: Data frame
        :return: Data frame included technical indications
        """
        self._df['rsi'] = ta.momentum.RSIIndicator(close=self._df['close'], window=14).rsi()
        self._df['ema_12'] = ta.trend.EMAIndicator(close=self._df['close'], window=12).ema_indicator()
        self._df['ema_26'] = ta.trend.EMAIndicator(close=self._df['close'], window=26).ema_indicator()

        macd = ta.trend.MACD(close=self._df['close'])
        self._df['macd'] = macd.macd()
        self._df['macd_signal'] = macd.macd_signal()
        self._df['macd_hist'] = macd.macd_diff()
        self._df['price_change'] = self._df['close'].pct_change()  # Biến động  theo phan tram
        self._df['volatility'] = (self._df['high'] - self._df['low']) / self._df['open']
        self._df.dropna(inplace=True)


    def draw_chart(self):
        """
        Draw features on chart
        """
        plt.figure(figsize=(14,14))

        plt.subplot(3, 1, 1)  # (rows, cols, position)
        plt.plot(self._df['close'], label='Close')
        plt.plot(self._df['ema_12'], label='EMA 12')
        plt.plot(self._df['ema_26'], label='EMA 26')
        plt.legend()
        plt.title('EMA Crossover')

        plt.subplot(3, 1, 2)  # (rows, cols, position)
        plt.plot(self._df['macd'], label='macd')
        plt.plot(self._df['macd_signal'], label='macd_signal')
        plt.plot(self._df['macd_hist'], label='macd_hist')
        plt.legend()
        plt.title('MACD')

        plt.subplot(3, 1, 3)  # (rows, cols, position)
        plt.plot(self._df['volatility'], label='volatility')
        plt.plot(self._df['price_change'], label='price_change')
        plt.legend()
        plt.title('VOTALITITY')

        plt.tight_layout()
        plt.show()
