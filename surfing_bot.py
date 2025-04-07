import websocket
import json
from collections import deque
import time
from api_client import APIClient
from wallet import Wallet
from dotenv import load_dotenv
load_dotenv()

price_buffer = deque(maxlen=1000)
volume_buffer = deque(maxlen=1000)
average_30_buffer = deque(maxlen=30)
average_10_volumn = deque(maxlen=10)

last_signal_time = time.time() 
cooldown = 10
awaiting_pullback = False
pullback_reference_price = None

holding = False
entry_price = 0

client = APIClient()
wallet = Wallet()

def buy():
    try:
        affordble_quantity = wallet.get_affordble_quantity("SOLUSDT")
        affordble_quantity = int(affordble_quantity * 100) / 100
        print(f"Buy {affordble_quantity} SOL")
        client.buy("SOLUSDT", quantity=affordble_quantity)         # Only buy 20%
    except Exception as e:
        print(e)

def sell():
    try:
        quantity = int(wallet.get_quantity("SOL") * 0.99 * 100 ) / 100
        print(f"Sell {quantity} SOL")
        client.sell("SOLUSDT", quantity=quantity)       
    except Exception as e:
        print(e)

def on_message(ws, msg):
    global last_signal_time, awaiting_pullback, pullback_reference_price
    global holding, entry_price
    msg = json.loads(msg)
    if msg['e'] == 'trade':
        current_price = float(msg['p'])
        trade_volume = float(msg['q'])  # volume của giao dịch này
        timestamp = time.time()
        is_sell = msg['m']  # True = bên bán chủ động, False = bên mua chủ động

        price_buffer.append((timestamp, current_price))
        volume_buffer.append(trade_volume)
        average_10_volumn.append(trade_volume)
        average_30_buffer.append(current_price)
        avg_price = sum(average_30_buffer) / len(average_30_buffer)
        # print(f"📈 Giá: {current_price:.2f} USDT | 🧪 Volume 24h: {trade_volume:.5f} | is_sell: {is_sell}")

        # --- Nếu đang giữ coin, kiểm tra để bán ---
        if holding:
            profit = (current_price - entry_price) / entry_price
            print(f"👜 Đang giữ lệnh - PnL: {profit*100:.2f}%")

            # Chốt lời khi lời > 0.5%
            if is_sell and profit > 0.005 and current_price < avg_price:
                print("✅ CHỐT LỜI")
                holding = False
                sell()
                entry_price = 0
                last_signal_time = time.time()
                return

            # # Bán khẩn nếu có dấu hiệu bán mạnh (giá giảm và volume tăng bất thường)
            # if is_sell and current_price < avg_price:
            #     avg_volume = sum(volume_buffer) / len(volume_buffer)
            #     avg_trade_volume = sum(average_10_volumn) / len(average_10_volumn)
            #     volume_change_percent = (avg_trade_volume - avg_volume) / avg_volume
            #     if volume_change_percent > 0.5:  # Tốc độ bán tăng 50%. Bán mạnh
            #         print("❌ BÁN KHẨN: Áp lực bán mạnh!")
            #         holding = False
            #         sell()
            #         entry_price = 0
            #         last_signal_time = time.time()
            #         return

        # --- Nếu chưa giữ lệnh, xét điều kiện mua ---
        if not holding and price_buffer:
            old_price = price_buffer[0][1]
            price_change = (current_price - old_price) / old_price
            if time.time() - last_signal_time > cooldown:
                if 0.002 < price_change <= 0.004:
                    print("🟢 MUA NHẸ (tăng vừa đủ)")
                    buy()
                    holding = True
                    entry_price = current_price
                    last_signal_time = time.time()
                elif price_change > 0.004:
                    print("⚠️ Giá tăng mạnh! Chờ điều chỉnh...")
                    awaiting_pullback = True
                    pullback_reference_price = current_price

        # Nếu đang chờ điều chỉnh
        if awaiting_pullback and pullback_reference_price:
            drop_percent = (pullback_reference_price - current_price) / pullback_reference_price
            if drop_percent > 0.001:
                print("🟢 MUA ĐÁY sau tăng mạnh!")
                holding = True
                entry_price = current_price
                awaiting_pullback = False
                pullback_reference_price = None
                last_signal_time = time.time()


def on_error(ws, error):
    print("Lỗi:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔌 WebSocket đã đóng kết nối.")

def on_open(ws):
    print("🔌 Kết nối WebSocket thành công!")

# URL WebSocket Binance để nhận giá từng giây
SOCKET = "wss://stream.binance.com:9443/ws/solusdt@trade"

# Kết nối
ws = websocket.WebSocketApp(
    SOCKET,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

# Bắt đầu chạy vòng lặp
ws.run_forever()