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


def before(i, symbol):
    symbol1 = symbol.replace(' ', '')
    df = pd.read_csv(f'min{i}_prof/out/{symbol1}_agg.csv')
    filtered_df = df[df['net_profit'] >= 250]
    sorted_df = filtered_df.sort_values(by='net_profit', ascending=False)
    sorted_df.to_csv(f'min{i}_prof/before/{symbol}_before.csv', index=False)

def after(i, symbol):
    df = pd.read_csv(f'min{i}_prof/corrected/{symbol}_corrected.csv')
    filtered_df = df[df['final_net_profit'] >= 250]
    sorted_df = filtered_df.sort_values(by='final_net_profit', ascending=False)
    sorted_df.to_csv(f'min{i}_prof/after/{symbol}_after.csv', index=False)


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
            if trade_data['profit'].tail(3).sum() < -75:
                return -50000  # Arbitrarily large loss to prevent further evaluation
            
        if len(trade_data) > 0 and pd.notna(trade_data['profit'].iloc[-1]) and trade_data['profit'].iloc[-1] is not None and trade_data['profit'].iloc[-1] < -75:
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
    stance, symbol= args

    ohlc = ['into', 'inth', 'intl', 'intc']
    
    temp1 = pd.read_csv(f'min{stance}_prof/before/{symbol}_before.csv')
    data1 = pd.read_csv(f'data_{stance}min/{symbol}.csv')
    data1["time"] = pd.to_datetime(data1["time"], format="%Y-%m-%d %H:%M:%S", dayfirst=False)
    
    for col in ohlc:
        data1[col] = data1[col].astype(float)
        
    for j in range(len(temp1)):
        params = temp1.iloc[j][:-1].tolist()
        list2 = params[:2]  # First and second elements
        list1 = params[2:]  # All remaining elements
        net_profit = worker(list1, data1, list2)
        temp1.at[j, "final_net_profit"] = net_profit 
        temp1.to_csv(f'min{stance}_prof/corrected/{symbol}_corrected.csv', index=False)
        print(f"Completed {j+1} of {len(temp1)}")
    
    return
        

def main():
    
    before(3, 'Nifty 50')
    before(3, 'Nifty Bank')
    before(5, 'Nifty 50')
    before(5, 'Nifty Bank')     

    combinations = [(stance, symbol) for stance in [3, 5] for symbol in ['Nifty 50','Nifty Bank']]
    
    with Pool(processes=min(len(combinations), cpu_count())) as pool:
        pool.map(doing, combinations)
    
    print("Completed all combinations")
    
    after(3, 'Nifty 50')
    after(3, 'Nifty Bank')
    after(5, 'Nifty 50')
    after(5, 'Nifty Bank')


if __name__ == "__main__":
    main()