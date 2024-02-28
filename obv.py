import pandas as pd
import numpy as np

def compute_slope(series, length):
    x = np.arange(1, length + 1)
    y = series.values[-length:]  # Taking the last 'length' values
    slope, intercept = np.polyfit(x, y, 1)
    return slope

def dema(series, length):
    ema1 = series.ewm(span=length, adjust=False).mean()
    ema2 = ema1.ewm(span=length, adjust=False).mean()
    return 2 * ema1 - ema2

# Main function to compute OBV MACD Indicator
def compute_obv_macd_indicator(df, obv_len=14, macd_fast_len=12, macd_slow_len=26, macd_signal_len=9, shadow_window=28):
    # Ensure the DataFrame has the necessary columns
    # df['intc'] = pd.to_numeric(df['intc'], errors='coerce')
    # df['v'] = pd.to_numeric(df['v'], errors='coerce')  
    # # Calculate Modified OBV
    # df['OBV_Modified'] = (np.sign(df['intc'].diff()) * df['v']).fillna(0).cumsum()
    # df['OBV_SMA'] = df['OBV_Modified'].rolling(window=obv_len).mean()
    
    # # Calculate Shadow
    # price_spread = df['inth'] - df['intl']
    # price_spread_std = price_spread.rolling(window=shadow_window).std(ddof=0)
    # volume_spread = (df['OBV_Modified'] - df['OBV_SMA']).abs()
    # volume_spread_std = volume_spread.rolling(window=shadow_window).std(ddof=0)
    # df['Shadow'] = (df['OBV_Modified'] - df['OBV_SMA']) / volume_spread_std * price_spread_std

    # MACD Calculation using DEMA
    df['MACD'] = dema(df['intc'], macd_fast_len) - dema(df['intc'], macd_slow_len)
    df['MACD_Signal'] = df['MACD'].ewm(span=macd_signal_len, adjust=False).mean()

    # Slope Calculation for MACD
    df['Slope'] = df['MACD'].rolling(window=macd_signal_len).apply(lambda x: compute_slope(x, macd_signal_len), raw=False)

    # Assign color based on Slope direction
    df['Color'] = np.where(df['Slope'] > 0, 'blue', 'red')
    df = df.drop("MACD_Signal", axis = 1)
    
    return df