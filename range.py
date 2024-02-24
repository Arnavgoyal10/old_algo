import pandas as pd
import numpy as np

def true_range(df):
    high_low = df['inth'] - df['intl']
    high_close = np.abs(df['inth'] - df['intc'].shift())
    low_close = np.abs(df['intl'] - df['intc'].shift())
    true_ranges = pd.concat([high_low, high_close, low_close], axis=1)
    return true_ranges.max(axis=1)

def atr(df, period):
    tr = true_range(df)
    return tr.rolling(window=period).mean()

def enhanced_range_detector(df, length=20, mult=1.0, atr_length=500):
    df['sma'] = df['intc'].rolling(window=length).mean()
    df['atr'] = atr(df, atr_length) * mult
    
    df['range_top'] = df['sma'] + df['atr']
    df['range_bottom'] = df['sma'] - df['atr']
    df['status'] = 'unbroken'  # Default status

    for i in range(length, len(df)):
        max_range = df.loc[i-length:i, 'range_top'].max()
        min_range = df.loc[i-length:i, 'range_bottom'].min()
    
        current_close = df.loc[i, 'intc']

        if current_close > max_range:
            df.loc[i-length+1:i+1, 'status'] = 'up' 
        elif current_close < min_range:
            df.loc[i-length+1:i+1, 'status'] = 'down'  
        else:
            if df.loc[i-1, 'status'] == 'unbroken':
                df.loc[i, 'status'] = 'unbroken'
    
    df.drop(['sma', 'atr'], axis=1, inplace=True)
    
    return df