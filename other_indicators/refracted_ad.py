import pandas as pd

def append_value(dataframe, column_name, value, index):
    if index >= len(dataframe):
        new_row = pd.DataFrame([{col: (value if col == column_name else None) for col in dataframe.columns}])
        dataframe = pd.concat([dataframe, new_row], ignore_index=True)
    else:
        dataframe.at[index, column_name] = value
    return dataframe

ohlc=['into', 'inth', 'intl', 'intc']

current_state = 0
# 0 == order not placed, 1 == order placed

signal = 0
# 0 == no signal, 1 == order_signal, 3 == exit_signal

market_direction = 0
# 1 == up, -1 == down, 0 == no direction

stoploss = 0
order_count = 0
buying_price = 0
exit_price = 0
exit_time = 0
order_flag_count = 0
entry_time = 0
entry_price = 0

''''''''''''

stoploss_config = 10
squee_config  = 2


''''''''''''
def pivot(df):
    # Iterate over the rows from the bottom to the top
    for index in range(len(df)-1, -1, -1):
        current_time = df["time"].iloc[index]
        comparison_time = current_time.replace(hour=9, minute=15, second=0, microsecond=0)
        
        if current_time == comparison_time:
            # Calculate pivot and support/resistance levels
            p = (df['inth'].iloc[index] + df['intl'].iloc[index] + df['intc'].iloc[index]) / 3
            s1 = p - 0.382 * (df['inth'].iloc[index] - df['intl'].iloc[index])
            s2 = p - 0.618 * (df['inth'].iloc[index] - df['intl'].iloc[index])
            s3 = p - 1 * (df['inth'].iloc[index] - df['intl'].iloc[index])
            s4 = p + 0.382 * (df['inth'].iloc[index] - df['intl'].iloc[index])
            s5 = p + 0.618 * (df['inth'].iloc[index] - df['intl'].iloc[index])
            s6 = p + 1 * (df['inth'].iloc[index] - df['intl'].iloc[index])
            level = [s1, s2, s3, s4, s5, s6]
            return level
        
def set_stoploss(df, market_direction, stoploss):
    temp = 0.0
    levels = pivot(df)
    if market_direction == 1:
        temp = (max([level for level in levels if level < df["intc"].iloc[-1]], default=stoploss))-8
        if (temp > stoploss or stoploss == 0):
            stoploss = temp
    else:
        temp = (min([level for level in levels if level > df["intc"].iloc[-1]], default=stoploss))+8
        if (temp < stoploss or stoploss == 0):
            stoploss = temp
    # print("Stoploss: ", stoploss)
    # print(df['time'].iloc[-1])
    return stoploss

def check_exit(df, market_direction, stoploss):
    exit_price = 0
    exit_time = df["time"].iloc[-1]
    inth_last = df["inth"].iloc[-1]
    intl_last = df["intl"].iloc[-1]
        
    if inth_last >= stoploss and intl_last <= stoploss:
        exit_price = stoploss
        return 3, exit_price, exit_time, stoploss

    stoploss = set_stoploss(df, market_direction, stoploss)
    return 0, exit_price, exit_time, stoploss

def check_trade(df):
    buying_price = 0
    waiting = 0
    market_direction = 0
    stoploss = 0 
    
    current_time = df["time"].iloc[-1]
    comparison_time = current_time.replace(hour=14, minute=59, second=0, microsecond=0)
    
    if current_time > comparison_time:
        return 0, 0 , 0, 0
        
    smooth = df["smooth_velocity"].iloc[-1]
    smooth2 = df["smooth_velocity"].iloc[-2]
    
    if not ((smooth > 0  and smooth2 < 0) or (smooth < 0  and smooth2 > 0)):
        return 0, 0 , 0, 0

    psi1 = df["psi"].iloc[-1]
    psi2 = df["psi"].iloc[-2]
    
    if not (psi1 < 80 and psi2 < 80 and (psi1 - squee_config) < psi2):
        return 0, 0 , 0, 0
    
    if smooth < 0:
        market_direction = -1
    else:
        market_direction = 1
    
    if df["ImpulseMACD"].iloc[-1] == 0:
        return 0, 0 , 0, 0
        
    impulse_temp1 = df["ImpulseMACD"].iloc[-1] - df["ImpulseMACDCDSignal"].iloc[-1]
    impulse_temp2 = df["ImpulseMACD"].iloc[-2] - df["ImpulseMACDCDSignal"].iloc[-2]

    if market_direction != 1:
        impulse_temp1 = -impulse_temp1
        impulse_temp2 = -impulse_temp2

    
    if (impulse_temp2 < 0 and impulse_temp1 > 0):
        waiting = 1
    elif not (impulse_temp1 > impulse_temp2):
        return 0, 0 , 0, 0
    
    tsi_temp1 = df["TSI"].iloc[-1] - df["TSIs"].iloc[-1]
    tsi_temp2 = df["TSI"].iloc[-2] - df["TSIs"].iloc[-2]

    if market_direction != 1:
        tsi_temp1 = -tsi_temp1
        tsi_temp2 = -tsi_temp2

    if (tsi_temp2 < 0 and tsi_temp1 > 0):
        waiting = 1
    elif not (tsi_temp1 > tsi_temp2):
        return 0, 0 , 0, 0
    
    # comparison_time = current_time.replace(hour=9, minute=20, second=0, microsecond=0)
    # if current_time < comparison_time:
    #     waiting = 1
    
    if waiting == 1:
        return 0, market_direction, 0, 0
    else:
        stoploss = set_stoploss(df, market_direction, stoploss)
        
        if market_direction == 1:
            buying_price = df["inth"].iloc[-1]
        else:
            buying_price = df["intl"].iloc[-1]
        return 1, market_direction, buying_price, stoploss
    
def final(temp, trade_data, hyper_parameters):
    global stoploss_config, squee_config
    
    global current_state, signal, market_direction, stoploss, order_count, buying_price, exit_time
    global exit_price, order_flag_count, entry_time, entry_price
    
    (stoploss_config, squee_config) = hyper_parameters

    agg_profit = 0
    if current_state == 1:
        signal, exit_price, exit_time, stoploss = check_exit(temp, market_direction, stoploss)
        if signal == 3:
            if market_direction == 1:
                profit  = exit_price - entry_price
            else:
                profit  = entry_price - exit_price
            # print("Order exited at: ", exit_time ,"at price: ", exit_price, "with profit: ", profit)
            trade_data = append_value(trade_data, 'profit', profit, order_count)
            trade_data = append_value(trade_data, 'exit_time', exit_time, order_count)
            trade_data = append_value(trade_data, 'exit_price', exit_price, order_count)
            if profit > 120:
                agg_profit = 100
            elif profit < 10 and profit > 0:
                agg_profit = 0
            else:
                agg_profit = profit
            trade_data = append_value(trade_data, 'agg_profit', agg_profit, order_count)
            order_count = order_count+1
            current_state = 0
            market_direction = 0
            signal = 0
    
    elif current_state == 0 and signal == 1:
        if order_flag_count < 2:
            if (temp["inth"].iloc[-1] >= buying_price and temp["intl"].iloc[-1] <= buying_price):
                current_state = 1
                entry_time = temp["time"].iloc[-1]
                entry_price = buying_price
                stoploss = set_stoploss(temp, market_direction, stoploss)
                # print("Order placed at: ", entry_time ,"at price: ", entry_price, "with stoploss: ", stoploss)
                trade_data = append_value(trade_data, 'entry_time', entry_time, order_count)
                trade_data = append_value(trade_data, 'entry_price', entry_price, order_count)
                order_flag_count = 0
                
            else:
                order_flag_count = order_flag_count +1
        else:
            order_flag_count = 0
            market_direction = 0
            signal = 0

    new_signal, new_market_direction, new_buying_price, new_stoploss = check_trade(temp)
    # new_signal = 0, new_market_direction = 0, new_buying_price = 0, new_stoploss = 0
    # new_signal = 1, new_market_direction = market_direction, new_buying_price = buying_price, new_stoploss = stoploss

    if (market_direction == 0 or (market_direction == 1 and new_market_direction == -1) or (market_direction == -1 and new_market_direction == 1)):
        if current_state == 1:
            exit_price = temp["intc"].iloc[-1]
            if market_direction == 1:
                profit  = exit_price - entry_price
            else:
                profit  = entry_price - exit_price
            trade_data = append_value(trade_data, 'profit', profit, order_count)
            trade_data = append_value(trade_data, 'exit_time', temp["time"].iloc[-1], order_count)
            trade_data = append_value(trade_data, 'exit_price', exit_price, order_count)
            if profit > 120:
                agg_profit = 100
            elif profit < 10 and profit > 0:
                agg_profit = 0
            else:
                agg_profit = profit
            trade_data = append_value(trade_data, 'agg_profit', agg_profit, order_count)
            order_count = order_count+1
            order_flag_count = 0
            current_state = 0
        signal, market_direction, buying_price, stoploss = new_signal, new_market_direction, new_buying_price, new_stoploss
        order_flag_count = 0
    return trade_data