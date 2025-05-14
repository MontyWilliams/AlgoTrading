
import ccxt
import json
from pprint import pprint
# from hyperliquid.utils import constants
from utils import setup, get_user_orders, cancel_open_orders
import time
import pandas as pd
import datetime
# import schedule
import requests
import os
import subprocess



def main():
    address, info, exchange, account = setup()
    get_user_orders()
    cancel_open_orders()
    user_state = info.user_state(address)
    
    positions = []
    for position in user_state["assetPositions"]:
        positions.append(position["position"])
    if len(positions) > 0:
        print("Positions:")
        # for position in positions:
        #     print(json.dumps(position, indent=2))
        pprint(user_state)
        print(account)
        print(info)
    try:
        subprocess.Popen(
            ['ffplay', '-nodisp', '-autoexit', 'coin.wav'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("Playing sound with ffplay.")
    except Exception as e:
        print(f"Error playing sound: {e}")

if __name__ == "__main__":
    main()