import datetime
import pandas as pd
import files_interact
import login
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
import obv

data_dict = files_interact.extract()      
client=login.login()
ohlc=['into', 'inth', 'intl', 'intc']
     
def set_stoploss(temp, side):
    global stoploss
    num = 0 
    if side == "up":
        num = temp["intl"].iloc[-1] - 10
        if num > stoploss:
            stoploss = num
    else:
        stoploss = temp["inth"].iloc[-1] + 10
        if num < stoploss:
            stoploss = num
    float(stoploss)

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
    df_okx = okx.add_trading_signals(df)
    df_tsi = df[['intc']]
    df_tsi = tsi.tsi(df_tsi)
    order_signal = False

    if (df_okx["direction"].iloc[-1] == df_okx["direction"].iloc[-2]):
        temp1 = df_tsi["TSI_13_25_13"].iloc[-1] - df_tsi["TSI_13_25_13"].iloc[-2]
        temp2 = df_tsi["TSI_13_25_13"].iloc[-2] - df_tsi["TSI_13_25_13"].iloc[-3]
        if side == "up":
            if temp1 > temp2:
                order_signal = True
                set_stoploss(df, side)
        else:
            if temp1 < temp2:
                order_signal = True
                set_stoploss(df, side)
    else:
        print("order came in waiting but got canceled")
    confirmation_waiting = False
    
    return order_signal, confirmation_waiting

def check_trade(df):
    global stoploss
    okx_signal = False
    impulse_signal = False
    tsi_waiting = False
    signal = False
    confirmation_waiting = False
    impulse_waiting = False
    small_signal = False
    
    df_okx = okx.add_trading_signals(df)
    df_squeeze = squeeze.squeeze_index(df)
    df_range = ranged.in_range_detector(df)
    df_impulse = df[['time', 'inth', 'intl', 'intc']]
    df_impulse = impulsemacd.macd(df_impulse)
    df_tsi = df[['intc']]
    df_tsi = tsi.tsi(df_tsi)
    current_time = df["time"].iloc[-1]
    comparison_time = current_time.replace(hour=15, minute=00, second=0, microsecond=0)
    bull_or_bear = "none"
    
    if current_time < comparison_time:        
        if (df_okx["direction"].iloc[-1] != df_okx["direction"].iloc[-2]):
            okx_signal = True
     
        if (okx_signal == True and df_range["in range"].iloc[-1] == False):
            if (df_squeeze["psi"].iloc[-1] < 80 and df_squeeze["psi"].iloc[-2] < 80 and df_squeeze["psi"].iloc[-1] < df_squeeze["psi"].iloc[-2]):
                bull_or_bear = df_okx["direction"].iloc[-1]
                small_signal = True
        
        if (df_impulse["ImpulseMACD"].iloc[-1] != 0 and small_signal == True): 
            if (bull_or_bear == "up"):
                impulse_temp1 = (df_impulse["ImpulseMACD"].iloc[-1]) - (df_impulse["ImpulseMACDCDSignal"].iloc[-1])
                impulse_temp2 = (df_impulse["ImpulseMACD"].iloc[-2]) - (df_impulse["ImpulseMACDCDSignal"].iloc[-2])           
            else:
                impulse_temp1 = (df_impulse["ImpulseMACDCDSignal"].iloc[-1]) - (df_impulse["ImpulseMACD"].iloc[-1])
                impulse_temp2 = (df_impulse["ImpulseMACDCDSignal"].iloc[-2]) - (df_impulse["ImpulseMACD"].iloc[-2])
            
            if (impulse_temp2 < 0 and impulse_temp1 > 0):
                impulse_waiting = True
            elif (impulse_temp1 > impulse_temp2 and abs(impulse_temp1) > 4):
                impulse_signal = True
            
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
    
        if(impulse_waiting ==True or tsi_waiting == True):
            confirmation_waiting = True    
        elif (signal == True):
            comparison_time = current_time.replace(hour=9, minute=20, second=0, microsecond=0)
            if current_time < comparison_time:
                confirmation_waiting = True
            else:
                set_stoploss(df, bull_or_bear)
        
        if (confirmation_waiting == True):
            signal = False
            
    return signal, confirmation_waiting, bull_or_bear, df_impulse["ImpulseMACD"].iloc[-1], df_impulse["ImpulseMACDCDSignal"].iloc[-1], df_tsi["TSI_13_25_13"].iloc[-1], df_tsi["TSIs_13_25_13"].iloc[-1], df["time"].iloc[-1]
              
def place_order(df):
    time = df["time"].iloc[-1]
    entry_price = df["into"].iloc[-1]
    order_signal = False
    order_placed = True
    print("order placed")
    print(time)
    
    return time, entry_price, order_signal, order_placed

def check_exit(df, side):
    df_exit = df[['intc']]
    df_exit = tsi.tsi(df_exit)
    exit_price = 0
    time = df["time"].iloc[-1]
    alarm = False
    order_placed = True
    order_exit = False
    
    if side == "up":
        if (df_exit["TSI_13_25_13"].iloc[-1] < df_exit["TSI_13_25_13"].iloc[-2]):
            alarm = True
            case = 2
    else:
        if (df_exit["TSI_13_25_13"].iloc[-1] > df_exit["TSI_13_25_13"].iloc[-2]):
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
        set_stoploss(df, side)
    return time, exit_price, order_placed, order_exit
    
def main():
    
    token = files_interact.get_token("NSE", "Nifty 50")
    lastBusDay = datetime.datetime.now()-datetime.timedelta(days=30)
    lastBusDay = lastBusDay.replace(hour=0, minute=0, second=0, microsecond=0)
    # last_day = datetime.datetime.now()-datetime.timedelta(days=27)
    # last_day = last_day.replace(hour=0, minute=0, second=0, microsecond=0)
    ret = client.get_time_price_series(exchange="NSE", token = str(int(token)), starttime=int(lastBusDay.timestamp()), interval="5")
    ret = pd.DataFrame.from_dict(ret)
    ret["time"] = pd.to_datetime(ret["time"], dayfirst=True)
    ret.sort_values(by='time', ascending=True, inplace=True)
    ret.reset_index(inplace=True)
    for col in ohlc:
        ret[col] = ret[col].astype(float)
    temp = pd.DataFrame()
    temp = ret.iloc[:530].copy()
    data_columns = ['entry_time', 'entry_price', 'exit_time', 'exit_price', 'impulse_line', 'impulse_signal', 'tsi_line', 'tsi_signal', 'tsi_time']
    trade_data = pd.DataFrame(columns=data_columns)
    ret = ret[530:]
    ret.reset_index(inplace=True)
    order_placed = False
    order_signal = False
    confirmation_waiting = False
    order_counter = 0
    bull_or_bear = None   
    
    impulse_line = 0
    impulse_signal = 0
    tsi_line = 0
    tsi_signal = 0
    tsi_time = 0
    
    
    for i in range(0, len(ret)):
        
        if (order_placed == True and order_signal == False and confirmation_waiting == False):
            exit_time, exit_price, order_placed, order_exit = check_exit(temp, bull_or_bear) 
            if order_exit == True:
                trade_data = append_value(trade_data, 'exit_time', exit_time, order_counter)
                trade_data = append_value(trade_data, 'exit_price', exit_price, order_counter)
                order_counter = order_counter + 1
        elif (order_placed == False and order_signal == False and confirmation_waiting == True):
            order_signal, confirmation_waiting = confirmation(temp, bull_or_bear)
        elif (order_placed == False and order_signal == True and confirmation_waiting == False):
            entry_time , entry_price, order_signal, order_placed = place_order(temp)
            trade_data = append_value(trade_data, 'entry_time', entry_time, order_counter)
            trade_data = append_value(trade_data, 'entry_price', entry_price, order_counter)
            trade_data = append_value(trade_data, 'impulse_line', impulse_line, order_counter)
            trade_data = append_value(trade_data, 'impulse_signal', impulse_signal, order_counter)
            trade_data = append_value(trade_data, 'tsi_line', tsi_line, order_counter)
            trade_data = append_value(trade_data, 'tsi_signal', tsi_signal, order_counter)
            trade_data = append_value(trade_data, 'tsi_time', tsi_time, order_counter)
        elif (order_placed == False and order_signal == False and confirmation_waiting ==  False):
            order_signal, confirmation_waiting, bull_or_bear, impulse_line, impulse_signal, tsi_line, tsi_signal , tsi_time= check_trade(temp)
        
        
        if (i%50 == 0):
            print("working fine")
            print(temp["time"].iloc[-1])
        next_row = ret.iloc[[i]]
        temp = pd.concat([temp, next_row], ignore_index=True) 
    
    current_directory = os.getcwd()
    df_comb_file = os.path.join(current_directory, 'testing4.csv')
    trade_data.to_csv(df_comb_file, index=False)
    
    
if __name__ == "__main__":
    main()
    