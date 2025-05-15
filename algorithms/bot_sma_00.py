from utils import setup
from pprint import pprint

def sma_bot_00():
    """
    This bot is a simple moving average bot that uses the 20, 41, and 75 period moving averages
    to determine the trend of the market. It will buy when the 20 period moving average crosses
    above the 41 period moving average and sell when the 20 period moving average crosses below
    the 41 period moving average.
    """
    # Setup
    address, info, exchange, account = setup()
    print("address type:", type(address))
    pprint(dir(info))
    pprint(dir(exchange))
    pprint(dir(account))

def main():
    sma_bot_00()
if __name__ == "__main__":
    main()