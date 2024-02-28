import pandas as pd
import numpy as np

def compute_slope(series, length):
    # Calculation of the slope based on the least squares method
    x = np.arange(1, length + 1)
    y = series.values[-length:]  # Taking the last 'length' values
    slope, intercept = np.polyfit(x, y, 1)
    return slope

def dema(series, length):
    ema1 = series.ewm(span=length, adjust=False).mean()
    ema2 = ema1.ewm(span=length, adjust=False).mean()
    return 2 * ema1 - ema2

def compute_obv_macd_indicator(df, obv_ema_len=14, macd_fast_len=12, macd_slow_len=26, macd_signal_len=9, shadow_window=28):
    # Check for required columns
    df['intc'] = pd.to_numeric(df['intc'], errors='coerce')
    df['v'] = pd.to_numeric(df['v'], errors='coerce')   
    required_columns = ['into', 'inth', 'intl', 'intc', 'v']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"DataFrame must contain the following columns: {required_columns}")

    # OBV Calculation
    df['OBV'] = (np.sign(df['intc'].diff()) * df['v']).fillna(0).cumsum()
    # Adjusting OBV smoothing to use Simple Moving Average (SMA)
    df['OBV_SMA'] = df['OBV'].rolling(window=obv_ema_len).mean()


    # Price Spread Calculation
    price_spread = df['inth'] - df['intl']
    price_spread_std = price_spread.rolling(window=shadow_window, min_periods=1).std(ddof=0)

    # v Spread Calculation
    volume_spread = (df['OBV'] - df['OBV_SMA']).abs()
    volume_spread_std = volume_spread.rolling(window=shadow_window, min_periods=1).std(ddof=0)

    # Shadow Value Calculation
    df['Shadow'] = (df['OBV'] - df['OBV_SMA']) / volume_spread_std * price_spread_std

    # MACD Calculation
    fast_ema = df['intc'].ewm(span=macd_fast_len, adjust=False).mean()
    slow_ema = df['intc'].ewm(span=macd_slow_len, adjust=False).mean()
    df['MACD'] = fast_ema - slow_ema
    df['MACD_Signal'] = df['MACD'].ewm(span=macd_signal_len, adjust=False).mean()

    # Slope Calculation for T-Channel
    df['Slope'] = df['MACD'].rolling(window=macd_signal_len).apply(lambda x: compute_slope(x, macd_signal_len), raw=False)

    # Determining Line and Color
    df['Line'] = df['Shadow']  # This could be adjusted based on further specification
    df['Color'] = np.where(df['Shadow'] > 0, 'blue', 'red')

    return df
