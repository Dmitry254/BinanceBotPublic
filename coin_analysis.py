import time
import traceback

from base_func import get_data, get_data_header, create_signature, set_order_interval
from key import api_key_binance, secret_binance
from wss_func import create_connection, get_coin_price, get_top_orders
# from tg_bot import message, send_text_message


def get_coin_last_price(symbol):
    url = f"https://fapi.binance.com/fapi/v1/ticker/price/"
    params = {
        'symbol': symbol,
        'timestamp': int(time.time() * 1000)
    }
    params = create_signature(params)
    res = get_data_header(url, params)
    if 'msg' in res.keys():
        if res['msg'] == 'Invalid symbol.':
            return "Сoin is not traded"
    coin_price = float(res['price'])
    return coin_price


def get_orders(symbol):
    url = f"https://fapi.binance.com/fapi/v1/depth/"
    params = {
        'symbol': symbol,
        'limit': 1000,
        'price': 1,
        'timestamp': int(time.time() * 1000),
    }
    params = create_signature(params)
    res = get_data_header(url, params)
    return res


def combine_orders(coin_orders, orders_interval, order_type):
    combined_orders = {}
    interval_border = 0
    average_order_price = 0
    combined_order_size = 0
    price_sum = 0
    counter = 0
    orders_info = coin_orders[order_type]
    combined_orders_list = []
    for order_info in orders_info:
        order_price = float(order_info[0])
        order_size = float(order_info[1])
        if order_type == 'asks':
            if order_price > interval_border or interval_border == 0:
                interval_border = order_price + orders_interval
                if counter != 0:
                    average_order_price = price_sum / counter
                    combined_orders_list.append([average_order_price, combined_order_size])
                combined_order_size = 0
                price_sum = 0
                counter = 0
            combined_order_size += order_size
            price_sum += order_price
            counter += 1
        elif order_type == 'bids':
            if order_price < interval_border or interval_border == 0:
                interval_border = order_price - orders_interval
                if counter != 0:
                    average_order_price = price_sum / counter
                    combined_orders_list.append([average_order_price, combined_order_size])
                combined_order_size = 0
                price_sum = 0
                counter = 0
            combined_order_size += order_size
            price_sum += order_price
            counter += 1
    combined_orders.update({order_type: combined_orders_list})
    return combined_orders


def get_volume(symbol, last_interval):
    if last_interval > 28:
        last_interval = 28
    url = f"https://fapi.binance.com/futures/data/takerlongshortRatio"
    params = {
        'symbol': symbol,
        'period': "1d",
        'limit': 500,
        'startTime': int(time.time() * 1000) - 86400000 * last_interval,
        'endTime': int(time.time() * 1000),
    }
    res = get_data(url, params)
    return res


def get_average_volumes(coin_volume):
    average_buy_volume, average_sell_volume, average_total_volume = 0, 0, 0
    counter = 0
    for candle_volume in coin_volume:
        try:
            average_buy_volume += float(candle_volume['buyVol'])
            average_sell_volume += float(candle_volume['sellVol'])
            counter += 1
        except TypeError:
            traceback.print_exc()
            print(coin_volume)
            print(candle_volume)
            continue
    average_buy_volume = average_buy_volume / counter
    average_sell_volume = average_sell_volume / counter
    average_total_volume = average_buy_volume + average_sell_volume
    return average_buy_volume, average_sell_volume, average_total_volume


def get_level_volume(combined_orders, price_level, order_type):
    level_volume = 0
    for combined_order in combined_orders[order_type]:
        if order_type == 'asks':
            if combined_order[0] > price_level:
                order_number = combined_orders[order_type].index(combined_order)
                if order_number == 0:
                    level_volume = float(combined_orders[order_type][order_number][1])
                    return level_volume
                level_volume = float(combined_orders[order_type][order_number][1]) + float(combined_orders[order_type][order_number - 1][1])
                return level_volume
        elif order_type == 'bids':
            if combined_order[0] < price_level:
                order_number = combined_orders[order_type].index(combined_order)
                if order_number == 0:
                    level_volume = float(combined_orders[order_type][order_number][1])
                    return level_volume
                level_volume = float(combined_orders[order_type][order_number][1]) + float(combined_orders[order_type][order_number - 1][1])
                return level_volume
    return None


def start_analysis(symbol, coin_current_price, last_interval, price_level, order_type):
    print(symbol)
    stream_name = ""
    coin_price = get_coin_last_price(symbol)
    if coin_price == "Сoin is not traded":
        print(coin_price)
        return coin_price
    coin_orders = get_orders(symbol)
    orders_interval = set_order_interval(coin_current_price)
    combined_orders = combine_orders(coin_orders, orders_interval, order_type)
    coin_volume = get_volume(symbol, last_interval)
    average_buy_volume, average_sell_volume, average_total_volume = get_average_volumes(coin_volume)
    level_volume = get_level_volume(combined_orders, price_level, order_type)
    analysis_results = [coin_price, price_level, level_volume, average_buy_volume, average_sell_volume, average_total_volume]
    print(coin_price)
    print(combined_orders)
    print(average_buy_volume, average_sell_volume, average_total_volume)
    print(price_level)
    print(level_volume)
    return analysis_results
