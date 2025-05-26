from algo_trading.utilities.utils import setup, ask_bid, get_user_orders
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
    # Check PnL of open positions and close them if they reach the target or max loss.
    # pnl_close(10, 5)
    account_bal = float(info.user_state(address)["marginSummary"]["accountValue"])
    print(f"Account balance: {account_bal}")
    ask, bid, l2_data = ask_bid(symbol)
    df, latest_signal = ind_sma(symbol, 15, 1000, [20, 50])
    print(df)
    if latest_signal == "buy":
        size = round(account_bal * 0.9 / ask, 2)  # Use 90% of account balance for the trade
        print("Buy signal detected!")
        # Place a buy order
        kill_switch(address, info, exchange, symbol)
        order_result = exchange.order(
            symbol,
            True,  # Buy
            size,  # Size
            ask,  # Price
            {"limit": {"tif": "Gtc"}}
        )
        print(f"Order result: {order_result}")
    elif latest_signal == "sell":
        size = round(account_bal * 0.9 / bid, 2) 
        print("Sell signal detected!")
        # Place a sell order
        kill_switch(address, info, exchange, symbol)
        order_result = exchange.order(
            symbol,
            False,  # Sell
            size,  # Size
            bid,  # Price
            {"limit": {"tif": "Gtc"}}
        )
        print(f"Order result: {order_result}")
    else:
        print("No signal detected.")

def main():
    while True:
        try:
            sma_bot_00()
            time.sleep(60)  # Wait for 1 minute before checking again
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)  # Wait before retrying in case of an error
    
if __name__ == "__main__":
    main()