import asyncio
import json
import os
from datetime import datetime
import pytz
from websockets import connect
from termcolor import cprint


websocket_url = 'wss://fstream.binance.com/ws/!forceOrder@arr'
filename = 'binance_liq.csv'

if not os.path.isfile(filename):
    with open(filename, 'w') as f:
        f.write(",".join([
            'symbol', 'side', 'order_type', 'time_in_force', 'original_quantity', 'price', 'average_price', 'order_status', 'order_last_filled_quantity', 'order_filled_accumulated_quantity', 'order_trade_time', 'usd_size'
        ]) + "\n")