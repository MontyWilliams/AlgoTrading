import pandas as pd
from talib import RSI
import time
from utils import get_candles, setup, ask_bid

symbol = 'AR'
timeframe = '15'
limit = 100

def ind_rsi(symbol=symbol, timeframe=timeframe, limit=limit, rsi_period=24):
    """
    - Get candles for a given symbol, timeframe/limit
    - Returns RSI dataframe
    """
    print(f'Running {timeframe} timeframe RSI strategy...')

    # Fetch candlestick data
    candle_sticks = get_candles(symbol, timeframe, limit)
    df_rsi = pd.DataFrame(candle_sticks, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']) 
    df_rsi['timestamp'] = pd.to_datetime(df_rsi['timestamp'], unit='ms')

    # Calculate RSI
    delta = df_rsi['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=rsi_period, min_periods=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period, min_periods=rsi_period).mean()

    rs = avg_gain / avg_loss
    df_rsi['rsi'] = 100 - (100 / (1 + rs))

    # Generate signals based on RSI thresholds
    df_rsi.loc[df_rsi['rsi'] < 30, 'signal'] = 'buy'  # Oversold
    df_rsi.loc[df_rsi['rsi'] > 70, 'signal'] = 'sell'  # Overbought

    # Calculate support and resistance levels
    df_rsi['support'] = df_rsi['close'].rolling(window=limit).min()
    df_rsi['resis'] = df_rsi['close'].rolling(window=limit).max()

    print(df_rsi)
    
    df_rsi2 = pd.DataFrame(candle_sticks, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']) 
    df_rsi2['timestamp'] = pd.to_datetime(df_rsi['timestamp'], unit='ms')
    rsi2 = RSI(df_rsi['close'])
    df_rsi2['rsi'] = rsi2.rsi()
    
    print(df_rsi2)

    return df_rsi

def main():
    ind_rsi(symbol=symbol, timeframe=timeframe, limit=limit)
if __name__ == '__main__':
    main()