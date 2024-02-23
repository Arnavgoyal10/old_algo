import pandas as pd
import numpy as np

def find_pivots(df, lb, rb, ohlc=['open', 'high', 'low', 'close']):
    df['pivot_high'] = df[ohlc[1]].rolling(window=lb+rb+1, center=True).max() == df[ohlc[1]]
    df['pivot_low'] = df[ohlc[2]].rolling(window=lb+rb+1, center=True).min() == df[ohlc[2]]
    return df

def hhll(df, left, right, ohlc=['open', 'high', 'low', 'close']):
    
    df = find_pivots(df,5,5, ohlc)
    lb = left
    rb = right
    df['direction'] = False
    prev_pivot_high = None
    prev_pivot_low = None
    for i in range(lb + rb, len(df)):
        current_high = df.iloc[i][ohlc[1]]
        current_low = df.iloc[i][ohlc[2]]
        if df.iloc[i]['pivot_high'] and prev_pivot_high is not None and current_high > prev_pivot_high:
            df.at[i, 'direction'] = 'down'
            prev_pivot_high = current_high
        elif df.iloc[i]['pivot_low'] and prev_pivot_low is not None and current_low < prev_pivot_low:
            df.at[i, 'direction'] = 'up'
            prev_pivot_low = current_low
        else:
            if df.iloc[i]['pivot_high']:
                prev_pivot_high = current_high
            if df.iloc[i]['pivot_low']:
                prev_pivot_low = current_low

    return df
