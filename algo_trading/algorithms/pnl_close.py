from algo_trading.utilities.utils import setup, get_user_orders, ask_bid
import time
import pandas as pd
import json
from pprint import pprint
from kill_switch import kill_switch

target = 10
max_loss = -1

def pnl_close(target=target, max_loss=max_loss):
    address, info, exchange, account = setup()

    while True:
        openPositions, hasOpenPositions = get_user_orders(address, info)
        
        if not hasOpenPositions:
        
            print('No open positions...')
            return

        for position in openPositions:
            symbol = position['symbol']
            long = position['long']
            size = position['size']
            entry_price = float(position['entry_price'])
            leverage = float(position['leverage'])
            side = 'long' if long else 'short'
            current_price = ask_bid(symbol)[1]

            print(f'side: {side} | entry price: {entry_price} | leverage: {leverage}')
            if side == 'long':
                diff = current_price - entry_price
                long = True
            else:
                diff = entry_price - current_price
                long = False
            try:
                perc = round(((diff / entry_price) * leverage), 10)
            except:
                perc = 0

            perc = 100 * perc
            print(f'for {symbol} this is the PNL % {(perc)}%')
            pnlclose = False
            in_pos =False

            if perc > 0:
                in_pos = True
                print(f'In profit: {perc}%')
                if perc >= target:
                    print(f'Target reached: {target}%')
                    pnlclose = True
                    kill_switch(symbol)
                else:
                    print(f'Target not reached: {target}%')
            elif perc < 0:
                in_pos = True
                if perc <= max_loss:
                    print(f'Max loss reached: {max_loss}%. Closing position...')
                    kill_switch(symbol)
                else:
                    print(f'Max loss not reached: {max_loss}%. Current PnL: {perc}%')
            else:
                print('We are not in position')
            print(f' for {symbol} Just finished checking PnL')
            return pnlclose, in_pos, size, long
        print('sleep for 30 seconds')
        time.sleep(30)

def main():
    pnl_close(target, max_loss)

if __name__ == "__main__":
    main()