import datetime
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor
import strategy

ohlc = ['into', 'inth', 'intl', 'intc']

def append_value(dataframe, column_name, value, index):
    if index >= len(dataframe):
        new_row = pd.DataFrame([{col: (value if col == column_name else None) for col in dataframe.columns}])
        if not new_row.empty and not new_row.isna().all().all():
            new_row = new_row.dropna(axis=1, how='all')
            dataframe = pd.concat([dataframe, new_row], ignore_index=True)
    else:
        dataframe.at[index, column_name] = value
    return dataframe

def execute_strategy(params, ret, ohlc):
    stoploss, super_trend_period, super_trend_multiplier, squee, lookback, ema_length, conv, length, mult, atr_length, lengthMA, lengthSignal, fast, slow, signal, window_len, v_len, len10, slow_length = params
    
    temp = pd.DataFrame()
    temp = ret.iloc[:80].copy()
    data_columns = ['time', 'reason', 'bull or bear']
    trade_columns = ['entry_time', 'entry_price', 'exit_time', 'exit_price', 'profit']
    entry_frame_data = pd.DataFrame(columns=data_columns)
    trade_data = pd.DataFrame(columns=trade_columns)
    ret = ret[80:]
    hyperparameter = {
        'stoploss': stoploss,
        'super_trend_period': super_trend_period,
        'super_trend_multiplier': super_trend_multiplier,
        'squee': squee,
        'lookback': lookback,
        'ema_length': ema_length,
        'conv': conv,
        'length': length,
        'mult': mult,
        'atr_length': atr_length,
        'lengthMA': lengthMA,
        'lengthSignal': lengthSignal,
        'fast': fast,
        'slow': slow,
        'signal': signal,
        'window_len': window_len,
        'v_len': v_len,
        'len10': len10,
        'slow_length': slow_length,
    }

    for i in range(0, len(ret)):
        entry_frame_data, trade_data = strategy.final(temp, entry_frame_data, trade_data, hyperparameter)
        if i % 50 == 0:
            print("working fine")
            print(temp["time"].iloc[-1])
        next_row = ret.iloc[[i]]
        temp = pd.concat([temp, next_row], ignore_index=True)
    
    return trade_data['profit'].sum()

def main():
    file_path = 'Book1.xlsx'
    ret = pd.read_excel(file_path)
    ret["time"] = pd.to_datetime(ret["time"], dayfirst=True)
    for col in ohlc:
        ret[col] = ret[col].astype(float)
    
    # Prepare the parameters for each task
    tasks = [(stoploss, super_trend_period, super_trend_multiplier, squee, lookback, ema_length, conv, length, mult, atr_length, lengthMA, lengthSignal, fast, slow, signal, window_len, v_len, len10, slow_length)
             for stoploss in range(5, 21)
             for super_trend_period in range(8, 26)
             for super_trend_multiplier in [x * 0.1 for x in range(15, 38)]
             for squee in range(1, 5)
             for lookback in range(9, 19)
             for ema_length in range(14, 27)
             for conv in range(40, 66)
             for length in range(8, 29)
             for mult in [x * 0.1 for x in range(2, 16)]
             for atr_length in range(350, 551, 10)
             for lengthMA in range(25, 40)
             for lengthSignal in range(6, 15)
             for fast in range(8, 18)
             for slow in range(18, 32)
             for signal in range(8, 19)
             for window_len in range(25, 40)
             for v_len in range(8, 19)
             for len10 in [x * 0.1 for x in range(2, 16)]
             for slow_length in range(20, 33)]

    # Execute the tasks in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(lambda params: execute_strategy(params, ret.copy(), ohlc), tasks))
    
    # Initialize the net_profit DataFrame
    net_profit_columns = [
        'stoploss', 'super_trend_period', 'super_trend_multiplier', 'squee', 'lookback', 'ema_length', 'conv', 'length', 'mult', 'atr_length', 'lengthMA', 'lengthSignal', 'fast', 'slow', 'signal', 'window_len', 'v_len', 'len10', 'slow_length', 'net_profit'
    ]
    net_profit = pd.DataFrame(columns=net_profit_columns)
    
    # Update the net_profit DataFrame with the results
    hyperparameter_count = 0
    for i, (params, net_profit_1) in enumerate(zip(tasks, results)):
        hyperparameter_dict = dict(zip(net_profit_columns[:-1], params))
        hyperparameter_dict['net_profit'] = net_profit_1
        net_profit = net_profit.append(hyperparameter_dict, ignore_index=True)
        hyperparameter_count += 1
        print(f"Task {i + 1} done, net profit: {net_profit_1}")
    
    # Save the net_profit DataFrame to a CSV file
    current_directory = os.getcwd()
    df_comb_file = os.path.join(current_directory, 'netprofit.csv')
    net_profit.to_csv(df_comb_file, index=True)

if __name__ == "__main__":
    main()

