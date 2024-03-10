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
# trio-websocket, websocket, websocket-client, ypy-websocket 
import obv
# from tvDatafeed import TvDatafeed, Interval

# tv = TvDatafeed()

# data_dict = files_interact.extract()      
# client=login.login()
ohlc=['into', 'inth', 'intl', 'intc']
     
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
    
    return order_signal, confirmation_waiting, stoploss

def check_trade(df):
    supertrend_signal = False
    impulse_signal = False
    tsi_waiting = False
    signal = False
    confirmation_waiting = False
    impulse_waiting = False
    small_signal = False
    
    # df_okx = okx.add_trading_signals(df)
    df_super = supertrend.SuperTrend(df, period= 17, multiplier=3, ohlc=ohlc)
    df_squeeze = squeeze.squeeze_index(df)
    df_range = ranged.in_range_detector(df)
    df_impulse = df[['time', 'inth', 'intl', 'intc']]
    df_impulse = impulsemacd.macd(df_impulse)
    df_tsi = df[['intc']]
    df_tsi = tsi.tsi(df_tsi)
    current_time = df["time"].iloc[-1]
    comparison_time = current_time.replace(hour=15, minute=00, second=0, microsecond=0)
    bull_or_bear = "none"
    stoploss = 0
    reason = "nothing"
    
    
    if current_time < comparison_time:        
        if (df_super["STX17_3.0"].iloc[-1] != df_super["STX17_3.0"].iloc[-2]):
            supertrend_signal = True
        else:
            reason = "super_trend_ said no"
     
        if (supertrend_signal == True and df_range["in range"].iloc[-1] == False):
            if (df_squeeze["psi"].iloc[-1] < 80 and df_squeeze["psi"].iloc[-2] < 80 and df_squeeze["psi"].iloc[-1] < df_squeeze["psi"].iloc[-2]):
                bull_or_bear = df_super["STX17_3.0"].iloc[-1]
                small_signal = True
            else:
                reason = "Squee said no"
        
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
            else:
                reason = "impulse said no"

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
    return signal, confirmation_waiting, bull_or_bear, stoploss, reason
              
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
        stoploss = set_stoploss(df, side, stoploss)
    return time, exit_price, order_placed, order_exit, stoploss
    
def main():
    # ret = tv.get_hist(symbol='NIFTY',exchange='NSE',interval=Interval.in_5_minute,n_bars=1000)
        
    file_path = 'Book1.xlsx'
    ret = pd.read_excel(file_path)
    ret["time"] = pd.to_datetime(ret["time"], dayfirst=True)
    for col in ohlc:
        ret[col] = ret[col].astype(float)
    
    # token = files_interact.get_token("NSE", "Nifty 50")
    # lastBusDay = datetime.datetime.now()-datetime.timedelta(days=30)
    # lastBusDay = lastBusDay.replace(hour=0, minute=0, second=0, microsecond=0)
    # # last_day = datetime.datetime.now()-datetime.timedelta(days=27)
    # # last_day = last_day.replace(hour=0, minute=0, second=0, microsecond=0)
    # ret = client.get_time_price_series(exchange="NSE", token = str(int(token)), starttime=int(lastBusDay.timestamp()), interval="5")
    # ret = pd.DataFrame.from_dict(ret)
    # ret["time"] = pd.to_datetime(ret["time"], dayfirst=True)
    # ret.sort_values(by='time', ascending=True, inplace=True)
    # ret.reset_index(inplace=True)
    # for col in ohlc:
    #     ret[col] = ret[col].astype(float)
    
    temp = pd.DataFrame()
    temp = ret.iloc[:80].copy()
    data_columns = ['time', 'entry_time', 'entry_price', 'exit_time', 'exit_price', 'profit', 'reason']
    trade_data = pd.DataFrame(columns=data_columns)
    ret = ret[80:]
    order_placed = False
    order_signal = False
    confirmation_waiting = False
    order_counter = 0
    bull_or_bear = None  
    stoploss = 0 
    reason = "nothing"
    
    for i in range(0, len(ret)): 
        if (order_placed == True and order_signal == False and confirmation_waiting == False):
            exit_time, exit_price, order_placed, order_exit, stoploss = check_exit(temp, bull_or_bear, stoploss) 
            if order_exit == True:
                trade_data = append_value(trade_data, 'exit_time', exit_time, order_counter)
                trade_data = append_value(trade_data, 'exit_price', exit_price, order_counter)
                if bull_or_bear == "up":
                    profit  = exit_price - entry_price
                else:
                    profit  = entry_price - exit_price
                trade_data = append_value(trade_data, 'profit', profit, order_counter)
                order_counter = order_counter + 1
        elif (order_placed == False and order_signal == False and confirmation_waiting == True):
            order_signal, confirmation_waiting, stoploss = confirmation(temp, bull_or_bear)
            if order_signal == True:
                reason = "came in waiting, placing order"
            else:
                reason = "came in wating, got caneled"
            trade_data = append_value(trade_data, 'time', temp["time"].iloc[-1], order_counter)
            trade_data = append_value(trade_data, 'reason', reason, order_counter)
            order_counter = order_counter + 1
        elif (order_placed == False and order_signal == True and confirmation_waiting == False):
            entry_time , entry_price, order_signal, order_placed, stoploss = place_order(temp, bull_or_bear, stoploss)
            trade_data = append_value(trade_data, 'entry_time', entry_time, order_counter)
            trade_data = append_value(trade_data, 'entry_price', entry_price, order_counter)
        elif (order_placed == False and order_signal == False and confirmation_waiting ==  False):
            order_signal, confirmation_waiting, bull_or_bear, stoploss, reason = check_trade(temp)
            trade_data = append_value(trade_data, 'time', temp["time"].iloc[-1], order_counter)
            trade_data = append_value(trade_data, 'reason', reason, order_counter)
            order_counter = order_counter + 1
        
        
        if (i%50 == 0):
            print("working fine")
            print(temp["time"].iloc[-1])
        next_row = ret.iloc[[i]]
        temp = pd.concat([temp, next_row], ignore_index=True) 
    
    current_directory = os.getcwd()
    df_comb_file = os.path.join(current_directory, 'testing4.csv')
    trade_data.to_csv(df_comb_file, index=True)
    
    
if __name__ == "__main__":
    main()
    