import pandas as pd
import numpy as np


def wma(weights):
    def calc(x):
        return np.sum(weights * x) / np.sum(weights)
    return calc

def calculate_hma(df, length):
    if 'intc' not in df.columns:
        raise ValueError("DataFrame must contain a 'intc' column.")
    
    half_length = int(length / 2)
    sqrt_length = int(np.floor(np.sqrt(length)))
    weights_half = np.arange(1, half_length + 1)
    weights_full = np.arange(1, length + 1)
    weights_sqrt = np.arange(1, sqrt_length + 1)
    
    wma_half = df['intc'].rolling(window=half_length).apply(wma(weights_half), raw=True)
    wma_full = df['intc'].rolling(window=length).apply(wma(weights_full), raw=True)
    
    df['hma'] = (2 * wma_half - wma_full).rolling(window=sqrt_length).apply(wma(weights_sqrt), raw=True)
    
    return df
