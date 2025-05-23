from algo_trading.utilities.utils import get_user_orders, cancel_open_orders, ask_bid
import time
import pandas as pd


def kill_switch(address, info, exchange, symbol):
    """
    Gets User info from setup(), passes in symbols
    to open_positions and then checks the balances
    so that we can close the positions
    """
    print(f'starting kill switch for {symbol}')

    while True:
        openPositions, has_positions = get_user_orders(address, info)
        if not has_positions:
            print('No open positions to close')
            return
        
        cancel_open_orders(address, info, exchange)
        
        for position in openPositions:
            symbol = position["symbol"]
            size = position["size"]
            long = position["long"]

            print(f'Closing position for {symbol} with size {size} and isLong: {long}')
            bid, ask = ask_bid(symbol)

            if long:
                price = ask
                print(f"selling {symbol} at {ask}")
            else:
                price = bid
                print(f"buying {symbol} at {bid}")

            order_result = exchange.order(
                symbol,
                not long,  # switches to opposite side
                size,
                price,
                {"limit": {"tif": "Gtc"}}
            )
            print(f"Order result for {symbol}: {order_result}")

        # Sleep for 30 seconds after processing all symbols
        print("Sleeping for 30 seconds before checking positions again...")
        time.sleep(30)
    
def main():
    pass  # This module is intended to be imported, not run directly.
          
if __name__ == "__main__":
    main()
    