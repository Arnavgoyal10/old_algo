import pandas as pd


def calculate(df, lookback, ema_length):
    velocity_list = []
    for i in range(1, lookback + 1):
        velocity_i = (df['intc'] - df['intc'].shift(i)) / i
        velocity_list.append(velocity_i)
    df['velocity'] = pd.concat(velocity_list, axis=1).sum(axis=1) / lookback

    df['smooth_velocity'] = df['velocity'].ewm(span=ema_length, adjust=False).mean()

    return df