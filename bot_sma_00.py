from algo_trading.utilities.utils import setup, ask_bid, get_user_orders
from  algo_trading.algorithms.pnl_close import pnl_close
from algo_trading.algorithms.kill_switch import kill_switch
from algo_trading.indicators.ind_sma import ind_sma
from pprint import pprint
import time

symbol = "AR"

address, info, exchange, account = setup()

ask_bid(symbol)

def sma_bot_00():
    """
    This bot is a simple moving average bot that uses the 20, 41, and 75 period moving averages
    to determine the trend of the market. It will buy when the 20 period moving average crosses
    above the 41 period moving average and sell when the 20 period moving average crosses below
    the 41 period moving average.
    """
    # kill_switch(address, info, exchange, symbol)
    ask, bid, l2_data = ask_bid(symbol)
    df = ind_sma(symbol, 15, 1000, [20, 50])
    pnl_close(10, 5)
def main():
    while True:
        sma_bot_00()
        time.sleep(30)
if __name__ == "__main__":
    main()