import asyncio
import json
from datetime import datetime
from websockets import connect  
from termcolor import cprint
import random

symbols = ['btcusdt', 'taousdt', 'suiusdt', 'arusdt']
websocket_url_base = 'wss://fstream.binance.com/ws/'

shared_symbol_counter = {'count': 0}
print_lock = asyncio.Lock()

async def binance_funding_stream(symbol, shared_counter):
    websocket_url = f'{websocket_url_base}{symbol}@markPrice'
    async with connect(websocket_url) as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                event_time = datetime.fromtimestamp(data['E'] / 1000).strftime('%H:%M:%S')
                symbol_display = data['s'].replace('USDT', '')
                funding_rate = float(data['r'])
                yearly_funding_rate = (funding_rate * 3 * 365) * 100
                # daily_funding_rate = (funding_rate * 3) * 100
                
                if yearly_funding_rate > 50:
                    text_color, back_color = 'white', 'on_red'
                elif yearly_funding_rate > 30:
                    text_color, back_color = 'white', 'on_yellow'
                elif yearly_funding_rate > 5:
                    text_color, back_color = 'white', 'on_cyan'
                elif yearly_funding_rate < -10:
                    text_color, back_color = 'white', 'on_green'
                else:
                    text_color, back_color = 'white', 'on_blue'

                async with print_lock:
                    cprint(f"{symbol_display} funding: {yearly_funding_rate:.2f}%", text_color, back_color)
                    # cprint(f"{symbol_display} funding: {daily_funding_rate:.2f}%", text_color, back_color)
                
                shared_counter['count'] += 1
                if shared_counter['count'] >= len(symbols):
                    async with print_lock:
                        cprint(f"{event_time} yrly fund", 'blue', 'on_yellow')
                        # cprint(f"{event_time} daily fund", 'white', 'on_yellow')
                    shared_counter['count'] = 0
            except Exception as e:
                print(f"[{symbol}] WebSocket error: {e}")
                await asyncio.sleep(5)

async def main():
    tasks = [binance_funding_stream(symbol, shared_symbol_counter) for symbol in symbols]
    await asyncio.gather(*tasks)

asyncio.run(main())