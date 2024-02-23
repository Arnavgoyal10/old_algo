import pandas as pd
import numpy as np

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def calculate_rsi(series, period):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_t3(series, period):
    e1 = calculate_ema(series, period)
    e2 = calculate_ema(e1, period)
    e3 = calculate_ema(e2, period)
    e4 = calculate_ema(e3, period)
    e5 = calculate_ema(e4, period)
    e6 = calculate_ema(e5, period)
    b = 0.7
    c1 = -b**3
    c2 = 3*b**2 + 3*b**3
    c3 = -6*b**2 - 3*b - 3*b**3
    c4 = 1 + 3*b + b**3 + 3*b**2
    return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3

def determine_direction(current, prev, prev2):
    if current > prev and prev < prev2:
        return 'up'
    elif current < prev and prev > prev2:
        return 'down'
    else:
        return 'nothing'

def add_direction_column(df, short_l1=5, short_l2=20, short_l3=15, long_l1=20, long_l2=15):
    close = df['intc']

    # Calculating the Short Term Xtrender
    shortTermXtrender = calculate_rsi(calculate_ema(close, short_l1) - calculate_ema(close, short_l2), short_l3) - 50
    df['shortTermXtrender'] = shortTermXtrender

    # Calculating the T3 Moving Average of the Short Term Xtrender
    maShortTermXtrender = calculate_t3(shortTermXtrender, 5)
    df['maShortTermXtrender'] = maShortTermXtrender

    # Shifting the T3 Moving Average to compare with previous values
    df['maShortTermXtrender_1'] = df['maShortTermXtrender'].shift(1)
    df['maShortTermXtrender_2'] = df['maShortTermXtrender'].shift(2)

    # Applying the direction determination logic
    df['direction'] = df.apply(
        lambda row: determine_direction(
            row['maShortTermXtrender'],
            row['maShortTermXtrender_1'],
            row['maShortTermXtrender_2']
        ), axis=1
    )

    # Dropping intermediate columns
    df.drop(['shortTermXtrender', 'maShortTermXtrender', 'maShortTermXtrender_1', 'maShortTermXtrender_2'], axis=1, inplace=True)

    return df
