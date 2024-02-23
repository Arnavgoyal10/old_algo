import pandas as pd
import numpy as np

# Assuming the DataFrame `df` has columns: 'open', 'high', 'low', 'close', 'volume'

# EMA calculation
def ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

# DEMA calculation
def dema(series, length):
    ema1 = ema(series, length)
    ema2 = ema(ema1, length)
    return 2 * ema1 - ema2

# Calculate the moving average based on the type
def calculate_ma(src, length, ma_type):
    if ma_type == "DEMA":
        return dema(src, length)
    else:
        return ema(src, length)  # Default to EMA if type not recognized

# Calcualte OBV
def calculate_obv(close, volume):
    direction = np.sign(close.diff())
    obv = (direction * volume).fillna(0).cumsum()
    return obv

# Function to calculate the slope
def calc_slope(y_values):
    x_values = np.arange(len(y_values))
    m, b = np.polyfit(x_values, y_values, 1)
    return m

# OBV MACD Indicator calculation
def obv_macd_indicator(df, ma_type="DEMA", fast_length=12, slow_length=26, signal_smoothing=9):
    df['obv'] = calculate_obv(df['close'], df['volume'])
    df['fast_ma'] = calculate_ma(df['obv'], fast_length, ma_type)
    df['slow_ma'] = calculate_ma(df['obv'], slow_length, ma_type)
    df['macd'] = df['fast_ma'] - df['slow_ma']
    df['signal'] = ema(df['macd'], signal_smoothing)
    df['histogram'] = df['macd'] - df['signal']
    df['slope'] = df['histogram'].rolling(window=signal_smoothing).apply(calc_slope, raw=True)
    return df