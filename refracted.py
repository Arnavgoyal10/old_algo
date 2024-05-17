import pandas as pd
import supertrend
import impulsemacd
import tsi
import threading
import os
import argparse
import velocity_indicator
import squeeze
import obv
import okxfinal
import okx
import hull_ma

def append_value(dataframe, column_name, value, index):
    if index >= len(dataframe):
        new_row = pd.DataFrame([{col: (value if col == column_name else None) for col in dataframe.columns}])
        if not new_row.empty and not new_row.isna().all().all():
            new_row = new_row.dropna(axis=1, how='all')
            dataframe = pd.concat([dataframe, new_row], ignore_index=True)
    else:
        dataframe.at[index, column_name] = value
    return dataframe

    
ohlc=['into', 'inth', 'intl', 'intc']


currect_state = 0
# 0 == order not placed, 3 == order placed, 2 == confirmation waiting, 1 == order_signal, 4 == exit_signal

market_direction = 0
# 1 == up, -1 == down, 0 == no direction

stoploss = 0
order_count = 0
buying_price = 0
exit_price = 0
exit_time = 0
order_flag_count = 0



''''''''''''

stoploss_config = 10
squee_config  = 2

# veloctity_order settings
lookback_config=14
ema_length_config=20

# squee_order settings
conv_config = 50
length_config = 20

# impulse_order settings
lengthMA_config = 34
lengthSignal_config = 9

# tsi_order settings
fast_config = 13
slow_config = 25
signal_config = 13

# obv_exit settings
window_len_config = 28
v_len_config = 14
len10_config = 1
slow_length_config = 26 

''''''''''''

def confirmation(df, market_direction):
    stoploss =0
    buying_price = 0
    df_tsi = df[['intc']]
    df_tsi = tsi.tsi(df_tsi, fast = fast_config, slow = slow_config, signal = signal_config)
    temp1 = df_tsi["TSI"].iloc[-1] - df_tsi["TSI"].iloc[-2]
    temp2 = df_tsi["TSI"].iloc[-2] - df_tsi["TSI"].iloc[-3]
    if market_direction == 1:
        if temp1 > temp2:
            buying_price = df["inth"].iloc[-1]
            stoploss = set_stoploss(df, market_direction, stoploss)
            return 1, market_direction, buying_price, stoploss
    else:
        if temp1 < temp2:
            buying_price = df["intl"].iloc[-1]
            stoploss = set_stoploss(df, market_direction, stoploss)
            return 1, market_direction, buying_price, stoploss
        
    return 0, 0, 0, 0
    # return state, market_direction, buying_price, stoploss
    
def set_stoploss(df, market_direction, stoploss):
    temp = 0.0
    if market_direction == 1:
        temp = df["intl"].iloc[-1] - stoploss_config
        if (temp > stoploss or stoploss == 0):
            stoploss = temp
    else:
        temp = df["inth"].iloc[-1] + stoploss_config
        if (temp < stoploss or stoploss == 0):
            stoploss = temp
    return stoploss

def check_exit(df, market_direction, stoploss):
    df_exit = obv.calculate_custom_indicators(df, window_len = window_len_config, v_len =v_len_config,len10= len10_config, slow_length = slow_length_config)
    exit_price = 0
    exit_time = df["time"].iloc[-1]
    
    if market_direction == 1:
        if ((df_exit["b5"].iloc[-1]) < df_exit["b5"].iloc[-2]):
            exit_price = df["intc"].iloc[-1]
            return 4, exit_price, exit_time, stoploss
    else:
        if ((df_exit["b5"].iloc[-1]) > df_exit["b5"].iloc[-2]):
            exit_price = df["intc"].iloc[-1]
            return 4, exit_price, exit_time, stoploss
        
    if (df["inth"].iloc[-1] >= stoploss and df["intl"].iloc[-1] <= stoploss):
        exit_price = stoploss
        return 4, exit_price, exit_time, stoploss

    stoploss = set_stoploss(df, market_direction, stoploss)
    return 3, exit_price, exit_time, stoploss
        
def check_trade(df):
    buying_price = 0
    waiting = 0
    market_direction = 0
    stoploss = 0 
    
    current_time = df["time"].iloc[-1]
    comparison_time = current_time.replace(hour=15, minute=00, second=0, microsecond=0)
    
    if current_time > comparison_time:
        return 0, 0 , 0, 0
        # return state, market_direction, buying_price, stoploss
    
    df_velocity = velocity_indicator.calculate(df, lookback=lookback_config, ema_length=ema_length_config) 
    
    if(df_velocity["smooth_velocity"].iloc[-1] > 0  and df_velocity["smooth_velocity"].iloc[-2] > 0 or df_velocity["smooth_velocity"].iloc[-1] < 0  and df_velocity["smooth_velocity"].iloc[-2] < 0):
        return 0, 0 , 0, 0
    
    df_squeeze = squeeze.squeeze_index(df,conv=conv_config, length=length_config)
    
    if not (df_squeeze["psi"].iloc[-1] < 80 and df_squeeze["psi"].iloc[-2] < 80 and (df_squeeze["psi"].iloc[-1] - squee_config) < df_squeeze["psi"].iloc[-2]):
        return 0, 0 , 0, 0
        
    if df_velocity["smooth_velocity"].iloc[-1] < 0:
        market_direction = -1
    else:
        market_direction = 1
        
    df_impulse = df[['time', 'inth', 'intl', 'intc']]
    df_impulse = impulsemacd.macd(df_impulse, lengthMA = lengthMA_config, lengthSignal = lengthSignal_config)
    
    if df_impulse["macd"].iloc[-1] == 0:
        return 0, 0 , 0, 0
        
    if (market_direction == 1):
        impulse_temp1 = (df_impulse["ImpulseMACD"].iloc[-1]) - (df_impulse["ImpulseMACDCDSignal"].iloc[-1])
        impulse_temp2 = (df_impulse["ImpulseMACD"].iloc[-2]) - (df_impulse["ImpulseMACDCDSignal"].iloc[-2])           
    else:
        impulse_temp1 = (df_impulse["ImpulseMACDCDSignal"].iloc[-1]) - (df_impulse["ImpulseMACD"].iloc[-1])
        impulse_temp2 = (df_impulse["ImpulseMACDCDSignal"].iloc[-2]) - (df_impulse["ImpulseMACD"].iloc[-2])
    
    if (impulse_temp2 < 0 and impulse_temp1 > 0):
        waiting = 1
    # elif (impulse_temp1 > impulse_temp2 and abs(impulse_temp1) > 4):
    elif not (impulse_temp1 > impulse_temp2):
        return 0, 0 , 0, 0
    
    df_tsi = df[['intc']]
    df_tsi = tsi.tsi(df_tsi, fast = fast_config, slow = slow_config, signal = signal_config)
    if (market_direction == 1):
        tsi_temp1 = (df_tsi["TSI"].iloc[-1]) - (df_tsi["TSIs"].iloc[-1])
        tsi_temp2 = (df_tsi["TSI"].iloc[-2]) - (df_tsi["TSIs"].iloc[-2])              
    else:
        tsi_temp1 = (df_tsi["TSIs"].iloc[-1]) - (df_tsi["TSI"].iloc[-1])
        tsi_temp2 = (df_tsi["TSIs"].iloc[-2]) - (df_tsi["TSI"].iloc[-2])
            
    if (tsi_temp2 < 0 and tsi_temp1 > 0):
        waiting = 1
    elif not (tsi_temp1 > tsi_temp2):
        return 0, 0 , 0, 0
    
    comparison_time = current_time.replace(hour=9, minute=20, second=0, microsecond=0)
    if current_time < comparison_time:
        waiting = 1
    
    if waiting == 1:
        return 2, 0 , 0, 0
    else:
        stoploss = set_stoploss(df, market_direction, stoploss)
        
        if market_direction == 1:
            buying_price = df["inth"].iloc[-1]
        else:
            buying_price = df["intl"].iloc[-1]
        return 1, market_direction, buying_price, stoploss
    
def final(temp, trade_data, hyper_parameters, senario):
    global stoploss_config, squee_config, lookback_config, ema_length_config, conv_config, length_config
    global lengthMA_config, lengthSignal_config, fast_config, slow_config, signal_config
    global window_len_config, v_len_config, len10_config, slow_length_config
    
    global currect_state, market_direction, stoploss, order_count, buying_price, exit_time, exit_price, order_flag_count
    
    
    # Unpacking scenario list
    (currect_state, market_direction, stoploss, order_count, buying_price, 
    exit_time, exit_price) = senario

    # Unpacking hyper_parameters list
    (stoploss_config, squee_config, lookback_config, ema_length_config, conv_config, 
    length_config, lengthMA_config, lengthSignal_config, fast_config, slow_config, 
    signal_config, window_len_config, v_len_config, len10_config, slow_length_config) = hyper_parameters

    
    new_currect_state, new_market_direction, new_buying_price, new_stoploss = check_trade(temp)
    if market_direction != new_market_direction:
        if currect_state == 3:
            if market_direction == 1:
                profit  = exit_price - entry_price
            else:
                profit  = entry_price - exit_price
            trade_data = append_value(trade_data, 'profit', profit, order_count)
            order_count = order_count+1

        currect_state, market_direction, buying_price, stoploss = new_currect_state, new_market_direction, new_buying_price, new_stoploss
        order_flag_count = 0
    
    