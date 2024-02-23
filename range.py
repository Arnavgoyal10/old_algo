import pandas as pd
import numpy as np

# Function to calculate True Range (helper for ATR)
def true_range(df):
    high_low = df['inth'] - df['intl']
    high_close = np.abs(df['inth'] - df['intc'].shift())
    low_close = np.abs(df['intl'] - df['intc'].shift())
    return pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

# Calculate ATR based on the True Range
def atr(df, atr_length):
    return true_range(df).rolling(window=atr_length).mean()

# Main function to replicate Pine Script logic
def range_detector(df, length=20, mult=1.0, atr_length=500):
    # Calculate SMA and ATR
    df['sma'] = df['intc'].rolling(window=length).mean()
    df['atr'] = atr(df, atr_length) * mult
    
    # Initialize columns for the range detection
    df['range_top'] = np.nan
    df['range_bottom'] = np.nan
    df['is_shading'] = False
    
    for i in range(length, len(df)):
        current_close = df.loc[i, 'intc']
        for j in range(i-length+1, i+1):
            range_top = df.loc[j, 'sma'] + df.loc[j, 'atr']
            range_bottom = df.loc[j, 'sma'] - df.loc[j, 'atr']
            
            # Check if current close is within the last range, considering the entire period
            if range_bottom <= current_close <= range_top:
                df.loc[i, 'range_top'] = range_top
                df.loc[i, 'range_bottom'] = range_bottom
                df.loc[i, 'is_shading'] = True
                break  # Stop checking once a matching range is found
    
    # Drop unnecessary columns
    df.drop(['sma', 'atr'], axis=1, inplace=True)
    
    return df