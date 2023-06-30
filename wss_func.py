import websocket
import json


def create_connection(stream_names, symbol):
    url = f"wss://fstream.binance.com/stream?streams={stream_names}"
    ws = websocket.WebSocketApp(url, on_message=on_message, on_close=on_close)
    ws.run_forever()


def on_message(ws, message):
    data = message
    print(data)


def on_close(ws):
    print("Connection closed")


def get_coin_price(symbol):
    stream_name = f"{symbol}@markPrice@1s/"
    return stream_name


def get_top_orders(symbol, number_orders, update_speed):
    stream_name = f"{symbol}@depth{number_orders}@{update_speed}ms/"
    return stream_name
