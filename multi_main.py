import os
import pandas as pd
import refracted
import multiprocessing
import itertools


ohlc=['into', 'inth', 'intl', 'intc']
     

base_directory = os.getcwd()
data_directory = os.path.join(base_directory, "data")

hyperparameters = [
    [7, 10, 12],
    [2, 4, 6],
    [10, 14, 16],
    [16, 20, 24],
    [44, 50, 56],
    [16, 20, 24],
    [30, 34, 38],
    [7, 9, 11],
    [10, 13, 16],
    [20, 25, 30],
    [10, 13, 16]
]
 
def append_value(dataframe, column_name, value, index):
    if index >= len(dataframe):
        new_row = pd.DataFrame([{col: (value if col == column_name else None) for col in dataframe.columns}])
        if not new_row.empty and not new_row.isna().all().all():
            new_row = new_row.dropna(axis=1, how='all')
            dataframe = pd.concat([dataframe, new_row], ignore_index=True)
    else:
        dataframe.at[index, column_name] = value
    return dataframe

def working(ret, hyper_parameters, counter):
    
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
    
    for i in range(0, len(hyper_parameters)):
        
        trade_columns = ['entry_time', 'entry_price', 'exit_time', 'exit_price', 'profit']
        trade_data = pd.DataFrame(columns=trade_columns)
        temp = pd.DataFrame()
        temp = ret.iloc[:200].copy()
        df = ret[200:]
        
        for j in range(0, len(df)):
            trade_data = refracted.final(temp,trade_data, hyper_parameters[i])        
            
            if (j%150 == 0):
                print(f'"working fine {j}"')
                print(temp["time"].iloc[-1])
            
            next_row = df.iloc[[j]]
            temp = pd.concat([temp, next_row], ignore_index=True)
            temp = temp.iloc[-110:].reset_index(drop=True)
        
        net_profit = append_value(net_profit, 'stoploss', hyper_parameters[i][0], i)
        net_profit = append_value(net_profit, 'squee', hyper_parameters[i][1], i)
        net_profit = append_value(net_profit, 'lookback', hyper_parameters[i][2], i)
        net_profit = append_value(net_profit, 'ema_length', hyper_parameters[i][3], i)
        net_profit = append_value(net_profit, 'conv', hyper_parameters[i][4], i)
        net_profit = append_value(net_profit, 'length', hyper_parameters[i][5], i)
        net_profit = append_value(net_profit, 'lengthMA', hyper_parameters[i][6], i)
        net_profit = append_value(net_profit, 'lengthSignal', hyper_parameters[i][7], i)
        net_profit = append_value(net_profit, 'fast', hyper_parameters[i][8], i)
        net_profit = append_value(net_profit, 'slow', hyper_parameters[i][9], i)
        net_profit = append_value(net_profit, 'signal', hyper_parameters[i][10], i)
        net_profit_1 = trade_data['profit'].sum()
        net_profit = append_value(net_profit, 'net_profit', net_profit_1, i)
    
    df_comb_file = os.path.join(data_directory, f'netprofit_{counter}.csv')
    net_profit.to_csv(df_comb_file, index=True)
             
def worker(ret, hyper_parameters, counter):
    
    print("Worker started ", counter)
    working(ret, hyper_parameters, counter)
    print("Worker finished ", counter) 
    

def main():
    print("starting")
    file_path = 'nifty_full_feb.xlsx'
    ret = pd.read_excel(file_path)
    ret["time"] = pd.to_datetime(ret["time"], dayfirst=True)
    for col in ohlc:
        ret[col] = ret[col].astype(float) 
    

    all_combinations = list(itertools.product(*hyperparameters))

    total_combinations = len(all_combinations)

    num_lists = 50
    size_of_each_list = total_combinations // num_lists
    remainder = total_combinations % num_lists

    separate_lists = []
    
    for i in range(num_lists):
        start_index = i * size_of_each_list
        end_index = start_index + size_of_each_list
        if i == num_lists - 1:
            end_index += remainder
        separate_lists.append(all_combinations[start_index:end_index])
        
    processes = []
    
    for i, hyper_parameters in enumerate(separate_lists):
        p = multiprocessing.Process(target=worker, args=(ret, hyper_parameters, i))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    print("All workers finished")
    
    
                                                                                                                 
if __name__ == "__main__":
    main()
    