import pandas as pd

def calculate(df, lookback=14, ema_length=20):
    if 'intc' not in df.columns:
        raise ValueError("DataFrame must contain a 'intc' column")
    
    # Calculate Velocity
    df['velocity'] = 0.0
    for i in range(1, lookback + 1):
        df['velocity'] += (df['intc'] - df['intc'].shift(i)) / i
    df['velocity'] /= lookback
    
    # Calculate Acceleration
    df['acceleration'] = 0.0
    for i in range(1, lookback + 1):
        df['acceleration'] += (df['velocity'] - df['velocity'].shift(i)) / i
    df['acceleration'] /= lookback
    
    # Calculate Smoothed Velocity using EMA
    df['smoothed_velocity'] = df['velocity'].ewm(span=ema_length, adjust=False).mean()
    
    return df
