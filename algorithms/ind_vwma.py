import pandas as pd
import talib as ta
import time
from utils import get_candles

symbol = 'AR'
timeframe = '15'
limit = 100

def get_df_vwma():
    bar = get_candles(symbol, timeframe, limit)
    df_vwma = pd.DataFrame(bar, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_vwma['timestamp'] = pd.to_datetime(df_vwma['timestamp'], unit='ms')

    return df_vwma

def ind_vwma():
    df_vwma = get_df_vwma()

    df_vwma['SMA(41);'] = df_vwma.close.rolling(41).mean()
    df_vwma['SMA(20)'] = df_vwma.close.rolling(20).mean()
    df_vwma['SMA(75)'] = df_vwma.close.rolling(75).mean()

    df_sma = df_vwma.fillna(0)

    # Get VWMA 

    vwmas = [20, 41, 75]

    df = get_df_vwma()

    # Calculate SMAs
    for sma in [20, 41, 75]:
        df[f'SMA({sma})'] = df['close'].rolling(sma).mean()

    # Precompute vol × close once
    df['volXclose'] = df['volume'] * df['close']

    for n in [20, 41, 75]:
        sum_vol = df['volume'].rolling(n).sum()
        sum_volXclose = df['volXclose'].rolling(n).sum()

        df[f'VWMA({n})'] = sum_volXclose / sum_vol

        # Generate crossover signals
        for sma in [20, 41, 75]:
            df.loc[df[f'VWMA({n})'] > df[f'SMA({sma})'], f'sig_{n}_gt_SMA({sma})'] = 'BUY'
            df.loc[df[f'VWMA({n})'] < df[f'SMA({sma})'], f'sig_{n}_lt_SMA({sma})'] = 'SELL'
    print(df_vwma)
    return df_vwma
def main():
    ind_vwma()
if __name__ == "__main__":
    main()