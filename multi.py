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

ohlc=['into', 'inth', 'intl', 'intc']
base_directory = os.getcwd()
data_directory = os.path.join(base_directory, "data_multi")

def calculate_indicators(df, hyperparamas):
    
    (lookback_config, ema_length_config, conv_config, 
    length_config, lengthMA_config, lengthSignal_config, fast_config, slow_config, 
    signal_config) = hyperparamas
    
    df = df.copy()
    
    df = velocity_indicator.calculate(df, lookback=lookback_config, ema_length=ema_length_config)
    df = squeeze.squeeze_index(df,conv=conv_config, length=length_config)
    
    df_macd = impulsemacd.macd(df, lengthMA = lengthMA_config, lengthSignal = lengthSignal_config)
    df[['ImpulseMACD', 'ImpulseMACDCDSignal']] = df_macd[['ImpulseMACD', 'ImpulseMACDCDSignal']]
    
    df_tsi = tsi.tsi(df, fast = fast_config, slow = slow_config, signal = signal_config)
    df[['TSI', 'TSIs']] = df_tsi[['TSI', 'TSIs']]
    
    return df

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
        parse1 = hyper_parameters[i][2:]
        parse2 = hyper_parameters[i][:2]
        
        df = calculate_indicators(ret, parse1)
        temp = pd.DataFrame()
        temp = df.iloc[:200].copy()
        df = df[200:]
        
        for j in range(0, len(df)):
            trade_data = refracted.final(temp,trade_data, parse2)        
            
            if (j%150 == 0):
                print(f'"working fine {j}"')
                print(temp["time"].iloc[-1])
            
            next_row = df.iloc[[j]]
            temp = pd.concat([temp, next_row], ignore_index=True)
            temp = temp.iloc[-110:].reset_index(drop=True)
        
        net_profit = append_value(net_profit, 'stoploss', parse2[0], i)
        net_profit = append_value(net_profit, 'squee', parse2[1], i)
        net_profit = append_value(net_profit, 'lookback', parse1[0], i)
        net_profit = append_value(net_profit, 'ema_length', parse1[1], i)
        net_profit = append_value(net_profit, 'conv', parse1[2], i)
        net_profit = append_value(net_profit, 'length', parse1[3], i)
        net_profit = append_value(net_profit, 'lengthMA', parse1[4], i)
        net_profit = append_value(net_profit, 'lengthSignal', parse1[5], i)
        net_profit = append_value(net_profit, 'fast', parse1[6], i)
        net_profit = append_value(net_profit, 'slow', parse1[7], i)
        net_profit = append_value(net_profit, 'signal', parse1[8], i)
        net_profit_1 = trade_data['profit'].sum()
        net_profit = append_value(net_profit, 'net_profit', net_profit_1, i)
    
    df_comb_file = os.path.join(data_directory, f'netprofit_{counter}.csv')
    net_profit.to_csv(df_comb_file, index=True)
             
def worker(ret, hyper_parameters, counter):
    
    print("Worker started ", counter)
    working(ret, hyper_parameters, counter)
    print("Worker finished ", counter) 
    
def main():

    with cProfile.Profile() as pr:

        file_path = 'excel_files/nifty_full_feb.xlsx'
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
    
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats("profile_multi.prof")
    
                                                                                                             
if __name__ == "__main__":
    main()
    