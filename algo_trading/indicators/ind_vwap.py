import pandas as pd
# from talib import RSI
import time
from utils import get_candles

symbol = 'AR'
timeframe = '15'
limit = 100

def get_df_vwap():
    """"
    Get candlestick for vwap
    """
    bars = get_candles(symbol, timeframe, limit)
    df_vwap = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_vwap['timestamp'] = pd.to_datetime(df_vwap['timestamp'], unit='ms')

    lo = df_vwap['low'].min()
    hi = df_vwap['high'].max()
    l2h = hi - lo
    avg = (hi + lo) / 2

    return df_vwap

def ind_vwap():
    print('starting the vwma indicatior to see if it is bullish or bearish')

    df_vwap = get_df_vwap()

    # VWAP = ( sum [first 13 values]) / (sumb [volume top 13 ])
    df_vwap['volXclose'] = df_vwap['close'] * df_vwap['volume']

    # Get cummulative sum of volume
    df_vwap['cum_vol'] = df_vwap['volume'].cumsum()

    # Get cummulative sum of vol * price hi + low + close / 3 gets average
    df_vwap['cumvolXclose'] = (df_vwap['volume'] * (df_vwap['high'] + df_vwap['low'] + df_vwap['close']) / 3).cumsum()

    # Get VWAP
    df_vwap['VWAP'] = df_vwap['cumvolXclose'] / df_vwap['cum_vol']
    df_vwap = df_vwap.fillna(0)

    # VWAP equation = sum(volume * avg price) / sum(volume)

    print(df_vwap)

    return df_vwap

def main():
    ind_vwap()
if __name__ == "__main__":
    main()