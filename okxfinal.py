import pandas as pd
import numpy as np


def add_trading_signals(df, entryLength, exitLength):

    # Calculate highest and lowest values over specified windows
    df['upper'] = df['inth'].rolling(window=entryLength).max()
    df['lower'] = df['intl'].rolling(window=entryLength).min()
    df['up'] = df['inth'].rolling(window=entryLength).max()
    df['down'] = df['intl'].rolling(window=entryLength).min()
    df['sup'] = df['inth'].rolling(window=exitLength).max()
    df['sdown'] = df['intl'].rolling(window=exitLength).min()

    # Define crossover function
    def crossover(series1, series2):
        return (series1 > series2) & (series1.shift(1) <= series2.shift(1))

    def barssince(series):
        true_indices = np.where(series, np.arange(len(series)), np.nan)
        last_true_indices = pd.Series(true_indices).ffill().values
        bars_since = np.arange(len(series)) - last_true_indices
        bars_since[np.isnan(last_true_indices)] = np.nan
        return bars_since

    # Calculate barssince for conditions
    df['barssince_up'] = barssince(df['inth'] >= df['up'].shift(1))
    df['barssince_down'] = barssince(df['intl'] <= df['down'].shift(1))

    # Calculate buy and sell signals and exits
    df['buySignal'] = (df['inth'] == df['upper'].shift(1)) | crossover(df['inth'], df['upper'].shift(1))
    df['sellSignal'] = (df['intl'] == df['lower'].shift(1)) | crossover(df['lower'].shift(1), df['intl'])
    df['buyExit'] = (df['intl'] == df['sdown'].shift(1)) | crossover(df['sdown'].shift(1), df['intl'])
    df['sellExit'] = (df['inth'] == df['sup'].shift(1)) | crossover(df['inth'], df['sup'].shift(1))

    # Calculate barssince for buy and sell signals and exits
    df['entryBarssinceBuy'] = barssince(df['buySignal'].shift(1))
    df['entryBarssinceSell'] = barssince(df['sellSignal'].shift(1))
    df['exitBarssinceBuy'] = barssince(df['buyExit'].shift(1))
    df['exitBarssinceSell'] = barssince(df['sellExit'].shift(1))

    
    # ENTER_LONG and ENTER_SHORT signals
    df['ENTER_LONG'] = df['buySignal'] & (df['exitBarssinceBuy'] < df['entryBarssinceBuy'].shift(1))
    df['ENTER_SHORT'] = df['sellSignal'] & (df['exitBarssinceSell'] < df['entryBarssinceSell'].shift(1))
    
    df['direction'] = df.apply(lambda row: 'up' if row['ENTER_LONG'] and not row['ENTER_SHORT'] else
                                      'down' if row['ENTER_SHORT'] and not row['ENTER_LONG'] else
                                      'nothing',
                                      axis=1)

    drop_columns = ['upper', 'lower', 'up', 'down', 'sup', 'sdown', 
                    'barssince_up', 'barssince_down', 'buySignal', 'sellSignal', 'buyExit', 'sellExit', 'entryBarssinceBuy','entryBarssinceSell','exitBarssinceBuy', 'exitBarssinceSell' ]
    df.drop(columns=drop_columns, inplace=True)


    return df