import pandas as pd

def pivot(df):
    # Iterate over the rows from the bottom to the top
    for index in range(len(df)-1, -1, -1):
        current_time = df["time"].iloc[index]
        comparison_time = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
        
        if current_time == comparison_time:
            # Calculate pivot and support/resistance levels
            p = (df['inth'].iloc[index] + df['intl'].iloc[index] + df['intc'].iloc[index]) / 3
            s1 = p - 0.382 * (df['inth'].iloc[index] - df['intl'].iloc[index])
            s2 = p - 0.618 * (df['inth'].iloc[index] - df['intl'].iloc[index])
            s3 = p - 1 * (df['inth'].iloc[index] - df['intl'].iloc[index])
            s4 = p + 0.382 * (df['inth'].iloc[index] - df['intl'].iloc[index])
            s5 = p + 0.618 * (df['inth'].iloc[index] - df['intl'].iloc[index])
            s6 = p + 1 * (df['inth'].iloc[index] - df['intl'].iloc[index])
            level = [s1, s2, s3, s4, s5, s6]
            return level
        
        
def set_stoploss(df, market_direction, stoploss):
    temp = 0.0
    levels = pivot.pivot(df)
    if market_direction == 1:
        temp = (max([level for level in levels if level < df["intc"].iloc[-1]], default=stoploss))-8
        if (temp > stoploss or stoploss == 0):
            stoploss = temp
    else:
        temp = (min([level for level in levels if level > df["intc"].iloc[-1]], default=stoploss))+8
        if (temp < stoploss or stoploss == 0):
            stoploss = temp
    # print("Stoploss: ", stoploss)
    # print(df['time'].iloc[-1])
    return stoploss