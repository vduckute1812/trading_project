from api_client import APIClient
from datetime import datetime
from typing import Dict

class Wallet:
    def __init__(self):
        self.__client = APIClient()
        self.load_assets()
        self.set_daily_usdt_asset()

    def load_assets(self):
        account_info = self.__client.get_account()
        current_asset_map = {
            balance['asset']: float(balance['free'])
            for balance in account_info['balances']
            if float(balance['free']) > 0
        }
        self.__current_asset_map = current_asset_map

    def get_usdt_asset(self, asset_quantity_map: Dict, symbol: str = "") -> float:
        usdt_quantity = 0.0
        if symbol:
            asset_quantity_map = {asset: quantity for asset, quantity in asset_quantity_map.items() if asset==symbol}
        for asset, quantity in asset_quantity_map.items():
            price_market = 1.0 if asset == "USDT" else self.__client.get_market_price(f"{asset}USDT")
            usdt_quantity += price_market * quantity
        return usdt_quantity
    
    def get_quantity(self, asset: str = "") -> float:
        self.load_assets()
        return self.__current_asset_map.get(asset, 0.0)

    def get_affordble_quantity(self, symbol: str = "") -> float:
        self.load_assets()
        price = self.__client.get_market_price(symbol=symbol)
        current_usdt = self.get_usdt_asset(self.__current_asset_map, symbol="USDT")
        return int(current_usdt / price * 10000) / 10000

    def set_daily_usdt_asset(self) -> None:
        self.__daily_asset_map = self.__current_asset_map
        daily_usdt_asset = self.get_usdt_asset(self.__daily_asset_map)
        print(f"[{datetime.utcnow()}] Origin USDT asset set: {daily_usdt_asset:.2f} USDT")

    def get_total_profit(self, symbol: str = "") -> None:
        self.load_assets()
        current_asset = self.get_usdt_asset(self.__current_asset_map, symbol=symbol)
        daily_usdt_asset = self.get_usdt_asset(self.__daily_asset_map, symbol=symbol)
        profit = (current_asset - daily_usdt_asset) / daily_usdt_asset
        print(f"👜 PnL: {profit*100:.2f}%")
