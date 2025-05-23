import asyncio
import json
import os
from datetime import datetime
import pytz
from websockets import connect
from termcolor import colored, cprint
from collections import defaultdict
from playsound import playsound

symbols = ['btcusdt', 'arusdt', 'taousdt']
websocket_url_base = 'wss://stream.binance.com/ws'

latest_trades = defaultdict(dict)
lock = asyncio.Lock()

def format_trade_cell(trade_type, symbol, time_str, usd, stars, color, attrs):
    display = f"{stars} {trade_type} {symbol.upper().replace('USDT', '')} {time_str} ${usd:,.0f}"
    return colored(f"{display:<35}", 'white', f'on_{color}', attrs=attrs)

async def binance_trade_stream(uri, symbol):
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
                est = pytz.UTC
                readable_trade_time = datetime.fromtimestamp(trade_time / 1000, est).strftime('%H:%M:%S')
                usd_size = price * quantity
                trade_type = 'SELL' if is_buyer_maker else 'BUY'
                color = 'red' if trade_type == 'SELL' else 'green'
                stars = ''
                attrs = []

                # Extra highlighting for big trades
                if usd_size >= 500000:
                    stars = '***'
                    color = 'magenta' if trade_type == 'SELL' else 'blue'
                    attrs = ['bold']
                elif usd_size >= 100000:
                    stars = '**'
                    attrs = ['bold']
                elif usd_size >= 50000:
                    stars = '*'
                    attrs = ['bold']
                elif usd_size <= 1000:
                    attrs = ['reverse']
                  

                row_outputs = []
                async with lock:
                    latest_trades[symbol] = {
                        'trade_type': trade_type,
                        'time': readable_trade_time,
                        'usd': usd_size,
                        'stars': stars,
                        'color': color,
                        'attrs': attrs
                    }

            except Exception as e:
                await asyncio.sleep(5)
                cprint(f"Error: {e}", 'red')

last_displayed = {}
async def display_loop():
    while True:
        await asyncio.sleep(0.1)
        row_outputs = []
        updated = False

        async with lock:
            for symbol in symbols:
                trade = latest_trades.get(symbol)
                last = last_displayed.get(symbol)

                if trade and trade != last:
                    updated = True
                    last_displayed[symbol] = trade
                    cell = format_trade_cell(
                        trade['trade_type'],
                        symbol,
                        trade['time'],
                        trade['usd'],
                        trade['stars'],
                        trade['color'],
                        trade['attrs']
                    )
                else:
                    # Show empty cell if nothing changed
                    cell = f"{symbol.upper().replace('USDT', ''):<35}"

                row_outputs.append(cell)

        if updated:
            print(" | ".join(row_outputs))

async def main():
    tasks = [binance_trade_stream(f"{websocket_url_base}/{symbol}@aggTrade", symbol) for symbol in symbols]
    tasks.append(display_loop())
    await asyncio.gather(*tasks)

asyncio.run(main())
