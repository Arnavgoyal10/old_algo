import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def squeeze_index(df, conv=50, length=20, col='intc'):
    # Initialize max and min columns
    df['max'] = df[col]
    df['min'] = df[col]
    
    # Calculate max and min using the convergence factor
    for i in range(1, len(df)):
        df.loc[i, 'max'] = max(df.loc[i, col], df.loc[i-1, 'max'] - (df.loc[i-1, 'max'] - df.loc[i, col]) / conv)
        df.loc[i, 'min'] = min(df.loc[i, col], df.loc[i-1, 'min'] + (df.loc[i, col] - df.loc[i-1, 'min']) / conv)
    
    # Calculate the diff and apply the logarithm safely
    df['diff'] = df['max'] - df['min']
    df['diff'] = np.where(df['diff'] <= 0, np.nan, df['diff'])  # Avoid log of non-positive numbers
    df['log_diff'] = np.log(df['diff'])

    # Calculate the PSI using correlation over the specified length
    df['psi'] = np.nan
    for i in range(length-1, len(df)):
        if df['log_diff'].iloc[i-length+1:i+1].isnull().any():
            # If any log_diff is NaN, skip the calculation
            continue
        corr, _ = pearsonr(df['log_diff'].iloc[i-length+1:i+1], np.arange(length))
        df.loc[i, 'psi'] = -50 * corr + 50

    # Drop the helper columns
    df.drop(['max', 'min', 'diff', 'log_diff'], axis=1, inplace=True)
    
    # Return the DataFrame with the new PSI column
    return df

# Usage example:
# Assume 'df' is your DataFrame and it has a column named 'close'
# df = squeeze_index(df)
