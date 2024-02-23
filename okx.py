import pandas as pd
import numpy as np

def add_trading_signals(df):
    entryLength = 20
    exitLength = 10

    df['highest_high'] = df['inth'].rolling(window=entryLength).max()
    df['lowest_low'] = df['intl'].rolling(window=entryLength).min()
    df['buySignal'] = (df['inth'] == df['highest_high'].shift(1)) | (df['inth'] > df['highest_high'].shift(1))
    df['sellSignal'] = (df['intl'] == df['lowest_low'].shift(1)) | (df['intl'] < df['lowest_low'].shift(1))

    # For barssince calculations, use cumsum on condition changes
    df['buySignalChange'] = df['buySignal'].diff().ne(0).cumsum()
    df['sellSignalChange'] = df['sellSignal'].diff().ne(0).cumsum()
    df['entryBarssince1'] = df.groupby('buySignalChange').cumcount()
    df['entryBarssince2'] = df.groupby('sellSignalChange').cumcount()

    # Resetting the count on signal change
    df['exitBarssince1'] = np.where(df['buySignal'], df['entryBarssince1'], np.nan)
    df['exitBarssince2'] = np.where(df['sellSignal'], df['entryBarssince2'], np.nan)

    # Fill NaNs with forward fill method to simulate 'barssince' logic
    df['exitBarssince1'].ffill(inplace=True)
    df['exitBarssince2'].ffill(inplace=True)

    # Determine the Long Entry, Short Entry, or Nothing signals
    df['direction'] = 'Nothing'
    df.loc[df['buySignal'] & (df['exitBarssince1'] < df['entryBarssince1'].shift(1)), 'direction'] = 'Long Entry'
    df.loc[df['sellSignal'] & (df['exitBarssince2'] < df['entryBarssince2'].shift(1)), 'direction'] = 'Short Entry'

    # Dropping helper columns to clean up the DataFrame
    drop_columns = ['highest_high', 'lowest_low', 'buySignal', 'sellSignal',
                    'buySignalChange', 'sellSignalChange', 'entryBarssince1', 'entryBarssince2',
                    'exitBarssince1', 'exitBarssince2']
    df.drop(columns=drop_columns, inplace=True)

    return df

# Example usage:
# df = your_dataframe_with_high_low_close_columns
# df_with_signals = add_trading_signals(df)
