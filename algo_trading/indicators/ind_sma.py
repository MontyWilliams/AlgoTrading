import pandas as pd
import time
from algo_trading.utilities.utils import get_candles, get_candles_hourly, setup, ask_bid

# timeframe = 15 # integer in minutes
# limit = 100
# sma = 20
# symbol = 'AR'

def ind_sma(symbol, timeframe, limit, sma_periods):
    """
    * Calculate Sma for a given symbol(s) and timeframe.
    - returns a dataframe
    """
    print(f'Running {timeframe} min, {sma_periods} day SMA strategy...')
    # Get the candle data
    candle_sticks = get_candles(symbol, timeframe, limit)
    if not candle_sticks:
        print("No candle data returned!")
        return pd.DataFrame()
    # Convert the candle data to a DataFrame
    df_sma = pd.DataFrame(candle_sticks, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']) 
    df_sma['timestamp'] = pd.to_datetime(df_sma['timestamp'], unit='ms')

    # Calculate the SMA of periods
    for period in sma_periods:  
        df_sma[f'sma{period}_{timeframe}'] = df_sma['close'].rolling(period).mean()
    
    return df_sma

def ind_sma_hourly(symbol, timeframe, limit, sma):
    
    print(f'Running {timeframe} min, {sma} day SMA strategy...')

    candle_sticks = get_candles_hourly(symbol, timeframe, limit)
    if not candle_sticks:
        print("No candle data returned!")
        
        return pd.DataFrame()
    
    df_hourly = pd.DataFrame(candle_sticks)
    df_hourly['timestamp'] = pd.to_datetime(df_hourly['timestamp'], unit='ms')
    df_hourly.set_index('timestamp', inplace=True)   

    # Compute 20-day SMA
    df_hourly[f'sma{sma}'] = df_hourly['close'].rolling(480).mean()

    # Get latest bid price
    bid = ask_bid(symbol)[1]

    # Generate signals
    df_hourly['signal'] = None
    df_hourly.loc[df_hourly[f'sma{sma}'] > bid, 'signal'] = 'sell'
    df_hourly.loc[df_hourly[f'sma{sma}'] < bid, 'signal'] = 'buy'

    # Support & resistance from previous day
    df_hourly['support'] = df_hourly['close'].shift(1).rolling(1).min()
    df_hourly['resis'] = df_hourly['close'].shift(1).rolling(1).max()

    return df_hourly

def ind_sma_daily(symbol, timeframe, limit, sma):
    limit = 1920  # need 96 15m candles to get 1 day candle so 1920 is the least in total
    print(f'Aggregating {timeframe}m candles into daily candles and Running daily SMA strategy...')

    candle_sticks = get_candles(symbol, timeframe, limit)
    df = pd.DataFrame(candle_sticks)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    # Resample to daily candles
    df_daily = df.resample('1D').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()

    # Compute 20-day SMA
    df_daily[f'sma{sma}'] = df_daily['close'].rolling(sma).mean()

    # Get latest bid price
    bid = ask_bid(symbol)[1]

    # Generate signals
    df_daily['signal'] = None
    df_daily.loc[df_daily[f'sma{sma}'] > bid, 'signal'] = 'sell'
    df_daily.loc[df_daily[f'sma{sma}'] < bid, 'signal'] = 'buy'

    # Support & resistance from previous day
    df_daily['support'] = df_daily['close'].shift(1).rolling(1).min()
    df_daily['resis'] = df_daily['close'].shift(1).rolling(1).max()

    return df_daily