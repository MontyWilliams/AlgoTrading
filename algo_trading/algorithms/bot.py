import time
from algo_trading.utilities.utils import setup, get_sz_px_decimals, ask_bid, play_sound
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
import ccxt
import datetime
import requests
from pprint import pprint

symbol = "AR"
timeframe = "4h"
size = 10


def limit_order(coin, is_buy, sz, limit_px, reduce_only, account):
    """
    place a limit order
    """
    exchange = Exchange(account, constants.MAINNET_API_URL)
    rounding = get_sz_px_decimals(coin)[0]
    sz = round(sz, rounding)

    print(f'coin: {coin}')
    print(f'is_buy: {is_buy}')
    print(f'sz: {sz}')
    print(f'reduce-only: {reduce_only}')

    print(f'placing limit order for: {coin} {sz} @ {limit_px}')
    order_result = exchange.order(coin, is_buy, sz, limit_px, {"limit": {"tif": 'Gtc'}}, reduce_only=reduce_only)
    
    if is_buy:
        print(f"Limit BUY order placed: {order_result['response']['data']['statuses'][0]}")
    else:
        print(f"Limit SELL order placed: {order_result['response']['data']['statuses'][0]}")
    
    if order_result['response']['data']['statuses'][0] == 'FILLED':
        print(f"Hell yea! it went thru! Order status: {order_result['response']['data']['statuses'][0]}")
        play_sound('../sfx/coin.wav')
    else:
        print(f"Didnt go thru... Order status: {order_result['response']['data']['statuses'][0]}")
        play_sound('../sfx/flush_y.wav')
    return order_result

coin = symbol
is_buy = True
ask, bid, l2_data = ask_bid(coin)            
reduce_only = False
account = setup()[3]

limit_order(coin, is_buy, size, bid, reduce_only, account)

time.sleep(5)

is_buy = False
reduce_only =True

# Sell ordder

limit_order(coin, is_buy, size, ask, reduce_only, account)