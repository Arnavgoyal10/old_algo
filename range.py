# import numpy as np
# import pandas as pd

# def calculate_atr(df, atr_length):
#     high_low = df['inth'] - df['intl']
#     high_close = np.abs(df['inth'] - df['intc'].shift())
#     low_close = np.abs(df['intl'] - df['intc'].shift())
#     true_ranges = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
#     atr = true_ranges.rolling(window=atr_length).mean()
#     return atr

# def detect_ranges(df, length, mult, atr_length):
#     df['MA'] = df['intc'].rolling(window=length).mean()
#     df['ATR'] = calculate_atr(df, atr_length) * mult
    
#     # Initialize columns to track range status and adjustments
#     df['RangeTop'] = np.nan
#     df['RangeBottom'] = np.nan
#     df['InRange'] = False
#     df['StartNewRange'] = False

#     for i in range(length, len(df)):
#         ma = df.loc[df.index[i], 'MA']
#         atr = df.loc[df.index[i], 'ATR']
#         upper_bound = ma + atr
#         lower_bound = ma - atr

#         # Logic to determine if a new range should start or if we should continue the previous range
#         if i == length or df.loc[df.index[i-1], 'StartNewRange']:
#             df.loc[df.index[i], 'StartNewRange'] = True
#             df.loc[df.index[i], 'RangeTop'] = upper_bound
#             df.loc[df.index[i], 'RangeBottom'] = lower_bound
#         else:
#             # Continue with previous range's bounds if within the range
#             prev_upper_bound = df.loc[df.index[i-1], 'RangeTop']
#             prev_lower_bound = df.loc[df.index[i-1], 'RangeBottom']
#             df.loc[df.index[i], 'RangeTop'] = prev_upper_bound
#             df.loc[df.index[i], 'RangeBottom'] = prev_lower_bound

#             # Start a new range if current price breaks out of the previous range
#             if df['intc'].iloc[i] > prev_upper_bound or df['intc'].iloc[i] < prev_lower_bound:
#                 df.loc[df.index[i], 'StartNewRange'] = True
#                 df.loc[df.index[i], 'RangeTop'] = upper_bound
#                 df.loc[df.index[i], 'RangeBottom'] = lower_bound
#             else:
#                 df.loc[df.index[i], 'StartNewRange'] = False

#         # Determine if current price is within the range
#         df.loc[df.index[i], 'InRange'] = df['intc'].iloc[i] <= upper_bound and df['intc'].iloc[i] >= lower_bound

#     # Cleanup: Remove the helper column if not needed for further analysis
#     df.drop(columns=['StartNewRange'], inplace=True)

#     return df







import pandas as pd
import numpy as np

def calculate_atr(df, atr_length):
    '''Calculate the Average True Range (ATR)'''
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(window=atr_length).mean()
    return atr

def in_range_detector(df, length=20, mult=1.0, atr_length=500):
    '''Add "in range" column to df indicating if price is within the calculated range'''
    # Ensure DataFrame has required columns
    if not {'close', 'high', 'low'}.issubset(df.columns):
        raise ValueError("DataFrame must include 'close', 'high', and 'low' columns")

    df['ma'] = df['close'].rolling(window=length).mean()
    df['atr'] = calculate_atr(df, atr_length) * mult

    # Initialize "in range" column with False
    df['in range'] = False
    
    for i in range(length, len(df)):
        close_prices = df['close'][i-length+1:i+1]
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



