import datetime
import pandas as pd
import tsi
import threading
import os
import argparse
import strategy


# from tvDatafeed import TvDatafeed, Interval

# tv = TvDatafeed()

ohlc=['into', 'inth', 'intl', 'intc']
     


def append_value(dataframe, column_name, value, index):
    if index >= len(dataframe):
        new_row = pd.DataFrame([{col: (value if col == column_name else None) for col in dataframe.columns}])
        if not new_row.empty and not new_row.isna().all().all():
            new_row = new_row.dropna(axis=1, how='all')
            dataframe = pd.concat([dataframe, new_row], ignore_index=True)
    else:
        dataframe.at[index, column_name] = value
    return dataframe

def loop_function(range_start, range_end):
        
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
    
    for stoploss in range(range_start, range_end):
        for super_trend_period in range(8, 26):
            for super_trend_multiplier in [x * 0.1 for x in range(15, 38)]:
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
                                                                                file_path = 'nifty_recent.xlsx'
                                                                                ret = pd.read_excel(file_path)
                                                                                ret["time"] = pd.to_datetime(ret["time"], dayfirst=True)
                                                                                for col in ohlc:
                                                                                    ret[col] = ret[col].astype(float) 
                                                                                    
                                                                                temp = pd.DataFrame()
                                                                                temp = ret.iloc[:80].copy()
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
                                                                                    
                                                                                    entry_frame_data, trade_data = strategy.final(temp, entry_frame_data, trade_data,hyperparameter)
                                                                                        
                                                                                    if (i%50 == 0):
                                                                                        print("working fine")
                                                                                        print(temp["time"].iloc[-1])
                                                                                    next_row = ret.iloc[[i]]
                                                                                    temp = pd.concat([temp, next_row], ignore_index=True)
                                                                                
                                                                
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
                                                                    
                                                                                
                                                                                current_directory = os.getcwd()
                                                                                df_comb_file = os.path.join(current_directory, f'entries_{range_start}.csv')
                                                                                entry_frame_data.to_csv(df_comb_file, index=True)
                                                                                trade_data1 = os.path.join(current_directory, f'trade_data_{range_start}.csv')
                                                                                trade_data.to_csv(trade_data1, index=True)
                                                                                df_comb_file = os.path.join(current_directory, f'netprofit_{range_start}.csv')
                                                                                net_profit.to_csv(df_comb_file, index=True)
                                                                                    
def main():
    
    # ret = tv.get_hist(symbol='NIFTY',exchange='NSE',interval=Interval.in_5_minute,n_bars=3000)
    
    stoploss_ranges = [(x, x + 1) for x in range(5, 21)]
    threads = []

    # Create and start threads
    for r in stoploss_ranges:
        thread = threading.Thread(target=loop_function, args=(r[0], r[1]))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print("All threads have completed their execution.")
    
                                                    
    
                                                                                                                                                   
if __name__ == "__main__":
    main()
    