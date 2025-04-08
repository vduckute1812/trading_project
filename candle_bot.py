from typing import Tuple, List
from api_client import APIClient
from binance.client import Client
from technique_indicator import TechniqueIndicator
from constant import PriceTrend, THE_LAST_THREE_CANDLES, PRICE_INCREASING_THRESHOLD, PRICE_DECREASING_THRESHOLD
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
import joblib


class CandleBot:
    def __init__(self, symbol: str, with_chart=False):
        self.__with_chart = with_chart
        self.__symbol = symbol
        self.__load_env()
        self.__encoder = LabelEncoder()
        self.__client = APIClient()

    def __load_env(self):
        from dotenv import load_dotenv
        load_dotenv()

    def __calculate_indication(self, symbol: str, with_chart: bool = False):
        klines = self.__client.get_historical_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE)
        indicator = TechniqueIndicator(klines=klines)
        indications = indicator.extract()
        if with_chart:
            indicator.draw_chart()
        return indications

    def __extract_features(self, symbol: str) -> Tuple:
        df = self.__calculate_indication(symbol=symbol, with_chart=self.__with_chart)
        df['future_return'] = df['close'].shift(THE_LAST_THREE_CANDLES) / df['close'] - 1  # return phần trăm thay đổi sau 3 nến
        df['target'] = df['future_return'].apply(lambda x: PriceTrend.INCREASING if x > PRICE_INCREASING_THRESHOLD else (PriceTrend.DESCREASING if x < PRICE_DECREASING_THRESHOLD else PriceTrend.SIDEWAY))   # gán nhãn
        df.dropna(inplace=True)
        X = df[self.xgp_features]
        y = df['target']
        y_encoded = self.__encoder.fit_transform(y)
        return X, y_encoded
    
    def ai_train(self):
        X, y = self.__extract_features(self.__symbol)
        model = XGBClassifier(
            objective='multi:softprob',
            num_class=3,
            eval_metric='mlogloss',
            use_label_encoder=False
        )
        model.fit(X, y)
        return model
    
    def ai_predict(self, model, latest):
        latest = latest[self.xgp_features].values.reshape(1, -1)
        prediction = model.predict(latest)[0]
        probabilities = model.predict_proba(latest)[0]  # [p_down, p_sideways, p_up]

        trend = self.__encoder.inverse_transform([prediction])[0]
        confidence = max(probabilities)
        print(f"📊 AI Dự đoán: {trend} (Conf: {confidence:.2f})")
        return trend, confidence
    
    def indication_predict(self, latest) -> int:
        rsi_signal = PriceTrend.INCREASING if latest['rsi'] < 30 else PriceTrend.DESCREASING if latest['rsi'] > 70 else PriceTrend.SIDEWAY
        macd_signal = PriceTrend.INCREASING if latest['macd'] > latest['macd_signal'] else PriceTrend.DESCREASING        
        print(f"rsi_signal: {rsi_signal}, macd_signal: {macd_signal}, latest_rsi: {latest['rsi']}, macd: {latest['macd']}, macd_signal: {latest['macd_signal']}")
        if rsi_signal == macd_signal:
            return rsi_signal
        return PriceTrend.UNKNOWN

    def handle(self) -> Tuple[int, float]:
        model = self.ai_train()
        latest = self.__calculate_indication(symbol=self.__symbol).iloc[-1]
        # model = joblib.load('xgb_model.pkl')
        ai_signal, confident = self.ai_predict(model=model, latest=latest)
        # indication_signal = self.indication_predict(latest=latest)
        # if ai_signal == indication_signal:  # AI and indicator predict same result
        return ai_signal, confident
        return PriceTrend.UNKNOWN, 0.0

    @property
    def xgp_features(self) -> List[str]:
        return ['rsi', 'ema_12', 'ema_26', 'macd', 'macd_signal', 'macd_hist', 'price_change']

