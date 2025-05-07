from utils import setup, get_user_orders, cancel_open_orders, ask_bid
import time
import pandas as pd
import json
from pprint import pprint

symbol = ''


def kill_switch(symbol=symbol):
    """
    Gets User info from setup(), passes in symbols
    to open_positions and then checks the balances
    so that we can close the positions
    """
    print(f'starting kill switch for {symbol}')
    address, info, exchange, account = setup()
    openPositions, has_positions = get_user_orders(address, info)
    if not has_positions:
        print('No open positions to close')
        return
    for position in openPositions:
        symbol = position["symbol"]
        size = position["size"]
        long = position["long"]
        
        print(f'Closing position for {symbol} with size {size} and isLong: {long}')
        cancel_open_orders(address, info, exchange)
        bid, ask = ask_bid(symbol)
        if long:
            price = ask
            print(f"selling {symbol} at {ask}")
        else:
            price = bid
            print(f"buying {symbol} at {bid}")
        order_result = exchange.order(
            symbol,
            not long, # switches to opposite side
            size,
            price,
            {"limit": {"tif": "Gtc"}}
        )
        print(f"Order result for {symbol}: {order_result}")
        print("sleeping for 30 seconds")
        time.sleep(30)
    
def main():
    kill_switch(symbol)
          
if __name__ == "__main__":
    main()
    