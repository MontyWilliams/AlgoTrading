import asyncio
import json
import os
from datetime import datetime
import pytz
from websockets import connect
from termcolor import cprint
from toolUtils import play_sound
import threading

# List of Symbols to track
symbols = ['btcusdt', 'arusdt', 'taousdt']
websocket_url_base = 'wss://stream.binance.com/ws'
trades_filename = 'binance_trades.csv'

# Check if csv file exists
if not os.path.exists(trades_filename):
    with open(trades_filename, 'w') as f:
        f.write('Event Time, Symbol, Aggregate Trade ID, Price, Quantity, First Trade ID, Trade Time, Is Buyer Maker\n')

def sound_off(sound):
    def play_sound_thread(sound):
        # print(f"Playing sound: {sound}")
        if sound == 'SELL_SOUND':
            play_sound('./flush_y.wav')
        elif sound == 'BUY_SOUND':
            play_sound('./cash_register_x.wav')
        else:
            print(f"Unknown sound: {sound}")

    # Run the play_sound function in a separate thread
    thread = threading.Thread(target=play_sound_thread, args=(sound,))
    thread.daemon = True  # Ensure the thread exits when the main program exits
    thread.start()

async def binance_trade_stream(uri, symbol, filename):
    async with connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                event_time = datetime.fromtimestamp(data['E'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                agg_trade_id = data['a']
                price = float(data['p'])
                quantity = float(data['q'])
                trade_time = int(data['T'])
                is_buyer_maker = data['m']
                utc = pytz.UTC
                usd_size = price * quantity
                display_symbol = symbol.upper().replace('USDT', '')

                #print different colors under certain conditions (add sounds later)
                trade_type = 'SELL' if is_buyer_maker else 'BUY'
                color = 'red' if trade_type == 'SELL' else 'green'
                sound = 'SELL_SOUND' if is_buyer_maker else 'BUY_SOUND'

                if usd_size > 14999:
                    stars = ''
                    attrs = ['bold'] if usd_size >= 50000 else []
                    repeat_count = 1
                    if usd_size >= 500000:
                        stars = '*' * 5
                        repeat_count = 1
                        if trade_type == 'SELL':
                            color = 'magenta'
                        else:
                            color = 'blue'
                    elif usd_size >= 100000:
                        stars = '*' * 3
                        repeat_count = 1
                    elif usd_size >= 50000:
                        stars = '*' * 2
                        repeat_count = 1
                    elif usd_size >= 10000:
                        stars = '*' * 1
                        repeat_count = 1
                    elif usd_size <= 1000:
                        stars = ''
                        repeat_count = 1
            
                    output = f"{stars} {trade_type} {display_symbol} {event_time} ${usd_size:,.0f} {stars}"
                    for _ in range(repeat_count):
                        cprint(output, 'white', f'on_{color}', attrs=attrs)
                        sound_off(sound)
                    
                    # Write to CSV file
                    with open(filename, 'a') as f:
                        f.write(f"{event_time}, {symbol.upper()}, {agg_trade_id}, {price}, {quantity},"
                                f"{trade_time},{is_buyer_maker}\n")


            except Exception as e:
                await asyncio.sleep(5)
                cprint(f"Error: {e}", 'red')

async def main():
    filename = 'binance_trades.csv'

    # Create a task for each symbol trade stream
    tasks = []
    for symbol in symbols:
        stream_url = f"{websocket_url_base}/{symbol}@aggTrade"
        tasks.append(binance_trade_stream(stream_url, symbol, filename))

    await asyncio.gather(*tasks)

asyncio.run(main())