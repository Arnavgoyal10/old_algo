import pandas as pd
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi
import threading
import refracted_advance as refracted

ohlc = ['into', 'inth', 'intl', 'intc']
lock = threading.Lock()

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

def main(symbol, count):
    
    folder1 = ""
    folder = ""
    if count == 0:
        folder = "Jan"
        folder1 = "Feb"
    elif count == 1:
        folder = "Feb"
        folder1 = "Mar"
    elif count == 2:
        folder = "Mar"
        folder1 = "Apr"
    elif count == 3:
        folder = "Apr"
        folder1 = "May"
    elif count == 4:
        folder = "May"
        folder1 = "Jun"
    elif count == 5:
        folder = "Jun"
        folder1 = "Jul"
        
    ret = pd.read_csv(f'min5/{folder}/{symbol}_params.csv')
    ret1 = pd.read_csv(f'monthly_5min/{folder1}/{symbol}.csv')
    
    
    
    for i in range(len(ret)):
        trade_columns = ['entry_time', 'entry_price', 'exit_time', 'exit_price', 'profit', 'agg_profit']
        trade_data = pd.DataFrame(columns=trade_columns)
        
        list1 = ret.iloc[i].to_list()
        configs = list1[:2]
        params = list1[2:-1]
        net = 0
        ret1["time"] = pd.to_datetime(ret1["time"], format="%Y-%m-%d %H:%M:%S", dayfirst=False)
        for col in ohlc:
            ret1[col] = ret1[col].astype(float)
        
        df = calculate_indicators(ret1, params)
        temp = df.head(5).copy()
        df = df.iloc[5:].reset_index(drop=True)
        
        for j in range(0, len(ret1)):
            
            with lock:
                trade_data = refracted.final(temp, trade_data, configs)
            
            if len(trade_data) > 3 and (trade_data['profit'].tail(3) < 0).all():
                if trade_data['profit'].tail(3).sum() < -85:
                    net = -50000
                    break  # Arbitrarily large loss to prevent further evaluation
                
            if len(trade_data) > 0 and pd.notna(trade_data['profit'].iloc[-1]) and trade_data['profit'].iloc[-1] is not None and trade_data['profit'].iloc[-1] < -85:
                net = -50000
                break
                # Arbitrarily large loss to prevent further evaluation
                
            next_row = ret1.iloc[[j]]
            temp = pd.concat([temp, next_row], ignore_index=True)
            temp = temp.tail(5)
    
        less_than_zero = (trade_data['agg_profit'] < 0).sum()
        greater_than_zero = (trade_data['agg_profit'] > 0).sum()
        
        if less_than_zero != 0:
            less_than_zero = 1
            
        if (greater_than_zero/less_than_zero) < 3.2:
                net = -50000
        
        if net == 0:
            net = trade_data['agg_profit'].sum()
        
        ret.at[i, 'net_profit1'] = net
            
    ret.to_csv(f'min5/{folder1}/{symbol}_trial.csv', index=False)
                                                                                                                 
if __name__ == "__main__":
    main()