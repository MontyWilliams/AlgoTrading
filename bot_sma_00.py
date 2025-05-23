from algo_trading.utilities.utils import setup, ask_bid
from algo_trading.algorithms.kill_switch import kill_switch
from algo_trading.indicators.ind_sma import ind_sma
from pprint import pprint

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
    # kill_switch(address, info, exchange, "AR")
    ask, bid, l2_data = ask_bid(symbol)
    # pprint(f"ask: {ask} | bid: {bid} | l2_data: {l2_data}")
    df = ind_sma(symbol, 15, 1000, [20, 50])
    counts = df['crossover_20_50m'].value_counts()
    print(counts)   
def main():
    sma_bot_00()
if __name__ == "__main__":
    main()