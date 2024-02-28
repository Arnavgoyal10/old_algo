import pandas as pd
import numpy as np

def compute_slope(series, length):
    x = np.arange(1, length + 1)
    y = series.values[-length:]
    slope, intercept = np.polyfit(x, y, 1)
    return slope

def dema(series, length):
    ema1 = series.ewm(span=length, adjust=False).mean()
    ema2 = ema1.ewm(span=length, adjust=False).mean()
    return 2 * ema1 - ema2

def compute_obv_macd_indicator(df, macd_fast_len=12, macd_slow_len=26, macd_signal_len=9):
    df['MACD'] = dema(df['intc'], macd_fast_len) - dema(df['intc'], macd_slow_len)
    df['MACD_Signal'] = df['MACD'].ewm(span=macd_signal_len, adjust=False).mean()

    df['Slope'] = df['MACD'].rolling(window=macd_signal_len).apply(lambda x: compute_slope(x, macd_signal_len), raw=False)

    df['Color'] = np.where(df['Slope'] > 0, 'blue', 'red')
    df = df.drop("MACD_Signal", axis = 1)
    return df