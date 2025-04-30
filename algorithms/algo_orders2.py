import time
from utils import setup

def main():
    address, info, exchange = setup()
    print(info.user_info)
    coin = "AR"
    is_buy = False
    sz = 0.1

    print(f"We try to Market {'Buy' if is_buy else 'Sell'} {sz} {coin}")

    order_result = exchange.market_open(coin, is_buy, sz, None, 0.01)
    if order_result ["status"] == "ok":
        for status in order_result["response"]["data"]["statuses"]:
            try:
                filled = status["filled"]
                print(f'Order #{filled["oid"]} filled {filled["totalSz"]} @filled["avgPx"]')
            except KeyError:
                print(f'Error: {status["error"]}')

        print("We wait for 2s before closing")
        time.sleep(2)

        print(f"We try to Market Colse all {coin}.")
        order_result = exchange.market_close(coin)
        if order_result["status"] == "ok":
            for status in order_result["response"]["data"]["statuses"]:
                try:
                    filled = status["filled"]
                    print(f'Order #{filled["oid"]} filled {filled["totalSz"]} @{filled["avgPx"]}')
                except KeyError:
                    print(f'Error: {status["error"]}')

if __name__ == " __main__":
    main()