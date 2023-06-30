import requests
import json
import hmac
import hashlib

from key import api_key_binance, secret_binance


def set_order_interval(coin_price):
    price_precision = coin_price * 0.0001
    return price_precision


def get_params(**params):
    pass


def get_string_from_dict(params):
    params_string = ""
    for key in params:
        params_string += f"{key}={params[key]}&"
    return params_string[:-1]


def create_signature(params):
    local_params = params
    if type(params) is dict:
        local_params = get_string_from_dict(params)
    secret_key = secret_binance.encode('utf-8')
    local_params = local_params.encode('utf-8')
    signature = hmac.new(secret_key, local_params, hashlib.sha256).hexdigest()
    if type(params) is dict:
        params.update({'signature': signature})
    elif type(params) is str:
        params += f"&signature={signature}"
    return params


def get_data(url, params):
    data = requests.get(url, params=params)
    res = json.loads(data.text)
    return res


def get_data_header(url, params):
    data = requests.get(url, headers={'X-MBX-APIKEY': api_key_binance}, params=params)
    res = json.loads(data.text)
    return res


def post_data_header(url, params):
    data = requests.post(url, headers={'X-MBX-APIKEY': api_key_binance}, params=params)
    res = json.loads(data.text)
    return res


params = {"id": "", "key": ""}
data = requests.post("https://ymscanner.com/api/price", params=params)
print(data)
res = json.loads(data.text)
print(res)
