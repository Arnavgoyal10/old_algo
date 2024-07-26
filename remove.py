import pandas as pd
import refracted_advance as refracted
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi
import threading
from multiprocessing import Pool, cpu_count
import os

lock = threading.Lock()

stance= [3,5,3,5]
trial = [1,2,1,2]

def calculate_indicators(df, hyperparameters):
    lookback_config = hyperparameters[0]
    ema_length_config = hyperparameters[1]
    conv_config = hyperparameters[2]
    length_config = hyperparameters[3]
    lengthMA_config = hyperparameters[4]
    lengthSignal_config = hyperparameters[5]    
    fast_config = hyperparameters[6]
    slow_config = hyperparameters[7]
    signal_config = hyperparameters[8]

    df = df.copy()
    df = velocity_indicator.calculate_float(df, lookback=lookback_config, ema_length=ema_length_config)
    df = squeeze.squeeze_index2_float(df, conv=conv_config, length=length_config)
    
    df_macd = impulsemacd.macd(df, lengthMA=lengthMA_config, lengthSignal=lengthSignal_config)
    df[['ImpulseMACD', 'ImpulseMACDCDSignal']] = df_macd[['ImpulseMACD', 'ImpulseMACDCDSignal']]
    
    df_tsi = tsi.tsi(df, fast=fast_config, slow=slow_config, signal=signal_config)
    df[['TSI', 'TSIs']] = df_tsi[['TSI', 'TSIs']]
    
    return df


def worker(params, ret, list_1):    
    trade_columns = ['entry_time', 'entry_price', 'exit_time', 'exit_price', 'profit', 'agg_profit']
    trade_data = pd.DataFrame(columns=trade_columns)
    
    df = calculate_indicators(ret, params)
    
    temp = df.head(5).copy()
    df = df.iloc[5:].reset_index(drop=True)

    for j in range(0, len(df)):
        with lock:
            trade_data = refracted.final(temp, trade_data, [list_1[0], list_1[1]])
        if len(trade_data) > 3 and (trade_data['profit'].tail(3) < 0).all():
            if trade_data['profit'].tail(3).sum() < -85:
                return -50000  # Arbitrarily large loss to prevent further evaluation
            
        if len(trade_data) > 0 and pd.notna(trade_data['profit'].iloc[-1]) and trade_data['profit'].iloc[-1] is not None and trade_data['profit'].iloc[-1] < -85:
            return -40000  # Arbitrarily large loss to prevent further evaluation
            
        next_row = df.iloc[[j]]
        temp = pd.concat([temp, next_row], ignore_index=True)
        temp = temp.tail(5)
    
    if len(trade_data) < 14:
        return -30000
    
    months_required = [2, 3, 4, 5, 6]  # Numeric representation of Feb, Mar, Apr, May, Jun, Jul
    month_counts = trade_data['entry_time'].dt.month.value_counts()

    if not all(month_counts.get(month, 0) >= 2 for month in months_required):
        return -20000
        
    negative_sum = 0
    positive_sum = 0
    postive_counter = 0
    negative_counter = 0
    for i in range(0, len(trade_data)):
        if pd.notna(trade_data['agg_profit'].iloc[i]) and trade_data['agg_profit'].iloc[i] is not None:
            if trade_data['agg_profit'].iloc[i] < 0:
                negative_sum += trade_data['agg_profit'].iloc[i]
                negative_counter += 1
            else:
                positive_sum += trade_data['agg_profit'].iloc[i]
                postive_counter += 1
    
    if negative_counter != 0:
        if ((positive_sum)/postive_counter)/((abs(negative_sum))/(negative_counter)) < 2:
            return -10000
    
    net_profit = trade_data['agg_profit'].sum()
    return net_profit


def doing(args):
    stance, trial = args

    ohlc = ['into', 'inth', 'intl', 'intc']
    if stance == 3:
        i = 3
    elif stance == 5:
        i = 5
    
    if trial == 1:
        temp1 = pd.read_csv(f'min{i}_prof/out/Nifty_top50_agg.csv')
        data1 = pd.read_csv(f'data_{i}min/Nifty 50.csv')
        data1["time"] = pd.to_datetime(data1["time"], format="%Y-%m-%d %H:%M:%S", dayfirst=False)
        
        for col in ohlc:
            data1[col] = data1[col].astype(float)
            
        for j in range(len(temp1)):
            params = temp1.iloc[j][:-1].tolist()
            list2 = params[:2]  # First and second elements
            list1 = params[2:]  # All remaining elements
            net_profit = worker(list1, data1, list2)
            temp1.at[j, "final_net_profit"] = net_profit 
            temp1.to_csv(f'min{i}_prof/Nifty_top50_agg_corrected.csv', index=False)
            print(f"Completed {j+1} of {len(temp1)}")
        
        return
        
    else:
        temp2 = pd.read_csv(f'min{i}_prof/out/banknifty_top.csv')
        data2 = pd.read_csv(f'data_{i}min/Nifty Bank.csv')
        data2["time"] = pd.to_datetime(data2["time"], format="%Y-%m-%d %H:%M:%S", dayfirst=False)
        
        for col in ohlc:
            data2[col] = data2[col].astype(float)
    
        for j in range(len(temp2)):
            params = temp2.iloc[j][:-1].tolist()
            list2 = params[:2]
            list1 = params[2:]
            net_profit = worker(list1, data2, list2)
            temp2.at[j, "final_net_profit"] = net_profit 
            temp2.to_csv(f'min{i}_prof/bank_nifty_top_corrected.csv', index=False)
            print(f"Completed {j+1} of {len(temp2)}")
        

def main():
    # Create a list of all (stance, trial) combinations
    combinations = [(stance, trial) for stance in [3, 5] for trial in [2, 1]]
    
    # Use multiprocessing Pool to run the combinations concurrently
    with Pool(processes=min(len(combinations), cpu_count())) as pool:
        pool.map(doing, combinations)
    
    print("Completed all combinations")


if __name__ == "__main__":
    main()