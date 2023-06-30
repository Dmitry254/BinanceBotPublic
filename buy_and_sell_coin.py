import time

from base_func import post_data_header, get_data, create_signature


def create_orders_and_levels(symbol, price, side):
    if side == "BUY":
        other_side = "SELL"
        stop_price = price * 0.98
        take_price = price * 1.03
    else:
        other_side = "BUY"
        stop_price = price * 1.02
        take_price = price * 0.97
    quantity = calculate_quantity(symbol, coin_price)
    limit_order = create_new_order(symbol, price, quantity, "LIMIT", side)
    stop_loss = create_stop_loss(symbol, stop_price, quantity, "LIMIT", other_side)
    take_profit = create_take_profit(symbol, take_price, quantity, "LIMIT", other_side)
    return limit_order, stop_loss, take_profit


def create_new_order(symbol, price, quantity, type, side):
    url = "https://fapi.binance.com/fapi/v1/order"
    params = {
        'symbol': symbol,
        'price': price,
        'quantity': quantity,
        'type': type,
        'side': side,
        'timeInForce': "GTC",
        'timestamp': int(time.time() * 1000)
    }
    print(params)
    params = create_signature(params)
    data = post_data_header(url, params)
    return data


def create_stop_loss(symbol, price, quantity, type, side):
    url = "https://fapi.binance.com/fapi/v1/order"
    params = {
        'symbol': symbol,
        'price': price,
        'quantity': quantity,
        'type': type,
        'side': side,
        'timeInForce': "GTC",
        'timestamp': int(time.time() * 1000)
    }
    print(params)
    params = create_signature(params)
    data = post_data_header(url, params)
    return data


def create_take_profit(symbol, price, quantity, type, side):
    url = "https://fapi.binance.com/fapi/v1/order"
    params = {
        'symbol': symbol,
        'price': price,
        'quantity': quantity,
        'type': type,
        'side': side,
        'timeInForce': "GTC",
        'timestamp': int(time.time() * 1000)
    }
    print(params)
    params = create_signature(params)
    data = post_data_header(url, params)
    return data


def create_level_orders(params):
    url = "https://fapi.binance.com/fapi/v1/order"
    return post_data_header(url, params)


def calculate_quantity(symbol, coin_price):
    precision = precisions_dict[symbol]
    quantity = float(f"{10 / coin_price:.{precision}f}")
    return quantity


def collect_coins_precisions():
    precisions_dict = {}
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    data = get_data(url, {})
    for coin in data['symbols']:
        precisions_dict.update({coin['symbol']: coin['pricePrecision'] - 1})
    return precisions_dict


if __name__ == "__main__":
    precisions_dict = collect_coins_precisions()
    coin_price = 400

    symbol = "BNBUSDT"
    price = 300
    order_type = 'asks'
    side = "BUY"
    limit_order, stop_loss, take_profit = create_orders_and_levels(symbol, price, side)
    print(limit_order)
    print(stop_loss)
    print(take_profit)
