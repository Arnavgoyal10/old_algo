import os
import pandas as pd
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi
import refracted_advance as refracted
import csv
from bayes_opt import BayesianOptimization
from datetime import datetime
import threading

lock = threading.Lock()

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

def worker(params, ret):    
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
    temp = df.copy()
    
    for j in range(0, len(df)):
        with lock:
            trade_data = refracted.final(temp, trade_data, [params['stoploss'], params['squee']])
        
        next_row = df.iloc[[j]]
        temp = pd.concat([temp, next_row], ignore_index=True)
        temp = temp.tail(5)
    
    if len(trade_data) < 14:
        return 50000
    
    net_profit = trade_data['agg_profit'].sum()
    return -net_profit  # BayesianOptimization minimizes the objective function

def final(name):
    print(datetime.now())
    ohlc = ['into', 'inth', 'intl', 'intc']

    file_path = f'data_5min/{name}.csv'
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    ret = pd.read_csv(file_path)
    ret["time"] = pd.to_datetime(ret["time"], format="%Y-%m-%d %H:%M:%S", dayfirst=False)
    for col in ohlc:
        ret[col] = ret[col].astype(float)
        
    def optimize_function(stoploss, squee, lookback, ema_length, conv, length, lengthMA, lengthSignal, fast, slow, signal):
        params = {
            'stoploss': stoploss,
            'squee': squee,
            'lookback': lookback,
            'ema_length': ema_length,
            'conv': conv,
            'length': length,
            'lengthMA': lengthMA,
            'lengthSignal': lengthSignal,
            'fast': fast,
            'slow': slow,
            'signal': signal
        }
        result = worker(params, ret)
        print(f"Evaluated params: {params}, Result: {result}")
        return worker(params, ret)
    
    pbounds = {
        'stoploss': (0, 50),
        'squee': (0, 10),
        'lookback': (5, 30),
        'ema_length': (6, 35),
        'conv': (28, 75),
        'length': (2, 40),
        'lengthMA': (14, 52),
        'lengthSignal': (2, 28),
        'fast': (2, 27),
        'slow': (8, 42),
        'signal': (2, 30)
    }
    
    optimizer = BayesianOptimization(f=optimize_function, pbounds=pbounds, verbose=2, random_state=11)
    optimizer.maximize(init_points=1000, n_iter=3000)
    
    print("Best hyperparameters found were: ", optimizer.max)
    print(datetime.now())
    
    top_results = []
    for i, res in enumerate(optimizer.res):
        if i < 5:
            params = res['params']
            params['net_profit'] = -res['target']
            top_results.append(params)
    
    columns = ["stoploss", "squee", "lookback", "ema_length", "conv", "length", "lengthMA", "lengthSignal", "fast", "slow", "signal", "net_profit"]
    with open(f"min5_prof/{name}_agg.csv", "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        writer.writerows(top_results)

