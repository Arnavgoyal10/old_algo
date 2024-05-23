import os
import pandas as pd
import refracted
import multiprocessing


ohlc=['into', 'inth', 'intl', 'intc']
     

base_directory = os.getcwd()
data_directory = os.path.join(base_directory, "data")
 
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
    
    
    hyperparameter1 = [[8,2,14,20,50,20,34,9,13,25,13], [9,2,14,20,50,20,34,9,13,25,13], [10,2,14,20,50,20,34,9,13,25,13]]
    hyperparameter2 = [[10,2,12,20,50,20,34,9,13,25,13], [10,2,13,20,50,20,34,9,13,25,13], [10,2,14,20,50,20,34,9,13,25,13]]
    
    
    hyperparameters_list = [hyperparameter1, hyperparameter2]
    
    processes = []
    
    for i, hyper_parameters in enumerate(hyperparameters_list):
        p = multiprocessing.Process(target=worker, args=(ret, hyper_parameters, i))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    print("All workers finished")
    
    
                                                                                                                 
if __name__ == "__main__":
    main()
    