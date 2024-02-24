import pandas as pd
import numpy as np

def calculate_ema(series, window, adjust=False):

    return series.ewm(span=window, adjust=adjust).mean()

def calculate_dema(series, window):
    ema1 = calculate_ema(series, window)
    ema2 = calculate_ema(ema1, window)
    return 2 * ema1 - ema2

def calculate_macd(df, fast_length, slow_length):
    fast_ema = calculate_ema(df['intc'], fast_length)
    slow_ema = calculate_ema(df['intc'], slow_length)
    df['macd'] = fast_ema - slow_ema
    return df

def calculate_macd_signal(df, signal_length):

    df['macd_signal'] = calculate_dema(df['macd'], signal_length)
    return df

def add_macd_to_df(df, fast_length=12, slow_length=26, signal_length=9):

    calculate_macd(df, fast_length, slow_length)
    calculate_macd_signal(df, signal_length)
    return df