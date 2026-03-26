import asyncio
import json
import os
from datetime import datetime
import pytz
from websockets import connect
from termcolor import cprint

"""
Track Liquidations on multiple exchanges to get the best picture of the market.Tracking:
    Binance: Center of crypto price, largest spot, massive retail "market wide confirmation"
    Bybit: High leverage, heavy perps, usually liqs, "early warning trigger"
    OKX: Larger, institutional structured positions, arbitrage, "smart money trigger"
    Hyperliquid: On chain perps, whale-heavy trading, transparent "whale positioning + forced exits"
"""

event = {
    "exchange": "",
    "time_stamp": "",
    "data": "data",             # dict of websocket data 
    "parsed": {                 # dict of parsed data, (varies by exchange)
        "symbol": "",
        "side": "",
        "price": 0.0,
        "size": 0.0,
        "usd_size": 0.0
    }
}
