import openpyxl
import time
import datetime

from base_func import get_data


def create_result_text(analysis_result):
    three_percent_result, five_percent_result, two_percent_result = analysis_result
    result_text = [0, 0, 0]
    if three_percent_result != 0 and three_percent_result < two_percent_result != 0:
        result_text[0] = three_percent_result
    if five_percent_result != 0 and five_percent_result < two_percent_result != 0:
        result_text[1] = five_percent_result
    if two_percent_result != 0 and three_percent_result == 0 and five_percent_result == 0:
        result_text[2] = two_percent_result
    if three_percent_result != 0 and two_percent_result == 0:
        result_text[0] = three_percent_result
    if five_percent_result != 0 and two_percent_result == 0:
        result_text[1] = five_percent_result
    if three_percent_result != 0 and three_percent_result > two_percent_result != 0:
        result_text[2] = two_percent_result
    if five_percent_result != 0 and three_percent_result > two_percent_result  != 0 and five_percent_result > two_percent_result != 0:
        result_text[2] = two_percent_result
    return result_text


def get_candles(symbol, start_time):
    end_time = int(time.time() * 1000)
    url = f"https://fapi.binance.com/fapi/v1/klines"
    params = {
        'symbol': symbol,
        'interval': "1m",
        'startTime': start_time,
        'endTime': end_time,
        'limit': 241
    }
    res = get_data(url, params)
    return res


def analysis_candles(candles, coin_price, price_level, order_type):
    three_percent_result = 0
    five_percent_result = 0
    two_percent_result = 0
    if order_type == 'asks':
        three_percent_profit = price_level * 1.03
        five_percent_profit = price_level * 1.05
        two_percent_loss = price_level * 0.97
        for candle in candles:
            if three_percent_profit < float(candle[2]):
                minutes = candles.index(candle)
                if three_percent_result == 0:
                    three_percent_result = minutes + 1
            if five_percent_profit < float(candle[2]):
                minutes = candles.index(candle)
                if five_percent_result == 0:
                    five_percent_result = minutes + 1
            if two_percent_loss > float(candle[3]):
                minutes = candles.index(candle)
                if two_percent_result == 0:
                    two_percent_result = minutes + 1
    elif order_type == 'bids':
        three_percent_profit = price_level * 0.97
        five_percent_profit = price_level * 0.95
        two_percent_loss = price_level * 1.03
        for candle in candles:
            if three_percent_profit > float(candle[3]):
                minutes = candles.index(candle)
                if three_percent_result == 0:
                    three_percent_result = minutes + 1
            if five_percent_profit > float(candle[3]):
                minutes = candles.index(candle)
                if five_percent_result == 0:
                    five_percent_result = minutes + 1
            if two_percent_loss < float(candle[2]):
                minutes = candles.index(candle)
                if two_percent_result == 0:
                    two_percent_result = minutes + 1
    analysis_result = [three_percent_result, five_percent_result, two_percent_result]
    return analysis_result


def get_volume(symbol, start_time):
    # print(symbol)
    url = f"https://fapi.binance.com/futures/data/takerlongshortRatio"
    params = {
        'symbol': symbol,
        'period': "5m",
        'limit': 400,
        'startTime': start_time - 15300000,
        'endTime': start_time
    }
    res = get_data(url, params)
    return res


def analysis_volumes(volumes, info_date, result_text, order_type):
    signal_time = False

    average_first_ten_buy_volume = 0
    average_first_ten_sell_volume = 0
    average_first_ten_sum_volume = 0

    before_signal_buy_volume = 0
    before_signal_sell_volume = 0
    before_signal_volume_counter = 0

    during_signal_buy_volume = 0
    during_signal_sell_volume = 0
    during_signal_volume_counter = 0

    level_signal_buy_volume = 0
    level_signal_sell_volume = 0
    level_signal_sum_volume = 0
    for volume in volumes:
        if volume['timestamp'] < info_date:
            before_signal_buy_volume += float(volume['buyVol'])
            before_signal_sell_volume += float(volume['sellVol'])
            before_signal_volume_counter += 1
            if before_signal_volume_counter == 10:
                try:
                    average_first_ten_buy_volume = before_signal_buy_volume / before_signal_volume_counter
                    average_first_ten_sell_volume = before_signal_sell_volume / before_signal_volume_counter
                except ZeroDivisionError:
                    pass
                average_first_ten_sum_volume = average_first_ten_buy_volume + average_first_ten_sell_volume
            if signal_time:
                during_signal_buy_volume += float(volume['buyVol'])
                during_signal_sell_volume += float(volume['sellVol'])
                during_signal_volume_counter += 1
        if volume['timestamp'] > info_date:
            if signal_time and level_signal_sum_volume == 0 and (result_text[0] != 0 or result_text[2] != 0):
                level_signal_buy_volume = float(volume['buyVol'])
                level_signal_sell_volume = float(volume['sellVol'])
                level_signal_sum_volume = level_signal_buy_volume + level_signal_sell_volume
            if not signal_time:
                if result_text[0] != 0:
                    info_date = info_date + result_text[0] * 60000
                if result_text[1] != 0:
                    info_date = info_date + result_text[1] * 60000 - result_text[0] * 60000
                if result_text[2] != 0:
                    info_date = info_date + result_text[2] * 60000
                if result_text[0] == 0 and result_text[2] == 0:
                    info_date = info_date + 245 * 60000
            if volumes[52] == volume and not signal_time:
                signal_time = volumes[52]
            elif volumes[52] != volume and not signal_time:
                signal_time = volumes[51]
    if not before_signal_volume_counter == 0:
        average_before_signal_buy_volume = before_signal_buy_volume / before_signal_volume_counter
        average_before_signal_sell_volume = before_signal_sell_volume / before_signal_volume_counter
        average_before_signal_sum_volume = average_before_signal_buy_volume + average_before_signal_sell_volume
    else:
        average_before_signal_buy_volume = 0
        average_before_signal_sell_volume = 0
        average_before_signal_sum_volume = 0
    if order_type == 'asks':
        volumes_list = [average_first_ten_buy_volume, average_first_ten_sum_volume,
                        average_before_signal_buy_volume, average_before_signal_sum_volume,
                        level_signal_buy_volume, level_signal_sum_volume]
        return volumes_list
    if order_type == 'bids':
        volumes_list = [average_first_ten_sell_volume, average_first_ten_sum_volume,
                        average_before_signal_sell_volume, average_before_signal_sum_volume,
                        level_signal_sell_volume, level_signal_sum_volume]
        return volumes_list


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
                return False
        for price in m_candles:
            if float(price[2]) > price_level:
                return False
    if order_type == 'bids':
        for price in h_candles:
            if float(price[3]) < price_level:
                return False
        for price in m_candles:
            if float(price[3]) < price_level:
                return False
    return True


def collect_deal_params(params):
    symbol, coin_link, order_type, coin_price, price_level, days_ago, level_touches, level_volume, \
    average_buy_volume, average_sell_volume, average_total_volume, info_date = params
    candles = get_candles(symbol, info_date)
    analysis_candles_result = analysis_candles(candles, coin_price, price_level, order_type)
    result_text = create_result_text(analysis_candles_result)
    volumes = get_volume(symbol, info_date)
    analysis_volumes_result = analysis_volumes(volumes, info_date, result_text, order_type)
    day_prices = check_day_prices(symbol, info_date, price_level, order_type)


if __name__ == "__main__":
    collect_stats()
