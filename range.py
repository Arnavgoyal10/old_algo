import pandas as pd
import numpy as np

# Assuming df is your dataframe and it has columns 'inth', 'intl', 'intc' for high, low, and close prices

# Function to calculate True Range (helper for ATR)
def true_range(df):
    high_low = df['inth'] - df['intl']
    high_close = np.abs(df['inth'] - df['intc'].shift())
    low_close = np.abs(df['intl'] - df['intc'].shift())
    true_ranges = pd.concat([high_low, high_close, low_close], axis=1)
    return true_ranges.max(axis=1)

# Calculate ATR based on the True Range
def atr(df, period):
    tr = true_range(df)
    return tr.rolling(window=period).mean()

# Enhanced range detector function to closely replicate Pine Script logic
def enhanced_range_detector(df, length=20, mult=1.0, atr_length=500):
    df['sma'] = df['intc'].rolling(window=length).mean()
    df['atr'] = atr(df, atr_length) * mult
    
    df['range_top'] = df['sma'] + df['atr']
    df['range_bottom'] = df['sma'] - df['atr']
    df['status'] = 'unbroken'  # Default status

    # Loop through the DataFrame to check range status
    for i in range(length, len(df)):
        # Initialize max and min for the range
        max_range = df.loc[i-length:i, 'range_top'].max()
        min_range = df.loc[i-length:i, 'range_bottom'].min()
        
        # Get the current close price
        current_close = df.loc[i, 'intc']

        # Determine if the current close is outside the range
        if current_close > max_range:
            df.loc[i-length+1:i+1, 'status'] = 'up'  # Set status to 'up' for the range period
        elif current_close < min_range:
            df.loc[i-length+1:i+1, 'status'] = 'down'  # Set status to 'down' for the range period
        else:
            # If close is within the range, check if previous status is not 'unbroken'
            # This is to ensure we only update the status if there was no prior breakout
            if df.loc[i-1, 'status'] == 'unbroken':
                df.loc[i, 'status'] = 'unbroken'
    
    # Keep only the necessary columns for output
    df.drop(['sma', 'atr'], axis=1, inplace=True)
    
    return df

# Sample usage:
# df = pd.read_csv('your_data.csv')
# df_enhanced = enhanced_range_detector(df)

# Make sure to test this code with your actual data and adjust as needed.
