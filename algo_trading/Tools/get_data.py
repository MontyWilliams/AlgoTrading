import  os
import time
import requests
import pandas as pd
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent  # or adjust as needed
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

symbol = 'AR'
timeframe = '15'
limit = 672  # 672 = 7 days of 15m candles
csv_output_path = DATA_DIR / f"{symbol}_{timeframe}m_data.csv"

def get_candles(symbol, timeframe, limit):
    """"
    - Get candles for a given symbol, timeframe/limit
    - Returns a df of candles
    """
    timeframe = int(timeframe)  # Convert to int in case it's a string
    interval_miliseconds = timeframe * 60 * 1000    # Convert timeframe to milliseconds
    end_time = int(time.time() * 1000)  # Current time in milliseconds
    start_time = end_time - (limit * interval_miliseconds)  # Calculate start time
    url = "https://api.hyperliquid.xyz/info"
    headers = {"Content-Type": "application/json"}
    data = {
        "type": "candleSnapshot",
        "req": {
            "coin": symbol,
            "interval": f"{timeframe}m",  # Format interval as a string with 'm' of api will refuse
            "startTime": start_time,
            "endTime": end_time,
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None
    
    candles = response.json()
    
    if not candles or not isinstance(candles, list):
        print("❌ No candle data returned.")
        return None
    
    candle_sticks = []
    for candle in candles:
        candle_sticks.append({
            "timestamp": pd.to_datetime(candle["t"], unit='ms'),
            "open": float(candle["o"]),
            "high": float(candle["h"]),
            "low": float(candle["l"]),
            "close": float(candle["c"]),
            "volume": float(candle["v"])
        })
    df = pd.DataFrame(candle_sticks)
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')  # Format to include seconds
    return df
    
def save_to_csv(df, filename):
    """
    Save the DataFrame to a CSV file
    """
    df.to_csv(filename, index=False, mode='w', encoding='utf-8', lineterminator='\n')
    print(f"✅ CSV saved to: {filename}")

def main():
    df = get_candles(symbol, timeframe, limit)
    print("📅 Current local time:", pd.Timestamp.now())
    print(df.tail())
    save_to_csv(df, csv_output_path)

if __name__ == "__main__":
    main()