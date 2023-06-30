def u_get_orders(symbol, coin_price):
    url = f"https://fapi.binance.com/fapi/v1/depth/"
    params = {
        'symbol': symbol,
        'limit': 1000,
        'price': 1,
        'timestamp': int(time.time() * 1000),
    }
    params = create_signature(params)
    print(params)
    res = send_get_header_req(url, params)
    return res


def u_combine_orders(coin_orders, orders_interval):
    order_types = ['asks', 'bids']
    combined_orders = {}
    interval_border = 0
    for order_type in order_types:
        combined_orders_list = []
        for order in coin_orders[order_types]:
            order_price = float(order[0])
            if order_type == 'asks':
                if order_price > interval_border:
                    interval_border = order_price + orders_interval
            elif order_type == 'bids':
                if order_price < interval_border:
                    interval_border = order_price - orders_interval
        combined_orders.update({order_type: combined_orders_list})
    return combined_orders


async def u_create_connection(stream_type, stream_name, symbol):
    url = f"wss://fstream.binance.com/{stream_type}/{symbol}@{stream_name}"
    print(url)
    async with websockets.connect(url) as client:
        data = json.loads(await client.recv())
        print(data)
