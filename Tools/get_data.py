import  os
import time
import requests
import pandas as pd
import json

symbol = 'AR'
timeframe = '15'
limit = 100
csv_output_path = f"{symbol}_{timeframe}m_data.csv"

def get_candles(symbol, timeframe, limit):
    """"
    - Get candles for a given symbol, timeframe/limit
    - Returns a df of candles
    """
    timeframe = int(timeframe)  # Convert to int incase it is a string
    end_time = int(time.time() * 1000)  # Current time in milliseconds
    interval_miliseconds = timeframe * 60 * 1000    # Convert timeframe to milliseconds
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
    if response.status_code == 200:
        candles = response.json()
        candle_sticks = []
        for candle in candles:
            open = float(candle["o"])
            close = float(candle["c"])
            high = float(candle["h"])
            low = float(candle["l"])
            timestamp = candle["t"]
            volume = float(candle["v"])
            candle_sticks.append({
                "timestamp": timestamp,
                "open": open,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume
            })
        
        candle_sticks_df = pd.DataFrame(candle_sticks, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        candle_sticks_df['timestamp'] = pd.to_datetime(candle_sticks_df['timestamp'], unit='ms')
        return candle_sticks_df
    else:
        print("Error: .....", response.status_code, response.text)
        return None

def save_to_csv(df, filename):
    """
    Save the DataFrame to a CSV file
    """
    df.to_csv(filename, index=False, mode='w', encoding='utf-8', lineterminator='\n')
    print(f"✅ CSV saved to: {filename}")

def main():
    df = get_candles(symbol, timeframe, limit)
    print(df.head())
    save_to_csv(df, csv_output_path)

if __name__ == "__main__":
    main()