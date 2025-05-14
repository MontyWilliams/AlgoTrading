import pandas as pd
import time
from utils import get_candles, setup, ask_bid

timeframe = 15 # integer in minutes
limit = 100
sma = 20
symbol = 'AR'

def ind_sma(symbol=symbol, timeframe=timeframe, limit=limit, sma_period=sma):

    print(f'Running {timeframe} day SMA strategy...')

    candle_sticks = get_candles(symbol, timeframe, limit)
    df_sma = pd.DataFrame(candle_sticks, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']) 
    df_sma['timestamp'] = pd.to_datetime(df_sma['timestamp'], unit='ms')

    # Daily SMA 20
    df_sma[f'sma{sma_period}_{timeframe}'] = df_sma['close'].rolling(sma_period).mean()

     # if bid < the 20 day sma then = BEARISH, if bid > 20 day sma = BULLISH
    bid = ask_bid(symbol)[1]

    #if sma > bid = SELL, if sma < bid = BUY
    df_sma.loc[df_sma[f'sma{sma_period}_{timeframe}'] > bid, 'signal'] = 'sell'
    df_sma.loc[df_sma[f'sma{sma_period}_{timeframe}'] < bid, 'signal'] = 'buy'

    df_sma['support'] = df_sma[:-1]['close'].min()
    df_sma['resis'] = df_sma[:-1]['close'].max()

    print(df_sma)
    
    return df_sma 
def main():
    ind_sma(symbol=symbol, timeframe=timeframe, limit=limit, sma_period=sma)

if __name__ == '__main__':
    main()