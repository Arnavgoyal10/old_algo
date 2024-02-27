import pandas as pd
import numpy as np

def calculate_atr(df, atr_length):
    '''Calculate the Average True Range (ATR)'''
    high_low = df['inth'] - df['intl']
    high_close = np.abs(df['inth'] - df['intc'].shift())
    low_close = np.abs(df['intl'] - df['intc'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(window=atr_length).mean()
    return atr

def in_range_detector(df, length=20, mult=1.0, atr_length=500):
    '''Add "in range" column to df indicating if price is within the calculated range'''
    # Ensure DataFrame has required columns

    df['ma'] = df['intc'].rolling(window=length).mean()
    df['atr'] = calculate_atr(df, atr_length) * mult

    # Initialize "in range" column with False
    df['in range'] = False
    
    for i in range(length, len(df)):
        close_prices = df['intc'][i-length+1:i+1]
        ma = df.at[i, 'ma']
        atr = df.at[i, 'atr']
        
        # Check if all close prices within the window are within the range
        if ((close_prices >= (ma - atr)) & (close_prices <= (ma + atr))).all():
            df.at[i, 'in range'] = True

    # Drop temporary columns (optional)
    df.drop(['ma', 'atr'], axis=1, inplace=True)
    
    return df

# Example usage
# Ensure your DataFrame 'df' includes 'high', 'low', and 'close' columns
# df = in_range_detector(df, length=20, mult=1.0, atr_length=500)



