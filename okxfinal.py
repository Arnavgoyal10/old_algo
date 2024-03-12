import pandas as pd
import numpy as np

def add_trading_signals(df):
    entryLength = 10
    exitLength = 10

    # Calculate highest and lowest values over specified windows
    df['upper'] = df['inth'].rolling(window=entryLength).max().shift(1)
    df['lower'] = df['intl'].rolling(window=entryLength).min().shift(1)
    df['up'] = df['inth'].rolling(window=entryLength).max()
    df['down'] = df['intl'].rolling(window=entryLength).min()
    df['sup'] = df['inth'].rolling(window=exitLength).max()
    df['sdown'] = df['intl'].rolling(window=exitLength).min()

    # Define crossover function
    def crossover(series1, series2):
        return (series1 > series2) & (series1.shift(1) <= series2.shift(1))

    # Define barssince function
    def barssince(series, condition=True):
        condition_met_indices = series[series == condition].index
        bars_since_list = np.zeros_like(series, dtype=int)
        prev_index = None
        for index in condition_met_indices:
            if prev_index is not None:
                bars_since_list[prev_index:index] = np.arange(1, index - prev_index + 1)
            prev_index = index
        if prev_index is not None:
            bars_since_list[prev_index:] = np.arange(1, len(series) - prev_index + 1)
        return bars_since_list

    # Calculate barssince for conditions
    df['barssince_up'] = barssince(df['inth'] >= df['up'].shift(1))
    df['barssince_down'] = barssince(df['intl'] <= df['down'].shift(1))

    # Determine entryLine and exitLine based on barssince logic
    df['entryLine'] = np.where(df['barssince_up'] <= df['barssince_down'], df['down'], df['up'])
    df['exitLine'] = np.where(df['barssince_up'] <= df['barssince_down'], df['sdown'], df['sup'])

    # Calculate buy and sell signals and exits
    df['buySignal'] = (df['inth'] == df['upper']) | crossover(df['inth'], df['upper'])
    df['sellSignal'] = (df['intl'] == df['lower']) | crossover(df['lower'], df['intl'])
    df['buyExit'] = (df['intl'] == df['sdown']) | crossover(df['sdown'], df['intl'])
    df['sellExit'] = (df['inth'] == df['sup']) | crossover(df['inth'], df['sup'])

    # Calculate barssince for buy and sell signals and exits
    df['entryBarssinceBuy'] = barssince(df['buySignal'], True)
    df['entryBarssinceSell'] = barssince(df['sellSignal'], True)
    df['exitBarssinceBuy'] = barssince(df['buyExit'], True)
    df['exitBarssinceSell'] = barssince(df['sellExit'], True)

    # ENTER_LONG and ENTER_SHORT signals
    df['ENTER_LONG'] = df['buySignal'] & (df['exitBarssinceBuy'] < df['entryBarssinceBuy'].shift(1))
    df['ENTER_SHORT'] = df['sellSignal'] & (df['exitBarssinceSell'] < df['entryBarssinceSell'].shift(1))
    
    df['direction'] = df.apply(lambda row: 'up' if row['ENTER_LONG'] and not row['ENTER_SHORT'] else
                                      'down' if row['ENTER_SHORT'] and not row['ENTER_LONG'] else
                                      'nothing',
                                      axis=1)

    drop_columns = ['upper', 'lower', 'up', 'down', 'sup', 'sdown', 
                    'barssince_up', 'barssince_down', 'entryLine', 'exitLine', 'buySignal', 'sellSignal', 'buyExit', 'sellExit', 'entryBarssinceBuy','entryBarssinceSell','exitBarssinceBuy', 'exitBarssinceSell' ]
    df.drop(columns=drop_columns, inplace=True)


    return df

# Example usage
# Assuming df is your DataFrame with 'high', 'low', 'close' columns
# df = replicate_pine_script_logic(df)
