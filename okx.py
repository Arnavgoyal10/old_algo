import pandas as pd
import numpy as np

def add_trading_signals(df):
    entryLength = 20

    df['highest_high'] = df['inth'].rolling(window=entryLength).max()
    df['lowest_low'] = df['intl'].rolling(window=entryLength).min()
    df['buySignal'] = (df['inth'] == df['highest_high'].shift(1)) | (df['inth'] > df['highest_high'].shift(1))
    df['sellSignal'] = (df['intl'] == df['lowest_low'].shift(1)) | (df['intl'] < df['lowest_low'].shift(1))

    df['buySignalChange'] = df['buySignal'].diff().ne(0).cumsum()
    df['sellSignalChange'] = df['sellSignal'].diff().ne(0).cumsum()
    df['entryBarssince1'] = df.groupby('buySignalChange').cumcount()
    df['entryBarssince2'] = df.groupby('sellSignalChange').cumcount()

    df['exitBarssince1'] = np.where(df['buySignal'], df['entryBarssince1'], np.nan)
    df['exitBarssince2'] = np.where(df['sellSignal'], df['entryBarssince2'], np.nan)

    df['exitBarssince1'].ffill(inplace=True)
    df['exitBarssince2'].ffill(inplace=True)

    df['direction'] = 'Nothing'
    df.loc[df['buySignal'] & (df['exitBarssince1'] < df['entryBarssince1'].shift(1)), 'direction'] = 'Long Entry'
    df.loc[df['sellSignal'] & (df['exitBarssince2'] < df['entryBarssince2'].shift(1)), 'direction'] = 'Short Entry'

    drop_columns = ['highest_high', 'lowest_low', 'buySignal', 'sellSignal',
                    'buySignalChange', 'sellSignalChange', 'entryBarssince1', 'entryBarssince2',
                    'exitBarssince1', 'exitBarssince2']
    df.drop(columns=drop_columns, inplace=True)

    return df