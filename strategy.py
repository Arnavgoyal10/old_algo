import datetime
import pandas as pd
import files_interact
import supertrend
import impulsemacd
import tsi
import threading
import os
import argparse
import hhll_indicator
import velocity_indicator
import hull_ma
import okx
import squeeze
import ranged
import okxfinal
import obv
import okxfinal
import okx
ohlc=['into', 'inth', 'intl', 'intc']


order_placed = False
order_signal = False
confirmation_waiting = False
entry_number = 0
bull_or_bear = None
order_exit = False
order_flag_count = 0  
stoploss = 0 
reason = "nothing"
price_threshold = 0
order_count = 0 

def set_stoploss(temp, side, stoploss):
    num = 0.0
    if side == "up":
        num = temp["intl"].iloc[-1] - 10
        print(num)
        if (num > stoploss or stoploss == 0):
            stoploss = num
            print("stoploss_set at")
            print(temp["time"].iloc[-1])
    else:
        num = temp["inth"].iloc[-1] + 10
        print(num)
        if (num < stoploss or stoploss == 0):
            stoploss = num
            print("stoploss_set at")
            print(temp["time"].iloc[-1])
    print(stoploss)
    return stoploss

def append_value(dataframe, column_name, value, index):
    if index >= len(dataframe):
        new_row = pd.DataFrame([{col: (value if col == column_name else None) for col in dataframe.columns}])
        if not new_row.empty and not new_row.isna().all().all():
            new_row = new_row.dropna(axis=1, how='all')
            dataframe = pd.concat([dataframe, new_row], ignore_index=True)
    else:
        dataframe.at[index, column_name] = value
    return dataframe

def confirmation(df, side):
    # df_okx = okx.add_trading_signals(df)
    df_super = supertrend.SuperTrend(df, period= 17, multiplier=3, ohlc=ohlc)
    df_tsi = df[['intc']]
    df_tsi = tsi.tsi(df_tsi)
    order_signal = False
    stoploss = 0
    price_threshold = 0

    if (df_super["STX17_3.0"].iloc[-1] == df_super["STX17_3.0"].iloc[-2]):
        temp1 = df_tsi["TSI_13_25_13"].iloc[-1] - df_tsi["TSI_13_25_13"].iloc[-2]
        temp2 = df_tsi["TSI_13_25_13"].iloc[-2] - df_tsi["TSI_13_25_13"].iloc[-3]
        if side == "up":
            if temp1 > temp2:
                order_signal = True
                stoploss = set_stoploss(df, side, stoploss)
        else:
            if temp1 < temp2:
                order_signal = True
                stoploss = set_stoploss(df, side, stoploss)
    else:
        print("order came in waiting but got canceled")
    confirmation_waiting = False
    
    if order_signal == True:
        if side == "up":
            price_threshold = df["inth"].iloc[-1]
        else:
            price_threshold = df["intl"].iloc[-1]
    
    return order_signal, confirmation_waiting, stoploss, price_threshold

def check_trade(df):
    supertrend_signal = False
    impulse_signal = False
    tsi_waiting = False
    signal = False
    confirmation_waiting = False
    impulse_waiting = False
    small_signal = False
    price_threshold = 0
    
    # df_okx = okx.add_trading_signals(df)
    # df_super = supertrend.SuperTrend(df, period= 17, multiplier=1.5, ohlc=ohlc)
    df_velocity = velocity_indicator.calculate(df)
    df_squeeze = squeeze.squeeze_index(df)
    df_range = ranged.in_range_detector(df)
    df_impulse = df[['time', 'inth', 'intl', 'intc']]
    df_impulse = impulsemacd.macd(df_impulse)
    df_tsi = df[['intc']]
    df_tsi = tsi.tsi(df_tsi)
    current_time = df["time"].iloc[-1]
    comparison_time = current_time.replace(hour=15, minute=00, second=0, microsecond=0)
    bull_or_bear = None
    stoploss = 0
    reason = "nothing"
    
    
    if current_time < comparison_time:        
        # if (df_super["STX17_1.5"].iloc[-1] != df_super["STX17_1.5"].iloc[-2]):
        # if (df_okx["direction"].iloc[-1] == "up" or df_okx["direction"].iloc[-1] == "down"):
        if(df_velocity["smooth_velocity"].iloc[-1] > 0  and df_velocity["smooth_velocity"].iloc[-2] < 0):
            supertrend_signal = True
        elif(df_velocity["smooth_velocity"].iloc[-1] < 0  and df_velocity["smooth_velocity"].iloc[-2] > 0):
            supertrend_signal = True
        else:
            reason = "super_trend_ said no"
     
        if (supertrend_signal == True and df_range["in range"].iloc[-1] == False):
            if (df_squeeze["psi"].iloc[-1] < 80 and df_squeeze["psi"].iloc[-2] < 80 and (df_squeeze["psi"].iloc[-1]-2.0) < df_squeeze["psi"].iloc[-2]):
                # bull_or_bear = df_super["STX17_1.5"].iloc[-1]
                # bull_or_bear = df_okx["direction"].iloc[-1]
                if df_velocity["smooth_velocity"].iloc[-1] < 0:
                    bull_or_bear = "down"
                else:
                    bull_or_bear = "up"
                small_signal = True
            else:
                reason = "Squee said no"
        elif (df_range["in range"].iloc[-1] == True):
            reason = "inrange said no"
        if (df_impulse["ImpulseMACD"].iloc[-1] != 0 and small_signal == True): 
            if (bull_or_bear == "up"):
                impulse_temp1 = (df_impulse["ImpulseMACD"].iloc[-1]) - (df_impulse["ImpulseMACDCDSignal"].iloc[-1])
                impulse_temp2 = (df_impulse["ImpulseMACD"].iloc[-2]) - (df_impulse["ImpulseMACDCDSignal"].iloc[-2])           
            else:
                impulse_temp1 = (df_impulse["ImpulseMACDCDSignal"].iloc[-1]) - (df_impulse["ImpulseMACD"].iloc[-1])
                impulse_temp2 = (df_impulse["ImpulseMACDCDSignal"].iloc[-2]) - (df_impulse["ImpulseMACD"].iloc[-2])
            
            if (impulse_temp2 < 0 and impulse_temp1 > 0):
                impulse_waiting = True
            # elif (impulse_temp1 > impulse_temp2 and abs(impulse_temp1) > 4):
            elif (impulse_temp1 > impulse_temp2):
                impulse_signal = True
            else:
                reason = "impulse said no"
        elif(df_impulse["ImpulseMACD"].iloc[-1] == 0):
            reason = "impulse is 0"
        if (impulse_signal == True or impulse_waiting == True):
            if (bull_or_bear == "up"):
                tsi_temp1 = (df_tsi["TSI_13_25_13"].iloc[-1]) - (df_tsi["TSIs_13_25_13"].iloc[-1])
                tsi_temp2 = (df_tsi["TSI_13_25_13"].iloc[-2]) - (df_tsi["TSIs_13_25_13"].iloc[-2])              
            else:
                tsi_temp1 = (df_tsi["TSIs_13_25_13"].iloc[-1]) - (df_tsi["TSI_13_25_13"].iloc[-1])
                tsi_temp2 = (df_tsi["TSIs_13_25_13"].iloc[-2]) - (df_tsi["TSI_13_25_13"].iloc[-2])
            
            if (tsi_temp2 < 0 and tsi_temp1 > 0):
                tsi_waiting = True
            elif (tsi_temp1 > tsi_temp2):
                signal = True
            else:
                impulse_waiting = False
                reason = "tsi said no"
    
        if(impulse_waiting == True or tsi_waiting == True):
            confirmation_waiting = True    
        elif (signal == True):
            comparison_time = current_time.replace(hour=9, minute=20, second=0, microsecond=0)
            if current_time < comparison_time:
                confirmation_waiting = True
            else:
                stoploss = set_stoploss(df, bull_or_bear, stoploss)
        
        if (confirmation_waiting == True):
            signal = False 
            reason = "order going in confirmation"   
    
    if signal == True:
        reason = "placeing order"
        if bull_or_bear == "up":
            price_threshold = df["inth"].iloc[-1]
        else:
            price_threshold = df["intl"].iloc[-1]
    
    if signal == False and confirmation_waiting == False:
        bull_or_bear = None
    
    return signal, confirmation_waiting, bull_or_bear, stoploss, reason, price_threshold
              
def place_order(df, bull_or_bear, stoploss):
    time = df["time"].iloc[-1]
    entry_price = df["into"].iloc[-1]
    order_signal = False
    order_placed = True
    stoploss = set_stoploss(df, bull_or_bear, stoploss)
    print("order placed")
    print(time)
    
    return time, entry_price, order_signal, order_placed, stoploss

def check_exit(df, side, stoploss):
    df_exit = obv.calculate_custom_indicators(df)
    # df_exit = df[['intc']]
    # df_exit = tsi.tsi(df_exit)
    exit_price = 0
    time = df["time"].iloc[-1]
    alarm = False
    order_placed = True
    order_exit = False
    
    if side == "up":
        if ((df_exit["b5"].iloc[-1]) < df_exit["b5"].iloc[-2]):
        # if ((df_exit["TSI_13_25_13"].iloc[-1]+2) < df_exit["TSI_13_25_13"].iloc[-2]):
            alarm = True
            case = 2
    else:
        if ((df_exit["b5"].iloc[-1]) > df_exit["b5"].iloc[-2]):
        # if ((df_exit["TSI_13_25_13"].iloc[-1]-2) > df_exit["TSI_13_25_13"].iloc[-2]):
            alarm = True
            case = 2
    if (df["inth"].iloc[-1] >= stoploss and df["intl"].iloc[-1] <= stoploss):
        alarm = True
        case = 1
    if alarm == True:
        order_placed = False
        order_exit = True
        if case == 1:
            exit_price = stoploss
        if case == 2:
            exit_price = df["intc"].iloc[-1]
    else:
        stoploss = set_stoploss(df, side, stoploss)
    return time, exit_price, order_placed, order_exit, stoploss

def final(temp, entry_frame_data, trade_data):
    global order_placed, order_signal, confirmation_waiting, entry_number, bull_or_bear, order_exit, order_flag_count, stoploss
    global reason, price_threshold, order_count, exit_time, exit_price, entry_time, entry_price
    
    
    if (order_placed == True and order_signal == False and confirmation_waiting == False):
        exit_time, exit_price, order_placed, order_exit, stoploss = check_exit(temp, bull_or_bear, stoploss) 
        if order_exit == True:
            trade_data = append_value(trade_data, 'exit_time', exit_time, order_count)
            trade_data = append_value(trade_data, 'exit_price', exit_price, order_count)
            if bull_or_bear == "up":
                profit  = exit_price - entry_price
            else:
                profit  = entry_price - exit_price
            trade_data = append_value(trade_data, 'profit', profit, order_count)
            order_count = order_count+1
            bull_or_bear = None
            order_exit = False
    
    elif (order_placed == False and order_signal == False and confirmation_waiting == True):
        order_signal, confirmation_waiting, stoploss, price_threshold= confirmation(temp, bull_or_bear)
        if order_signal == True:
            reason = "came in waiting, placing order"
        else:
            reason = "came in wating, got caneled"
            bull_or_bear = None
    
    elif (order_placed == False and order_signal == True and confirmation_waiting == False):
        if order_flag_count < 2:
            if (temp["inth"].iloc[-1] >= price_threshold and temp["intl"].iloc[-1] <= price_threshold):
                entry_time , entry_price, order_signal, order_placed, stoploss = place_order(temp, bull_or_bear, stoploss)
                trade_data = append_value(trade_data, 'entry_time', entry_time, order_count)
                trade_data = append_value(trade_data, 'entry_price', price_threshold, order_count)
                order_flag_count = 0
            else:
                order_flag_count = order_flag_count +1
        else:
            order_signal = False
            order_flag_count = 0
            bull_or_bear = None

    n_order_signal, n_confirmation_waiting, n_bull_or_bear, n_stoploss, n_reason, n_price_threshold = check_trade(temp)
    if bull_or_bear == None:
        order_signal, confirmation_waiting, bull_or_bear, stoploss, reason, price_threshold = n_order_signal, n_confirmation_waiting, n_bull_or_bear, n_stoploss, n_reason, n_price_threshold
        order_flag_count = 0

    elif bull_or_bear == "up" and n_bull_or_bear == "down":
        order_signal, confirmation_waiting, bull_or_bear, stoploss, reason, price_threshold = n_order_signal, n_confirmation_waiting, n_bull_or_bear, n_stoploss, n_reason, n_price_threshold
        reason = "new order came in"
        order_flag_count = 0
        if order_placed == True:
            order_exit = True
    elif bull_or_bear == "down" and n_bull_or_bear == "up":
        order_signal, confirmation_waiting, bull_or_bear, stoploss, reason, price_threshold = n_order_signal, n_confirmation_waiting, n_bull_or_bear, n_stoploss, n_reason, n_price_threshold
        reason = "new order came in"
        order_flag_count = 0
        if order_placed == True:
            order_exit = True
            
    if order_exit == True:
        trade_data = append_value(trade_data, 'exit_time', temp["time"].iloc[-1], order_count)
        trade_data = append_value(trade_data, 'exit_price', temp["intc"].iloc[-1], order_count)
        if bull_or_bear == "up":
            profit  = exit_price - entry_price
        else:
            profit  = entry_price - exit_price
        trade_data = append_value(trade_data, 'profit', profit, order_count)
        order_count = order_count+1
        order_exit = False
    
    
    entry_frame_data = append_value(entry_frame_data, 'time', temp["time"].iloc[-1], entry_number)
    entry_frame_data = append_value(entry_frame_data, 'reason', reason, entry_number)
    entry_frame_data = append_value(entry_frame_data, 'bull or bear', bull_or_bear, entry_number)
    entry_number = entry_number + 1
    
    return entry_frame_data, trade_data