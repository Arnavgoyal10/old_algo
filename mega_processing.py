import pandas as pd
import os
import multiprocessing
import strategy

ohlc=['into', 'inth', 'intl', 'intc']
     
file_path = 'nifty_full.xlsx'
ret_2 = pd.read_excel(file_path)
ret_2["time"] = pd.to_datetime(ret_2["time"], dayfirst=True)
for col in ohlc:
    ret_2[col] = ret_2[col].astype(float) 

base_directory = os.getcwd()            
                                                                                
def append_value(dataframe, column_name, value, index):
    if index >= len(dataframe):
        new_row = pd.DataFrame([{col: (value if col == column_name else None) for col in dataframe.columns}])
        if not new_row.empty and not new_row.isna().all().all():
            new_row = new_row.dropna(axis=1, how='all')
            dataframe = pd.concat([dataframe, new_row], ignore_index=True)
    else:
        dataframe.at[index, column_name] = value
    return dataframe

def loop_function(super_1, super_2):
        
    net_profit_columns = [
    'stoploss',
    'super_trend_period',
    'super_trend_multiplier',
    'squee',
    'lookback',
    'ema_length',
    'conv',
    'length',
    'mult',
    'atr_length',
    'lengthMA',
    'lengthSignal',
    'fast',
    'slow',
    'signal',
    'window_len',
    'v_len',
    'len10',
    'slow_length',
    'net_profit'
]
    
    net_profit = pd.DataFrame(columns=net_profit_columns)
    hyperparameter_count = 0
    
    start_index = int((super_1 - 1.5) * 10)
    super_trend_multiplier = (start_index + 15)*0.1
    
    end_index = int((super_2 - 1.5) * 10)
    super_trend_period = (end_index + 15)* 0.1
    
    main_folder = "data"
    folder_name = f"multiplier_{super_trend_multiplier}"
    sub_folder_name = f"period_{super_trend_period}" 
    directory_path = os.path.join(base_directory, main_folder, folder_name, sub_folder_name)
    os.makedirs(directory_path, exist_ok=True) 

    for stoploss in range(5, 21):
        for squee in range(1, 5):
            for lookback in range(9, 19):
                for ema_length in range(14, 27):
                    for conv in range(40, 66):
                        for length in range(8, 29):
                            for mult in [x * 0.1 for x in range(2, 16)]:
                                for atr_length in range(350, 551, 10):
                                    for lengthMA in range(25, 40):
                                        for lengthSignal in range(6, 15):
                                            for fast in range(8, 18):
                                                for slow in range(18, 32):
                                                    for signal in range(8, 19):
                                                        for window_len in range(25, 40):
                                                            for v_len in range(8, 19):
                                                                for len10 in [x * 0.1 for x in range(2, 16)]:
                                                                    for slow_length in range(20, 33):
                                                                            
                                                                        ret = ret_2
                                                                        hyper_count = 0
                                                                        temp = pd.DataFrame()
                                                                        temp = ret.iloc[:100].copy()
                                                                        data_columns = ['time','reason', 'bull or bear']
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
                                                                            
                                                                            entry_frame_data, trade_data, order_count = strategy.final(temp, entry_frame_data, trade_data,hyperparameter)
                                                                                
                                                                            if (i%150 == 0):
                                                                                print("working fine")
                                                                                print(temp["time"].iloc[-1])
                                                                            
                                                                            if ((len(temp)) % 1000  == 0):
                                                                                if (hyper_count == order_count):
                                                                                    break
                                                                                else:
                                                                                    hyper_count = order_count
                                                                            
                                                                            next_row = ret.iloc[[i]]
                                                                            temp = pd.concat([temp, next_row], ignore_index=True)
                                                                        
                                                                        if order_count > 0:
                                                                            net_profit = append_value(net_profit, 'stoploss', stoploss, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'super_trend_period', super_trend_period, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'super_trend_multiplier', super_trend_multiplier, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'squee', squee, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'lookback', lookback, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'ema_length', ema_length, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'conv', conv, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'length', length, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'mult', mult, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'atr_length', atr_length, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'lengthMA', lengthMA, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'lengthSignal', lengthSignal, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'fast', fast, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'slow', slow, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'signal', signal, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'window_len', window_len, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'v_len', v_len, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'len10', len10, hyperparameter_count)
                                                                            net_profit = append_value(net_profit, 'slow_length', slow_length, hyperparameter_count)
                                                                            net_profit_1 = trade_data['profit'].sum()
                                                                            net_profit = append_value(net_profit, 'net_profit', net_profit_1, hyperparameter_count)
                                                                            hyperparameter_count = hyperparameter_count + 1
                                                                            print(f'"done for"{hyperparameter_count}')
                                                                            try:
                                                                                df_comb_file = os.path.join(directory_path, f'netprofit_{super_trend_multiplier}_{super_trend_period}.csv')
                                                                                net_profit.to_csv(df_comb_file, index=True)
                                                                            except Exception as e:
                                                                                print("Error saving file for multiplier:", super_trend_multiplier)
                                                                                print(e)
                                                                                  
def worker(start, end):
    print("Worker started for multipliers:", start, "to", end)
    loop_function(start, end)
    print("Worker finished for multipliers:", start, "to", end)                          
                                 
def main():
    
    
    multiplier_ranges = []
    for i in range(15, 38):
        x = i / 10
        for y in range(8, 26):
            multiplier_ranges.append((x, y))
        
    print("Total number of multipliers to process:", len(multiplier_ranges))


    processes = []

    for r in multiplier_ranges:
        try:
            process = multiprocessing.Process(target=worker, args=(r[0], r[1]))
            processes.append(process)
            process.start()
        except Exception as e:
            print("Error starting process for multipliers:", r[0], "to", r[1])
            print(e)

    for process in processes:
        process.join()

    print("All processes have completed their execution.")
                                                                                                                                                                                               


if __name__ == "__main__":
    main()    
