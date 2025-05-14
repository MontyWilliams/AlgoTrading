import asyncio
import json
from datetime import datetime
from websockets import connect
from termcolor import cprint

symbols = ['btcusdt', 'ethusdt', 'solusdt', 'taousdt', 'suiusdt', 'arusdt', 'pepeusdt']
websocket_url_base = 'wss://fstream.binance.com/ws/'

shared_symbol_counter = {'count': 0}
print_lock = asyncio.Lock()
previous_values = {}  # Store previous funding rates

async def binance_funding_stream(symbol, shared_counter):
    websocket_url = f'{websocket_url_base}{symbol}@markPrice'
    while True:
        try:
            async with connect(websocket_url) as websocket:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    event_time = datetime.fromtimestamp(data['E'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    symbol_display = data['s'].replace('USDT', '')
                    funding_rate = float(data['r'])
                    yearly_funding_rate = (funding_rate * 3 * 365) * 100

                    # Only print if the value has changed
                    if symbol not in previous_values:
                        previous_values[symbol] = yearly_funding_rate

                        if yearly_funding_rate > 50:
                            text_color, back_color = 'white', 'on_blue'
                        elif yearly_funding_rate > 30:
                            text_color, back_color = 'white', 'on_blue'
                        elif yearly_funding_rate > 5:
                            text_color, back_color = 'white', 'on_blue'
                        elif yearly_funding_rate < -10:
                            text_color, back_color = 'white', 'on_blue'
                        else:
                            text_color, back_color = 'white', 'on_blue'

                        async with print_lock:
                            cprint(f"{symbol_display} funding: {yearly_funding_rate:.2f}%", text_color, back_color)

                            shared_counter['count'] += 1
                            if shared_counter['count'] >= len(symbols):
                                cprint(f"{event_time} yrly fund", 'white', 'on_black')
                                shared_counter['count'] = 0

        except Exception as e:
            print(f"[{symbol}] WebSocket error: {e}")
            await asyncio.sleep(5)

async def main():
    tasks = [binance_funding_stream(symbol, shared_symbol_counter) for symbol in symbols]
    await asyncio.gather(*tasks)

asyncio.run(main())
