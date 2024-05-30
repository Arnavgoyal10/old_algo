import pandas as pd
import numpy as np
from scipy.stats import pearsonr


def squeeze_index(df, conv, length, col='intc'):
    df['max'] = df[col]
    df['min'] = df[col]

    for i in df.index[1:]:
        df.loc[i, 'max'] = max(df.loc[i, col], df.loc[i-1, 'max'] - (df.loc[i-1, 'max'] - df.loc[i, col]) / conv)
        df.loc[i, 'min'] = min(df.loc[i, col], df.loc[i-1, 'min'] + (df.loc[i, col] - df.loc[i-1, 'min']) / conv)
    
    df['diff'] = df['max'] - df['min']
    df['diff'] = np.where(df['diff'] <= 0, np.nan, df['diff']) 
    df['log_diff'] = np.log(df['diff'])

    df['psi'] = np.nan
    for i in range(length-1, len(df)):
        if df['log_diff'].iloc[i-length+1:i+1].isnull().any():
            continue
        corr, _ = pearsonr(df['log_diff'].iloc[i-length+1:i+1], np.arange(length))
        df.loc[i, 'psi'] = -50 * corr + 50

    df.drop(['max', 'min', 'diff', 'log_diff'], axis=1, inplace=True)
    
    return df
