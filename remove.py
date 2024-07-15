import pandas as pd
import refracted_advance as refracted
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi
import threading
lock = threading.Lock()

stance= [1,3,5]


def calculate_indicators(df, hyperparameters):
    # (lookback_config, ema_length_config, conv_config, length_config, 
    #  lengthMA_config, lengthSignal_config, fast_config, slow_config, 
    #  signal_config) = hyperparameters
    
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
    temp = df.copy()

    for j in range(0, len(df)):
        with lock:
            trade_data = refracted.final(temp, trade_data, [list_1[0], list_1[1]])
        if len(trade_data) > 3 and (trade_data['profit'].tail(3) < 0).all():
            if trade_data['profit'].tail(3).sum() < -85:
                return -50000  # Arbitrarily large loss to prevent further evaluation
            
        if len(trade_data) > 0 and pd.notna(trade_data['profit'].iloc[-1]) and trade_data['profit'].iloc[-1] is not None and trade_data['profit'].iloc[-1] < -85:
            return -50000  # Arbitrarily large loss to prevent further evaluation
            
        next_row = df.iloc[[j]]
        temp = pd.concat([temp, next_row], ignore_index=True)
        temp = temp.tail(5)
    
    if len(trade_data) < 14:
        return -50000
    
    
    months_required = [2, 3, 4, 5, 6]  # Numeric representation of Feb, Mar, Apr, May, Jun, Jul
    month_counts = trade_data['entry_time'].dt.month.value_counts()

    if not all(month_counts.get(month, 0) >= 2 for month in months_required):
        return -50000
        
    
    less_than_zero = (trade_data['agg_profit'] < 0).sum()
    greater_than_zero = (trade_data['agg_profit'] > 0).sum()
    
    if (greater_than_zero/less_than_zero) < 3.2:
        return -50000

        
    net_profit = trade_data['agg_profit'].sum()
    return net_profit




for i in stance:
    # df = pd.read_csv(f'min{i}_prof/Nifty 50_agg.csv')
    # df1 = pd.read_csv(f'min{i}_prof/Nifty Bank_agg.csv')

    # # Filter out rows with net_profit less than 100
    # filtered_df = df[df['net_profit'] >= 250]
    # fil_df1 = df1[df1['net_profit'] >= 250]

    # # Sort the DataFrame by net_profit in descending order
    # sorted_df = filtered_df.sort_values(by='net_profit', ascending=False)
    # sorted_1 = fil_df1.sort_values(by='net_profit', ascending=False)
    # # Save the sorted and filtered data to a new CSV file
    # sorted_1.to_csv(f'min{i}_prof/bank_nifty_top.csv', index=False)
    # sorted_df.to_csv(f'min{i}_prof/Nifty_top50_agg.csv', index=False)

    temp1 = pd.read_csv(f'min{i}_prof/Nifty_top50_agg.csv')
    temp2 = pd.read_csv(f'min{i}_prof/bank_nifty_top.csv')
    data1 = pd.read_csv(f'data_{i}min/Nifty 50.csv')
    data2 = pd.read_csv(f'data_{i}min/Nifty Bank.csv')
    
    ohlc = ['into', 'inth', 'intl', 'intc']
    
    data1["time"] = pd.to_datetime(data1["time"], format="%Y-%m-%d %H:%M:%S", dayfirst=False)
    data2["time"] = pd.to_datetime(data2["time"], format="%Y-%m-%d %H:%M:%S", dayfirst=False)
    for col in ohlc:
        data1[col] = data1[col].astype(float)
        data2[col] = data2[col].astype(float)
    
    for j in range(len(temp2)):
        params = temp2.iloc[j][:-1].tolist()
        list2 = params[:2]
        list1 = params[2:]
        net_profit = worker(list1, data2, list2)
        temp2["final_net_profit"] = net_profit
        temp2.to_csv(f'min{i}_prof/bank_nifty_top_corrected.csv', index=False)
        print(f"Completed {j+1} of {len(temp2)}")
    
    for j in range(len(temp1)):
        params = temp1.iloc[j][:-1].tolist()
        list2 = params[:2]  # First and second elements
        list1 = params[2:]  # All remaining elements
        net_profit = worker(list1, data1, list2)
        temp1["final_net_profit"] = net_profit
        temp1.to_csv(f'min{i}_prof/Nifty_top50_agg_corrected.csv', index=False)
        print(f"Completed {j+1} of {len(temp1)}")
    

    