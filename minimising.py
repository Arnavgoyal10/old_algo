from scipy.optimize import minimize
import os
import pandas as pd
import refracted_advance as refracted
import multiprocessing
import cProfile
import pstats
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi
import random


ohlc=['into', 'inth', 'intl', 'intc']
     
file_path = 'excel_files/nifty_full_feb.xlsx'
ret = pd.read_excel(file_path)
ret["time"] = pd.to_datetime(ret["time"], dayfirst=True)
for col in ohlc:
    ret[col] = ret[col].astype(float) 


base_directory = os.getcwd()  
data_directory = os.path.join(base_directory, "data_trial")


def calculate_indicators(df, hyperparamas):
    
    (lookback_config, ema_length_config, conv_config, 
    length_config, lengthMA_config, lengthSignal_config, fast_config, slow_config, 
    signal_config) = hyperparamas
    
    df = df.copy()
    
    df = velocity_indicator.calculate_float(df, lookback=lookback_config, ema_length=ema_length_config)
    df = squeeze.squeeze_index2_float(df,conv=conv_config, length=length_config)
    
    df_macd = impulsemacd.macd(df, lengthMA = lengthMA_config, lengthSignal = lengthSignal_config)
    df[['ImpulseMACD', 'ImpulseMACDCDSignal']] = df_macd[['ImpulseMACD', 'ImpulseMACDCDSignal']]
    
    df_tsi = tsi.tsi(df, fast = fast_config, slow = slow_config, signal = signal_config)
    df[['TSI', 'TSIs']] = df_tsi[['TSI', 'TSIs']]
    
    return df

def append_value(dataframe, column_name, value, index):
    if index >= len(dataframe):
        new_row = pd.DataFrame([{col: (value if col == column_name else None) for col in dataframe.columns}])
        dataframe = pd.concat([dataframe, new_row], ignore_index=True)
    else:
        dataframe.at[index, column_name] = value
    return dataframe

def start_worker(hyper_parameters, counter):
    
    print("Worker started ", counter)
    optimising(hyper_parameters, counter)
    print("Worker finished ", counter) 

def optimising(hyper_parameters, counter):
    
    bounds = [(max(0, x - 3), x + 3) for x in hyper_parameters]

    result = minimize(worker, hyper_parameters, method="Nelder-Mead", bounds=bounds, options={'disp': True, 'fatol': 1e-04, 'maxfev': 10000})

    optimized_parameters = result.x
    maximum_net_profit = -result.fun
    
    net_profit_columns = [
    'stoploss',
    'squee',
    'lookback',
    'ema_length',
    'conv',
    'length',
    'lengthMA',
    'lengthSignal',
    'fast',
    'slow',
    'signal',
    'net_profit'
]
        
    net_profit = pd.DataFrame(columns=net_profit_columns)
    net_profit = append_value(net_profit, 'stoploss', optimized_parameters[0], 0)
    net_profit = append_value(net_profit, 'squee', optimized_parameters[1], 0)
    net_profit = append_value(net_profit, 'lookback', optimized_parameters[2], 0)
    net_profit = append_value(net_profit, 'ema_length', optimized_parameters[3], 0)
    net_profit = append_value(net_profit, 'conv', optimized_parameters[4], 0)
    net_profit = append_value(net_profit, 'length', optimized_parameters[5], 0)
    net_profit = append_value(net_profit, 'lengthMA', optimized_parameters[6], 0)
    net_profit = append_value(net_profit, 'lengthSignal', optimized_parameters[7], 0)
    net_profit = append_value(net_profit, 'fast', optimized_parameters[8], 0)
    net_profit = append_value(net_profit, 'slow', optimized_parameters[9], 0)
    net_profit = append_value(net_profit, 'signal', optimized_parameters[10], 0)
    net_profit = append_value(net_profit, 'net_profit', maximum_net_profit, 0)
    
    df_comb_file = os.path.join(data_directory, f'netprofit_{counter}.csv')
    net_profit.to_csv(df_comb_file, index=True)
    
def worker(hyper_parameters):
    trade_columns = ['entry_time', 'entry_price', 'exit_time', 'exit_price', 'profit']
    trade_data = pd.DataFrame(columns=trade_columns)
    parse1 = hyper_parameters[2:]
    parse2 = hyper_parameters[:2]
    
    df = calculate_indicators(ret, parse1)
    temp = pd.DataFrame()
    temp = df.iloc[:200].copy()
    df = df[200:]
    
    for j in range(0, len(df)):
        trade_data = refracted.final(temp,trade_data, parse2)        
        
        # if (j%150 == 0):
        #     print(f'"working fine {j}"')
        #     print(temp["time"].iloc[-1])
        
        if len(trade_data) >= 3 and (trade_data['profit'].tail(3) < 0).all():
            if trade_data['profit'].tail(3).sum() < -40:
                break

        next_row = df.iloc[[j]]
        temp = pd.concat([temp, next_row], ignore_index=True)
        temp = temp.iloc[-110:]
    
    net_profit_1 = trade_data['profit'].sum()
    return -net_profit_1
    
def main():

        
    with cProfile.Profile() as pr:
                
        num_points = 208

        ranges = {
            "stoploss": (0, 10),
            "squee": (1, 5),
            "lookback": (9, 19),
            "ema_length": (14, 27),
            "conv": (40, 66),
            "length": (8, 29),
            "lengthMA": (25, 40),
            "lengthSignal": (6, 15),
            "fast": (8, 18),
            "slow": (18, 32),
            "signal": (8, 19)
        }

        hyperparameters_list = [
            [random.randint(start, end) for start, end in ranges.values()]
            for _ in range(num_points)
]
        
        processes = []
        
        for i, hyper_parameters in enumerate(hyperparameters_list):
            p = multiprocessing.Process(target=start_worker, args=(hyper_parameters, i))
            processes.append(p)
            p.start()
        
        for p in processes:
            p.join()
        
        print("All workers finished")
    
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats("profile_multi_trial.prof")
    
    

if __name__ == "__main__":
    main()