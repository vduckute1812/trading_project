THE_LAST_THREE_CANDLES = -3
PRICE_INCREASING_THRESHOLD = 0.005 # 0.5%   
PRICE_DECREASING_THRESHOLD = -0.005 # -0.5%   


class PriceTrend:
    DESCREASING = -1
    SIDEWAY = 0
    INCREASING = 1
    UNKNOWN = 2

    def is_buy_signal(cls, val: int):
        return cls.INCREASING == val
    
    def is_sell_signal(cls, val: int):
        return cls.DESCREASING == val

class RSISingal:
    OVER_SELL = 30 #  <30 = oversold (buy)
    OVER_BOUGHT = 70  # RSI: >70 = overbought (sell)

class Action:
    BUY = 1
    SELL = 2
    HOLD = 3