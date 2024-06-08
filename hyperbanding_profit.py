import os
import pandas as pd
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi
import refracted_advance as refracted
import csv
from hyperopt import hp, fmin, tpe, Trials
from hyperopt.pyll.base import scope
from datetime import datetime

def calculate_indicators(df, hyperparameters):
    (lookback_config, ema_length_config, conv_config, length_config, 
     lengthMA_config, lengthSignal_config, fast_config, slow_config, 
     signal_config) = hyperparameters

    df = df.copy()
    df = velocity_indicator.calculate_float(df, lookback=lookback_config, ema_length=ema_length_config)
    df = squeeze.squeeze_index2_float(df, conv=conv_config, length=length_config)
    
    df_macd = impulsemacd.macd(df, lengthMA=lengthMA_config, lengthSignal=lengthSignal_config)
    df[['ImpulseMACD', 'ImpulseMACDCDSignal']] = df_macd[['ImpulseMACD', 'ImpulseMACDCDSignal']]
    
    df_tsi = tsi.tsi(df, fast=fast_config, slow=slow_config, signal=signal_config)
    df[['TSI', 'TSIs']] = df_tsi[['TSI', 'TSIs']]
    
    return df

def append_value(dataframe, column_name, value, index):
    if index >= len(dataframe):
        new_row = pd.DataFrame([{col: (value if col == column_name else None) for col in dataframe.columns}])
        dataframe = pd.concat([dataframe, new_row], ignore_index=True)
    else:
        dataframe.at[index, column_name] = value
    return dataframe

def worker(params):    
    trade_columns = ['entry_time', 'entry_price', 'exit_time', 'exit_price', 'profit', 'agg_profit']
    trade_data = pd.DataFrame(columns=trade_columns)
    
    hyperparameters = [
        params['lookback'],
        params['ema_length'],
        params['conv'],
        params['length'],
        params['lengthMA'],
        params['lengthSignal'],
        params['fast'],
        params['slow'],
        params['signal']
    ]
    
    df = calculate_indicators(ret, hyperparameters)
    temp = df.iloc[:200].copy()
    df = df[200:]
    
    for j in range(0, len(df)):
        trade_data = refracted.final(temp, trade_data, [params['stoploss'], params['squee']])
        
        if len(trade_data) > 3 and (trade_data['profit'].tail(3) < 0).all():
            if trade_data['profit'].tail(3).sum() < -40:
                break
            
        next_row = df.iloc[[j]]
        temp = pd.concat([temp, next_row], ignore_index=True)
        temp = temp.iloc[-110:]
    
    net_profit = trade_data['profit'].sum()
    return -net_profit  # Hyperopt minimizes the objective function

def final(name):
    print(datetime.now())
    ohlc = ['into', 'inth', 'intl', 'intc']
    # file_path = 'excel_files/nifty_full_feb.xlsx'
    file_path = f'symbols/{name}.csv'
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    global ret
    # ret = pd.read_excel(file_path)
    ret = pd.read_csv(file_path)
    ret["time"] = pd.to_datetime(ret["time"], dayfirst=True)
    for col in ohlc:
        ret[col] = ret[col].astype(float)
        
    # space = {
    #     'stoploss': scope.int(hp.quniform('stoploss', 0, 15, 1)),
    #     'squee': scope.int(hp.quniform('squee', 1, 6, 1)),
    #     'lookback': scope.int(hp.quniform('lookback', 9, 19, 1)),
    #     'ema_length': scope.int(hp.quniform('ema_length', 14, 27, 1)),
    #     'conv': scope.int(hp.quniform('conv', 40, 66, 1)),
    #     'length': scope.int(hp.quniform('length', 8, 29, 1)),
    #     'lengthMA': scope.int(hp.quniform('lengthMA', 25, 40, 1)),
    #     'lengthSignal': scope.int(hp.quniform('lengthSignal', 6, 15, 1)),
    #     'fast': scope.int(hp.quniform('fast', 8, 18, 1)),
    #     'slow': scope.int(hp.quniform('slow', 18, 32, 1)),
    #     'signal': scope.int(hp.quniform('signal', 8, 19, 1))
    # }
    
    space = {
    'stoploss': hp.uniform('stoploss', 0, 50),
    'squee': hp.uniform('squee', 1, 6),
    'lookback': hp.uniform('lookback', 9, 19),
    'ema_length': hp.uniform('ema_length', 14, 27),
    'conv': hp.uniform('conv', 40, 66),
    'length': hp.uniform('length', 8, 29),
    'lengthMA': hp.uniform('lengthMA', 25, 40),
    'lengthSignal': hp.uniform('lengthSignal', 6, 15),
    'fast': hp.uniform('fast', 8, 18),
    'slow': hp.uniform('slow', 18, 32),
    'signal': hp.uniform('signal', 8, 19)
}
    
    trials = Trials()
    best = fmin(fn=worker, space=space, algo=tpe.suggest, max_evals=13800, trials=trials)
    
    print("Best hyperparameters found were: ", best)
    print(datetime.now())
    
    # Sort trials by loss and get top 10
    top_trials = sorted(trials.trials, key=lambda x: x['result']['loss'])[:5]
    
    top_results = []
    for trial in top_trials:
        result = trial['result']
        params = trial['misc']['vals']
        params = {k: v[0] for k, v in params.items()}  # Extract single values from lists
        params['net_profit'] = -result['loss']
        top_results.append(params)
    
    # Export to CSV
    columns = ["stoploss", "squee", "lookback", "ema_length", "conv", "length", "lengthMA", "lengthSignal", "fast", "slow", "signal", "net_profit"]
    with open(f"symbols_profit/{name}_profit.csv", "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        writer.writerows(top_results)
