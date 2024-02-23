import pandas as pd
import numpy as np

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period):
    delta = series.diff()
    up, down = delta.clip(lower=0), -delta.clip(upper=0)
    ma_up = ema(up, period)
    ma_down = ema(down, period)
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))

def t3(src, length):
    e1 = ema(src, length)
    e2 = ema(e1, length)
    e3 = ema(e2, length)
    e4 = ema(e3, length)
    e5 = ema(e4, length)
    e6 = ema(e5, length)
    b = 0.7
    c1 = -b**3
    c2 = 3*b**2 + 3*b**3
    c3 = -6*b**2 - 3*b - 3*b**3
    c4 = 1 + 3*b + b**3 + 3*b**2
    return c1*e6 + c2*e5 + c3*e4 + c4*e3

def determine_direction(df, short_l1=5, short_l2=20, short_l3=15, long_l1=20, long_l2=15):
    # Assuming 'close' is the column with close prices
    close_col = 'intc'  # Change this to the actual column name of close prices in your dataframe
    
    # Calculate Xtrender values
    df['shortTermXtrender'] = rsi(ema(df[close_col], short_l1) - ema(df[close_col], short_l2), short_l3) - 50
    df['longTermXtrender'] = rsi(ema(df[close_col], long_l1), long_l2) - 50

    # Calculate T3 moving averages
    df['maShortTermXtrender'] = t3(df['shortTermXtrender'], 5)

    # Determine the circles for plotting
    df['plotshape_up'] = (df['maShortTermXtrender'] > df['maShortTermXtrender'].shift(1)) & (df['maShortTermXtrender'].shift(1) < df['maShortTermXtrender'].shift(2))
    df['plotshape_down'] = (df['maShortTermXtrender'] < df['maShortTermXtrender'].shift(1)) & (df['maShortTermXtrender'].shift(1) > df['maShortTermXtrender'].shift(2))

    # Filter out the 'nothing' directions and set 'up' or 'down' accordingly
    df['direction'] = np.where(df['plotshape_up'], 'up', np.where(df['plotshape_down'], 'down', 'nothing'))

    return df