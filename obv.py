import pandas as pd
import numpy as np

# Updated compute_slope function to take a single series as input
def compute_slope(series, length):
    # Calculation of the slope based on the least squares method
    x = np.arange(1, length + 1)
    y = series.values[-length:]  # Ensure we are taking the last 'length' values
    slope, intercept = np.polyfit(x, y, 1)
    return slope, intercept

# Updated DEMA calculation as per Pine Script logic
def dema(series, length):
    ema1 = series.ewm(span=length, adjust=False).mean()
    ema2 = ema1.ewm(span=length, adjust=False).mean()
    return 2 * ema1 - ema2

# Updated compute_obv_macd_indicator function
def compute_obv_macd_indicator(df, window_len=28, volume_len=14, obv_len=1, ma_len=9, slow_length=26):
    # Check if all required columns exist
    required_columns = ['intc', 'inth', 'intl', 'v']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"DataFrame must contain the following columns: {required_columns}")
    
    df[required_columns] = df[required_columns].apply(pd.to_numeric, errors='coerce')
    
    # Calculations as per Pine Script logic
    price_spread = df['inth'] - df['intl']
    price_spread_std = price_spread.rolling(window=window_len, min_periods=1).std(ddof=0)

    sign_change = np.sign(df['intc'].diff())
    v = (sign_change * df['v']).cumsum()
    smooth = v.rolling(window=volume_len, min_periods=1).mean()
    v_spread_std = (v - smooth).rolling(window=window_len, min_periods=1).std(ddof=0)
    shadow = (v - smooth) / v_spread_std * price_spread_std

    df['out'] = np.where(shadow > 0, df['inth'] + shadow, df['intl'] + shadow)
    df['obvema'] = df['out'].ewm(span=obv_len, adjust=False).mean()
    
    # Calculate the DEMA for the 'obvema' column
    ma = dema(df['obvema'], ma_len)
    slow_ma = df['intc'].ewm(span=slow_length, adjust=False).mean()
    df['macd'] = ma - slow_ma
    
    # Slope and intercept calculation
    df['slope'] = 0.0
    df['intercept'] = 0.0
    for i in range(ma_len - 1, len(df)):
        slope, intercept = compute_slope(df['macd'].iloc[i-ma_len+1:i+1], ma_len)
        df.at[i, 'slope'] = slope
        df.at[i, 'intercept'] = intercept
    
    df['tt1'] = df['intercept'] + df['slope'] * (ma_len + 1)

    # Color determination based on the slope
    df['color'] = df['macd'].diff().apply(lambda x: 'blue' if x > 0 else 'red')

    return df
