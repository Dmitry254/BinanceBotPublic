import time
import datetime
import traceback

from threading import Thread
from key import api_key_binance
# from tg_bot import message, send_text_message
from tg_notice import collect_notice
from base_func import get_data, post_data_header
from coin_analysis import start_analysis
from create_deal_params import collect_deal_params


def get_all_coins():
    url = f"https://api.binance.com/api/v3/exchangeInfo"
    params = {}
    res = get_data(url, params)
    spot_coins_list = [x['symbol'] for x in res['symbols'] if x['isSpotTradingAllowed'] and "USDT" in x['symbol']
                         and not x['symbol'][0:4] in black_list]
    margin_coins_list = [x['symbol'] for x in res['symbols'] if x['isMarginTradingAllowed'] and "USDT" in x['symbol']
                         and not x['symbol'][0:4] in black_list]
    return spot_coins_list, margin_coins_list


def get_current_price(symbols):
    current_prices = {}
    for symbol in symbols:
        url = f'https://api.binance.com/api/v3/avgPrice'
        params = {'symbol': symbol}
        res = get_data(url, params)
        current_prices.update({symbol: res['price']})
    return current_prices


def get_trades(symbols):
    for symbol in symbols:
        url = f"https://api.binance.com/api/v3/trades"
        params = {'symbol': symbol}
        res = get_data(url, params)
        return res


def get_candles(symbols, interval):
    candles_history = {}
    end_time = int(time.time() * 1000)
    start_times = ["%.0f" % (end_time - 86400000 * interval_of_days * x) for x in range(0, number_of_intervals)]
    for symbol in symbols:
        coin_max_and_min = []
        for time_number in range(number_of_intervals - 1):
            end_time = start_times[0 + time_number]
            start_time = start_times[1 + time_number]
            if start_time != start_times[-1]:
                max_candle_price = -1
                min_candle_price = 99999999999
                url = f"https://api.binance.com/api/v3/klines"
                params = {
                    'symbol': symbol,
                    'interval': interval,
                    'startTime': start_time,
                    'endTime': end_time,
                    'limit': int(20 * interval_of_days)
                }
                res = get_data(url, params)
                for candle in res:
                    if float(candle[2]) > max_candle_price:
                        max_candle_price = float(candle[2])
                    if float(candle[3]) < min_candle_price:
                        min_candle_price = float(candle[3])
                coin_max_and_min += [[max_candle_price, min_candle_price]]
        candles_history.update({symbol: coin_max_and_min})
    return candles_history


def search_close_levels(symbols):
    global notice_list
    for symbol in symbols:
        coin_current_price = float(current_prices[symbol])
        for coin_history_prices in candles_history[symbol]:
            if candles_history[symbol].index(coin_history_prices) == 0:
                continue
            coin_history_price_max = float(coin_history_prices[0])
            coin_history_price_min = float(coin_history_prices[1])
            if coin_current_price * close_percent > coin_history_price_max > coin_current_price / close_percent\
                    and coin_current_price < coin_history_price_max:
                interval_number = candles_history[symbol].index(coin_history_prices) + 1
                check_history_result = check_history_prices(symbol, coin_history_price_max, coin_current_price,
                                                            interval_number, 0)
                if check_history_result:
                    notice_data = f"{symbol}, {coin_history_price_max}, {interval_number * interval_of_days}"
                    if notice_data not in notice_list:
                        coin_link = f"https://www.binance.com/ru/futures/{symbol}_perpetual"
                        result_text = f"[{symbol}]({coin_link}) по цене {'%.2f' % coin_current_price} близок к максимальному уровню {coin_history_price_max}, который был около " \
                                      f"{interval_number * interval_of_days} дней назад, было {check_history_result} касаний уровня"
                        last_time = int(time.time() * 1000) - 86400000 * interval_of_days * number_of_intervals
                        # op = Thread(target=start_analysis, args=(symbol, coin_current_price, interval_number * interval_of_days,
                        #                                          coin_history_price_max, 'asks',))
                        # op.start()
                        analysis_results = start_analysis(symbol, coin_current_price,
                                                          interval_number * interval_of_days,
                                                          coin_history_price_max, 'asks')
                        if analysis_results != "Сoin is not traded":
                            notice_list = collect_notice(notice_list, notice_data)
                            if check_day_prices(symbol, int(time.time() * 1000), coin_history_price_max, 'asks'):
                                statistics_list = [symbol, coin_link, 'asks', analysis_results[0], analysis_results[1],
                                                   interval_number * interval_of_days, check_history_result,
                                                   analysis_results[2], analysis_results[3], analysis_results[4],
                                                   analysis_results[5], datetime.datetime.now()]
                                # send_text_message(message, result_text)
                                collect_deal_params(statistics_list)
                                print(result_text)
                        else:
                            margin_coins_list.pop(margin_coins_list.index(symbol))
            if coin_current_price * close_percent > coin_history_price_min > coin_current_price / close_percent\
                    and coin_current_price > coin_history_price_min:
                interval_number = candles_history[symbol].index(coin_history_prices) + 1
                check_history_result = check_history_prices(symbol, coin_history_price_min, coin_current_price,
                                                            interval_number, 1)
                if check_history_result:
                    notice_data = f"{symbol}, {coin_history_price_min}, {interval_number * interval_of_days}"
                    if notice_data not in notice_list:
                        coin_link = f"https://www.binance.com/ru/futures/{symbol}_perpetual"
                        result_text = f"[{symbol}]({coin_link}) по цене {'%.2f' % coin_current_price} близок к минимальному уровню {coin_history_price_min}, который был около " \
                                      f"{interval_number * interval_of_days} дней назад, было {check_history_result} касаний уровня"
                        last_time = int(time.time() * 1000) - 86400000 * interval_of_days * number_of_intervals
                        # op = Thread(target=start_analysis, args=(symbol, coin_current_price, interval_number * interval_of_days,
                        #                                          coin_history_price_min, 'bids',))
                        # op.start()
                        analysis_results = start_analysis(symbol, coin_current_price, interval_number * interval_of_days,
                                       coin_history_price_min, 'bids')
                        if analysis_results != "Сoin is not traded":
                            notice_list = collect_notice(notice_list, notice_data)
                            if check_day_prices(symbol, int(time.time() * 1000), coin_history_price_min, 'bids'):
                                statistics_list = [symbol, coin_link, 'bids', analysis_results[0], analysis_results[1],
                                                   interval_number * interval_of_days, check_history_result,
                                                   analysis_results[2], analysis_results[3], analysis_results[4],
                                                   analysis_results[5], datetime.datetime.now()]
                                # send_text_message(message, result_text)
                                collect_deal_params(statistics_list)
                                print(result_text)
                        else:
                            margin_coins_list.pop(margin_coins_list.index(symbol))


def check_history_prices(symbol, coin_history_price, coin_current_price, interval_number, min_or_max):
    """
    Проверка были ли пробои и касания уровня по интервалам
    """
    counter = 1
    for check_coin_history_prices in candles_history[symbol]:
        current_interval_number = candles_history[symbol].index(check_coin_history_prices) + 1
        check_coin_history_price = float(check_coin_history_prices[min_or_max])
        if current_interval_number == interval_number:
            break
        if min_or_max == 0:
            if coin_history_price * 1.005 < check_coin_history_price:
                coin_link = f"https://www.binance.com/ru/trade/{symbol}?layout=pro"
                result_text = f"[{symbol}]({coin_link}) по цене {'%.2f' % coin_current_price} близок к максимальному уровню {coin_history_price}, который был около " \
                              f"{interval_number * interval_of_days} дней назад, но около {current_interval_number * interval_of_days} дней назад был уровень {check_coin_history_price}"
                # print(result_text)
                return False
            if coin_history_price * 1.005 > check_coin_history_price > coin_history_price / 1.005:
                counter += 1
        elif min_or_max == 1:
            if coin_history_price / 1.005 > check_coin_history_price:
                coin_link = f"https://www.binance.com/ru/trade/{symbol}?layout=pro"
                result_text = f"[{symbol}]({coin_link}) по цене {'%.2f' % coin_current_price} близок к минимальному уровню {coin_history_price}, который был около " \
                              f"{interval_number * interval_of_days} дней назад, но около {current_interval_number * interval_of_days} дней назад был уровень {check_coin_history_price}"
                # print(result_text)
                return False
            if coin_history_price * 1.005 < check_coin_history_price < coin_history_price * 1.005:
                counter += 1
    return counter


def get_candles_for_check(symbol, info_date, interval, time_delta):
    url = f"https://api.binance.com/api/v3/klines"
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': info_date - time_delta,
        'endTime': info_date,
        'limit': 200
    }
    res = get_data(url, params)
    return res


def check_day_prices(symbol, info_date, price_level, order_type):
    h_candles = get_candles_for_check(symbol, info_date - 3600000, "2h", 172800000)
    m_candles = get_candles_for_check(symbol, info_date, "1m", 7200000)
    if order_type == 'asks':
        for price in h_candles:
            if float(price[2]) > price_level:
                print(1, info_date, symbol)
                return False
        for price in m_candles:
            if float(price[2]) > price_level:
                print(2, info_date, symbol)
                return False
    if order_type == 'bids':
        for price in h_candles:
            if float(price[3]) < price_level:
                print(3, info_date, symbol)
                return False
        for price in m_candles:
            if float(price[3]) < price_level:
                print(4, info_date, symbol)
                return False
    return True


if __name__ == "__main__":
    interval_of_days = 2
    number_of_intervals = 30
    close_percent = 1.05
    notice_list = []
    black_list = ["USDC", "BUSD", "TUSD", "EURU"]
    spot_coins_list, margin_coins_list = get_all_coins()
    margin_coins_list = margin_coins_list[0:5]
    current_prices = get_current_price(margin_coins_list)
    print(current_prices)
    candles_history = get_candles(margin_coins_list, "2h")
    current_day = datetime.date.today().day
    while True:
        try:
            script_start_time = datetime.datetime.now()
            search_close_levels(margin_coins_list)
            time.sleep(1)
            if current_day < datetime.date.today().day:
                candles_history = get_candles(margin_coins_list, "2h")
                print("Обновлены данные по свечам")
                current_day = datetime.date.today().day
            current_prices = get_current_price(margin_coins_list)
            end_start_time = datetime.datetime.now()
        except:
            traceback.print_exc()

