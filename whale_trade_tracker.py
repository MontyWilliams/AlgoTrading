import asyncio
import json
import os
from datetime import datetime
import pytz
from websockets import connect
from termcolor import cprint

# list of symbols to track
# Consider how usdt inflow means people are trying to get into crypto while outflow means people are selling
symbols  = ["BTCUSDT", "ethusdt", "solusdt", "bnbusdt", "xrpusdt"]
websocket_url_base = 'wss://fstream.binance.com/ws/'
trades_filename = "binance_whale_trades.csv"
COLUMN_WIDTH = 22

# Create the CSV file with headers if it doesn't exist. The whale tracker uses aggregate trades and shouldnt be used
# for backtesting.
if not os.path.isfile(trades_filename):
    with open(trades_filename, 'w') as f:
        f.write("Event Time, Symbol, Aggregate Trade ID, Price, Quantity, First Trade ID, Trade Time, Is Buyer Maker\n")

async def binance_trade_stream(uri, symbol, filename):
    async with connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                event_time = int(data['E'])
                agg_trade_id = data['a']
                price = float(data['p'])
                quantity = float(data['q'])
                trade_time = int(data['T'])
                is_buyer_maker = data['m']
                est = pytz.timezone('US/Eastern')
                readable_trade_time = datetime.fromtimestamp(trade_time / 1000, est).strftime('%H:%M:%S')
                usd_size = price * quantity
                display_symbol = symbol.upper().replace("USDT", "")

                if usd_size > 14999:
                    trade_type = "SELL" if is_buyer_maker else "BUY"
                    color = "red" if trade_type == "SELL" else "green"

                    stars = ""
                    attrs = ["bold"] if usd_size >= 50000 else []
                    repeat_count = 1
                    star_level = 0

                    if usd_size >= 500000:
                        stars = "*" * 2
                        repeat_count = 1
                        star_level = 2
                        if trade_type == "SELL":
                            color = "magenta"
                        else:
                            color = "blue"

                    elif usd_size >= 100000:
                        stars = "*" * 1
                        repeat_count = 1
                        star_level = 1

                    tier_text = f"{stars} {display_symbol} {readable_trade_time} ${usd_size:,.0f} {stars}".strip()
                    indent = (COLUMN_WIDTH + 3) * star_level
                    
                    for _ in range(repeat_count):
                        print(" " * indent, end="")
                        cprint(tier_text, "white", f'on_{color}', attrs=attrs)

                    # log the trade to the CSV file
                    with open(filename, 'a') as f:
                        f.write(f"{event_time}, {symbol}, {agg_trade_id}, {price}, {quantity}, {data['f']}, {trade_time}, {is_buyer_maker}\n")

            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(1)

async def main():
    filename = "binance_trades.csv"
    print(f"{'NO STAR':<{COLUMN_WIDTH}} | {'* STAR':<{COLUMN_WIDTH}} | {'** STAR':<{COLUMN_WIDTH}}")
    # print("-" * ((COLUMN_WIDTH * 3) + 6))
    tasks = []
    for symbol in symbols:
        stream_url = f"{websocket_url_base}{symbol.lower()}@aggTrade"
        tasks.append(asyncio.create_task(binance_trade_stream(stream_url, symbol, filename)))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())