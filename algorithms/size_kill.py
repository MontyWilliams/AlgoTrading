from utils import setup, get_user_orders, ask_bid
import time
import pandas as pd
import json
from pprint import pprint
from kill_switch import kill_switch

def size_kill():
    max_risk = 1

    address, info, exchange, account = setup()
    openPositions, hasOpenPositions = get_user_orders(address, info) # unpack stale values in case of no positions

    if not hasOpenPositions:
        print('No open positions...')
        return
    
    for position in openPositions:
        symbol = position['symbol']
        pnl = position['pnl']
        size = position['size']
        long = position['long']
        side = 'buy' if long else 'sell'
    try:
        pos_cost = abs(float(pnl))
        pos_side = side
        pos_size = size
    except:
        pos_cost = 0
        pos_side = ''
        pos_size = 0   
    print(f'Position cost: {pos_cost}')
    print(f'Position side: {pos_side}')

    if pos_cost > max_risk:
        print(f'EMERGENCY KILL SWITCH ACTIVATED DUE TO CURRENT POSITION SIZE OF {pos_cost} OVER MAX RISK OF: {max_risk}')
        kill_switch(symbol) # just calling the kill switch cause the code below is long
        time.sleep(30000)
    else:
        print(f'size kill check: current position cost is: {pos_cost} we are gucci')

def main():
    size_kill()
if __name__ == "__main__":
    main()