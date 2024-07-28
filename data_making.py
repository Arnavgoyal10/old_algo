import os
import current_indicators.velocity_indicator as velocity_indicator
import current_indicators.squeeze as squeeze
import current_indicators.impulsemacd as impulsemacd
import current_indicators.tsi as tsi
import threading
import pandas as pd
import refracted_advance as refracted
import warnings
warnings.simplefilter("ignore")

ohlc=['into', 'inth', 'intl', 'intc']

lock = threading.Lock()

def calculate_indicators(df, hyperparamas):
    
    (lookback_config, ema_length_config, conv_config, 
    length_config, lengthMA_config, lengthSignal_config, fast_config, slow_config, 
    signal_config) = hyperparamas
    
    df = df.copy()
    
    df = velocity_indicator.calculate_float(df, lookback=lookback_config, ema_length=ema_length_config)
    df = squeeze.squeeze_index2_float(df,conv=conv_config, length=length_config)
    
    df_macd = impulsemacd.macd(df, lengthMA = lengthMA_config, lengthSignal = lengthSignal_config)
    df[['ImpulseMACD', 'ImpulseMACDCDSignal']] = df_macd[['ImpulseMACD', 'ImpulseMACDCDSignal']]
    
    df_tsi = tsi.tsi(df, fast = fast_config, slow = slow_config, signal = signal_config)
    df[['TSI', 'TSIs']] = df_tsi[['TSI', 'TSIs']]
    
    return df


ret = pd.read_csv('Nifty Bank_after.csv')
ret1 = pd.read_csv('data_5min/Nifty Bank.csv')

os.makedirs("data", exist_ok=True)


def main():
    ret1["time"] = pd.to_datetime(ret1["time"], format="%Y-%m-%d %H:%M:%S", dayfirst=False)
    for col in ohlc:
        ret1[col] = ret1[col].astype(float)
    
    for i in range(len(ret)):
        trade_columns = ['entry_time', 'entry_price', 'exit_time', 'exit_price', 'profit', 'agg_profit']
        trade_data = pd.DataFrame(columns=trade_columns)
        states = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        list1 = ret.iloc[i].to_list()
        configs = list1[:2]
        params = list1[2:-2]
        
        df = calculate_indicators(ret1.copy(), params).copy()
        temp = df.head(5)
        df = df.iloc[5:].reset_index(drop=True)
        
        for j in range(len(df)):
            trade_data, states = refracted.final(temp, trade_data, configs, states)
            
            next_row = df.iloc[[j]]
            temp = pd.concat([temp, next_row], ignore_index=True)
            temp = temp.tail(5)
            
            trade_data.to_csv(f"data/trade_data_{i}.csv", index=False)
            
        
if __name__ == "__main__":
    main()