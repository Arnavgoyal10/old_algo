import pandas as pd
import numpy as np

def compute_slope(series, length):
    # Calculation of the slope based on the least squares method
    x = np.arange(1, length + 1)
    y = series.tail(length).values
    slope, intercept = np.polyfit(x, y, 1)
    return slope * (length + 1) + intercept

def calculate_ma(series, length, ma_type='DEMA'):
    # Calculate the specified moving average
    if ma_type == 'DEMA':
        ema1 = series.ewm(span=length, adjust=False).mean()
        ema2 = ema1.ewm(span=length, adjust=False).mean()
        return 2 * ema1 - ema2
    else:
        raise NotImplementedError(f"MA type '{ma_type}' is not implemented")

def compute_obv_macd_indicator(df, window_len=28, volume_len=14, obv_len=1, ma_type='DEMA', ma_len=9, slow_length=26):
    # Check if all required columns exist
    required_columns = ['close', 'high', 'low', 'volume']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"DataFrame must contain the following columns: {required_columns}")
    
    # Calculations as per Pine Script logic
    price_spread = df['high'] - df['low']
    price_spread_std = price_spread.rolling(window=window_len).std()

    sign_change = np.sign(df['close'].diff())
    v = (sign_change * df['volume']).cumsum()
    smooth = v.rolling(window=volume_len).mean()
    v_spread_std = (v - smooth).rolling(window=window_len).std()
    shadow = (v - smooth) / v_spread_std * price_spread_std

    df['out'] = np.where(shadow > 0, df['high'] + shadow, df['low'] + shadow)
    df['obvema'] = df['out'].ewm(span=obv_len, adjust=False).mean()
    ma = calculate_ma(df['obvema'], ma_len, ma_type)
    slow_ma = df['close'].ewm(span=slow_length, adjust=False).mean()
    df['macd'] = ma - slow_ma
    df['tt1'] = df['macd'].rolling(window=ma_len).apply(lambda x: calc_slope(x, ma_len))

    # Color determination based on the slope
    df['color'] = df['macd'].diff().apply(lambda x: 'blue' if x > 0 else 'red')

    # Pivot points detection (placeholder)
    # You will need to define the logic for pivot point detection based on the Pine Script
    # df['pivot'] = ...

    # Return the DataFrame with the new columns added
    return df

# Example usage:
# Assuming you have a DataFrame