import numpy as np
import pandas as pd

def calculate_wma(data, period):
    weights = np.arange(1, period + 1)[::-1]
    wma = np.full(data.shape[0], np.nan)  # Create an array of nans
    for i in range(period - 1, data.shape[0]):
        wma[i] = np.dot(data[i - period + 1:i + 1], weights) / weights.sum()
    return wma

def calculate_hma(df, column_name="intc", length=60):
    half_length = int(length / 2)
    sqrt_length = int(np.sqrt(length))

    # Calculate WMA for half length and full length
    half_wma = calculate_wma(df[column_name].values, half_length)
    full_wma = calculate_wma(df[column_name].values, length)

    # Calculate the raw HMA with half_length WMA and full_length WMA
    raw_hma = 2 * half_wma - full_wma

    # Calculate the final HMA using the square root of the length for WMA
    hma = calculate_wma(raw_hma, sqrt_length)
    df['HMA'] = hma

    return df

# Example usage:
# df = calculate_hma(df, "intc", 9)
